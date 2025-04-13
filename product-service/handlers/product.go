package handlers

import (
	"context"
	"fmt"
	"log"
	"product-service/models"
	"product-service/repo"
	"time"

	"github.com/go-playground/validator/v10"
	"github.com/google/uuid"
	"github.com/labstack/echo/v4"
	hu "plotva.ru/common/handlers_utils"
	jt "plotva.ru/common/json_types"
	"plotva.ru/common/kafka"
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
	ctx, cancel := context.WithTimeout(context.Background(), EndpointTimeout)
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
	ctx, cancel := context.WithTimeout(context.Background(), EndpointTimeout)
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
	ctx, cancel := context.WithTimeout(context.Background(), EndpointTimeout)
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
	ctx, cancel := context.WithTimeout(context.Background(), EndpointTimeout)
	defer cancel()

	var filter models.ProductFilter
	c.Bind(&filter)

	result, err := repo.GetByFilter(ctx, filter)
	if err != nil {
		return c.JSON(500, hu.Error(err))
	}
	return c.JSON(200, result)
}

// GET /api/product/view/:user_id/:id
//
// Response json:
// - status == 200: models.Product
// - statis != 200: hu.BasicResponse
//
// Делает абсолютно тоже самое что GetProductById, но еще и отправляет сообщение в кафку о просмотре.
// TODO: Надо брать user_id из авторизации
func GetViewProduct(repo repo.ProductRepo, producer *kafka.KafkaProducer, c echo.Context) error {
	ctx, cancel := context.WithTimeout(context.Background(), EndpointTimeout)
	defer cancel()

	userIdStr := c.Param("user_id")
	userId, err := uuid.Parse(userIdStr)
	if err != nil {
		return c.JSON(400, hu.Error(
			fmt.Errorf(
				"error while parsing user_id: %s",
				err.Error(),
			),
		))
	}

	productIdStr := c.Param("id")
	productId, err := uuid.Parse(productIdStr)
	if err != nil {
		return c.JSON(400, fmt.Errorf(
			"error while parsing product_id: %s",
			err.Error(),
		))
	}

	// Если не получилось отправить сообщение, сообщим об этом, но все равно ответим на запрос
	err = producer.SendJSON(kafka.KafkaProductViewsTopicName, models.ProductViewMessage{
		UserId:    jt.JsonUUID(userId),
		ProductId: jt.JsonUUID(productId),
		Timestamp: time.Now(),
	})
	if err != nil {
		log.Printf("can't send messages to kafka: %s", err)
	}

	result, err := repo.GetById(ctx, productId)

	if err != nil {
		return c.JSON(500, hu.Error(err))
	}
	return c.JSON(200, result)
}
