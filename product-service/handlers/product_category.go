package handlers

import (
	"context"
	"product-service/models"
	"product-service/repo"
	"time"

	hu "plotva.ru/common/handlers_utils"

	"github.com/labstack/echo/v4"
)

func Test(c echo.Context) error {
	time.Sleep(3 * time.Second)
	return c.String(200, "Hello world!")
}

// GET: /api/product/category/all
func GetAllProductCategories(catRepo repo.ProductCategoryRepo, c echo.Context) error {
	ctx, cancel := context.WithTimeout(context.Background(), EndpointTimeout)
	defer cancel()

	cats, err := catRepo.GetAll(ctx)
	if err != nil {
		return c.JSON(500, hu.Error(err))
	}

	return c.JSON(200, cats)
}

// POST: /api/product/category/add
func PostAddProductCategory(catRepo repo.ProductCategoryRepo, c echo.Context) error {
	ctx, cancel := context.WithTimeout(context.Background(), EndpointTimeout)
	defer cancel()

	var cat models.ProductCategory
	err := c.Bind(&cat)
	if err != nil {
		return c.JSON(400, hu.Error(err))
	}

	err = catRepo.Add(ctx, cat)
	if err != nil {
		return c.JSON(500, hu.Error(err))
	}

	return c.JSON(200, hu.Ok())
}

// DELETE: /api/product/category/delete/:name
func DeleteProductCategory(catRepo repo.ProductCategoryRepo, c echo.Context) error {
	ctx, cancel := context.WithTimeout(context.Background(), EndpointTimeout)
	defer cancel()

	name := c.Param("name")

	err := catRepo.DeleteByName(ctx, name)
	if err != nil {
		return c.JSON(500, hu.Error(err))
	}

	return c.JSON(200, hu.Ok())
}
