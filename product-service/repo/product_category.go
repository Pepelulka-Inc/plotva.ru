package repo

import (
	"context"
	"product-service/models"

	"github.com/jackc/pgx/v5"
	"plotva.ru/common/db"
)

type ProductCategoryRepo interface {
	GetAll(context.Context) ([]models.ProductCategory, error)
	Add(context.Context, models.ProductCategory) error
	DeleteByName(context.Context, string) error
}

type ProductCategoryRepoPg struct {
	Pool db.SqlConnectionPool
}

func (repo ProductCategoryRepoPg) GetAll(ctx context.Context) ([]models.ProductCategory, error) {
	queryString := `
SELECT category_name FROM plotva.product_categories ORDER BY category_name;
	`
	conn, err := repo.Pool.Acquire(ctx)
	if err != nil {
		return nil, err
	}
	defer conn.Release()

	rows, err := conn.Query(ctx, queryString)
	if err != nil {
		return nil, err
	}

	return pgx.CollectRows(rows, func(row pgx.CollectableRow) (models.ProductCategory, error) {
		var cat models.ProductCategory
		err := row.Scan(&cat.CategoryName)
		return cat, err
	})
}

func (repo ProductCategoryRepoPg) Add(ctx context.Context, cat models.ProductCategory) error {
	queryString := `
INSERT INTO plotva.product_categories (category_name) VALUES ($1);
	`
	if err := cat.Validate(); err != nil {
		return err
	}

	conn, err := repo.Pool.Acquire(ctx)
	if err != nil {
		return err
	}
	defer conn.Release()

	_, err = conn.Exec(ctx, queryString, cat.CategoryName)
	return err
}

func (repo ProductCategoryRepoPg) DeleteByName(ctx context.Context, name string) error {
	queryString := `
DELETE FROM plotva.product_categories WHERE category_name = $1;
	`
	conn, err := repo.Pool.Acquire(ctx)
	if err != nil {
		return err
	}
	defer conn.Release()

	_, err = conn.Exec(ctx, queryString, name)
	return err
}
