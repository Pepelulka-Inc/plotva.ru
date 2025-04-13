package repo

import (
	"context"
	"product-service/models"
	"strings"

	"plotva.ru/common/db"
	jt "plotva.ru/common/json_types"
	"plotva.ru/common/utils"

	"github.com/google/uuid"
	"github.com/jackc/pgx/v5"
)

type ProductRepo interface {
	GetById(context.Context, uuid.UUID) (models.Product, error)
	DeleteById(context.Context, uuid.UUID) error
	Add(context.Context, models.ProductCreate) (uuid.UUID, error)

	GetByFilter(context.Context, models.ProductFilter) ([]models.Product, error)
}

type ProductRepoPg struct {
	Pool db.SqlConnectionPool
}

func (repo ProductRepoPg) GetById(ctx context.Context, product_id uuid.UUID) (models.Product, error) {
	queryString := `
SELECT 
	product_id, name, description, seller_id, category, photo_url, price_rub, creation_time
FROM
	plotva.products
WHERE product_id = $1;
	`

	conn, err := repo.Pool.Acquire(ctx)
	if err != nil {
		return models.Product{}, err
	}
	defer conn.Release()

	row := conn.QueryRow(ctx, queryString, product_id)
	var result models.Product
	err = row.Scan(
		&result.ProductID,
		&result.Name,
		&result.Description,
		&result.SellerID,
		&result.Category,
		&result.PhotoURL,
		&result.PriceRub,
		&result.CreationTime,
	)
	return result, err
}

func (repo ProductRepoPg) DeleteById(ctx context.Context, product_id uuid.UUID) error {
	queryString := `
DELETE FROM 
	plotva.products
WHERE product_id = $1;
	`

	conn, err := repo.Pool.Acquire(ctx)
	if err != nil {
		return err
	}
	defer conn.Release()

	_, err = conn.Exec(ctx, queryString, product_id)
	return err
}

func (repo ProductRepoPg) Add(ctx context.Context, product models.ProductCreate) (uuid.UUID, error) {
	queryString := `
INSERT INTO
	plotva.products (name, description, seller_id, category, photo_url, price_rub, creation_time)
VALUES
	($1, $2, $3, $4, $5, $6, NOW())
RETURNING product_id;
	`
	conn, err := repo.Pool.Acquire(ctx)
	if err != nil {
		return uuid.UUID{}, err
	}
	defer conn.Release()

	row := conn.QueryRow(
		ctx,
		queryString,
		product.Name,
		product.Description,
		product.SellerID,
		product.Category,
		product.PhotoURL,
		product.PriceRub,
	)
	var result uuid.UUID
	err = row.Scan(&result)
	return result, err
}

func buildQueryForFilter(filter models.ProductFilter) (string, []any) {
	// Здесь мы строим запрос для фильтра
	var builder strings.Builder
	builder.WriteString(
		`
SELECT
	product_id, name, description, seller_id, category, photo_url, price_rub, creation_time
FROM
	plotva.products
	`)

	whereBuilder := db.NewWhereStatementBuilder(0)

	if filter.MaxPrice != nil {
		whereBuilder.AddBasicConstraint(
			"price_rub",
			*filter.MaxPrice,
			"<=",
		)
	}

	if filter.MinPrice != nil {
		whereBuilder.AddBasicConstraint(
			"price_rub",
			*filter.MinPrice,
			">=",
		)
	}

	if len(filter.CategoriesList) != 0 {
		anyList := utils.Map(
			filter.CategoriesList,
			func(s string) any { return any(s) },
		)
		whereBuilder.AddSetConstraint(
			"category",
			anyList,
			false,
		)
	}

	// TODO: Сделать NameFilter умнее
	if filter.NameFilter != nil {
		whereBuilder.AddBasicConstraint(
			"name",
			*filter.NameFilter,
			"=",
		)
	}

	if len(filter.SellersIDList) != 0 {
		anyList := utils.Map(
			filter.SellersIDList,
			func(s jt.JsonUUID) any { return any(s) },
		)
		whereBuilder.AddSetConstraint(
			"seller_id",
			anyList,
			false,
		)
	}

	if filter.MaxCreationTime != nil {
		whereBuilder.AddBasicConstraint(
			"creation_time",
			*filter.MaxCreationTime,
			"<=",
		)
	}

	if filter.MinCreationTime != nil {
		whereBuilder.AddBasicConstraint(
			"creation_time",
			*filter.MinCreationTime,
			">=",
		)
	}

	whereStmt, args := whereBuilder.GetQuery()
	builder.WriteString(whereStmt)
	builder.WriteRune(';')
	return builder.String(), args
}

func (repo ProductRepoPg) GetByFilter(ctx context.Context, filter models.ProductFilter) ([]models.Product, error) {
	query, args := buildQueryForFilter(filter)

	conn, err := repo.Pool.Acquire(ctx)
	if err != nil {
		return nil, err
	}
	defer conn.Release()

	rows, err := conn.Query(ctx, query, args...)
	if err != nil {
		return nil, err
	}
	return pgx.CollectRows(rows, func(row pgx.CollectableRow) (models.Product, error) {
		var product models.Product
		err := row.Scan(
			&product.ProductID,
			&product.Name,
			&product.Description,
			&product.SellerID,
			&product.Category,
			&product.PhotoURL,
			&product.PriceRub,
			&product.CreationTime,
		)
		return product, err
	})
}
