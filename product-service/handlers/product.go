package handlers

import (
	"context"
	"log"
	"product-service/models"
	"product-service/repo"
	"time"

	"github.com/go-playground/validator/v10"
	"github.com/google/uuid"
	"github.com/labstack/echo/v4"
	hu "plotva.ru/common/handlers_utils"
)

// POST /api/product/add
//
// Response json:
//
//   - status_code == 200: JSON string with uuid
//   - statuc_code != 200: hu.BasicResponse
//
// Request json: models.ProductCreate
//
// Middlewares:
//
//   - Expect json
func PostAddProduct(repo repo.ProductRepo, c echo.Context) error {
	ctx, cancel := context.WithTimeout(context.Background(), ENDPOINT_TIMEOUT)
	defer cancel()

	var product models.ProductCreate
	c.Bind(&product)

	val := validator.New()
	err := val.Struct(product)
	if err != nil {
		return c.JSON(400, hu.Error(err))
	}

	log.Println(product)

	id, err := repo.Add(ctx, product)
	if err != nil {
		return c.JSON(500, hu.Error(err))
	}

	return c.JSON(200, id.String())
}

// GET /api/product/:id
//
// Response json:
//
//   - status_code == 200: models.Product
//   - statuc_code != 200: hu.BasicResponse
func GetProductById(repo repo.ProductRepo, c echo.Context) error {
	ctx, cancel := context.WithTimeout(context.Background(), ENDPOINT_TIMEOUT)
	defer cancel()

	idStr := c.Param("id")
	uuid, err := uuid.Parse(idStr)
	if err != nil {
		return c.JSON(400, hu.Error(err))
	}

	prod, err := repo.GetById(ctx, uuid)
	if err != nil {
		return c.JSON(404, hu.Error(err))
	}

	return c.JSON(200, prod)
}

// DELETE /api/product/delete/:id
//
// Response json: hu.BasicResponse
func DeleteProductById(repo repo.ProductRepo, c echo.Context) error {
	ctx, cancel := context.WithTimeout(context.Background(), ENDPOINT_TIMEOUT)
	defer cancel()

	idStr := c.Param("id")
	uuid, err := uuid.Parse(idStr)
	if err != nil {
		return c.JSON(400, hu.Error(err))
	}

	err = repo.DeleteById(ctx, uuid)
	if err != nil {
		return c.JSON(500, hu.Error(err))
	}
	return c.JSON(200, hu.Ok())
}

// POST /api/product/filter
//
// Response json:
// - status == 200: []models.Product
// - statis != 200: hu.BasicResponse
//
// Request json: models.ProductFilter
//
// Middlewares:
// - Expect json
func PostGetProductsByFilter(repo repo.ProductRepo, c echo.Context) error {
	ctx, cancel := context.WithTimeout(context.Background(), ENDPOINT_TIMEOUT)
	defer cancel()

	var filter models.ProductFilter
	c.Bind(&filter)

	result, err := repo.GetByFilter(ctx, filter)
	time.Sleep(100 * time.Millisecond)
	if err != nil {
		return c.JSON(500, hu.Error(err))
	}
	return c.JSON(200, result)
}
