package main

import (
	"context"
	"errors"
	"flag"
	"log"
	"log/slog"
	"net/http"
	"os"
	"product-service/handlers"
	"product-service/internal"
	"product-service/repo"

	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/labstack/echo/v4"
	"plotva.ru/common/cfg"
	"plotva.ru/common/db"
	"plotva.ru/common/kafka"
)

func failOnError(err error) {
	if err != nil {
		log.Panic(err)
	}
}

// TODO: Валидация для /api/product/category/add
func setupProductCategoriesHandlers(e *echo.Echo, pool *pgxpool.Pool) {
	catRepo := repo.ProductCategoryRepoPg{Pool: pool}

	e.GET(
		"/api/product/category/all",
		func(c echo.Context) error {
			return handlers.GetAllProductCategories(catRepo, c)
		},
	)

	e.POST(
		"/api/product/category/add",
		func(c echo.Context) error {
			return handlers.PostAddProductCategory(catRepo, c)
		},
		internal.ExpectJSONMiddleware,
	)

	e.DELETE(
		"/api/product/category/delete/:name",
		func(c echo.Context) error {
			return handlers.DeleteProductCategory(catRepo, c)
		},
	)
}

func setupProductHandlers(e *echo.Echo, pool *pgxpool.Pool, producer *kafka.KafkaProducer) {
	productRepo := repo.ProductRepoPg{Pool: pool}

	e.POST(
		"/api/product/add",
		func(c echo.Context) error {
			return handlers.PostAddProduct(productRepo, c)
		},
		internal.ExpectJSONMiddleware,
	)

	e.POST(
		"/api/product/filter",
		func(c echo.Context) error {
			return handlers.PostGetProductsByFilter(productRepo, c)
		},
		internal.ExpectJSONMiddleware,
	)

	e.GET(
		"/api/product/:id",
		func(c echo.Context) error {
			return handlers.GetProductById(productRepo, c)
		},
	)

	e.GET(
		"/api/product/view/:user_id/:id",
		func(c echo.Context) error {
			return handlers.GetViewProduct(productRepo, producer, c)
		},
	)

	e.DELETE(
		"/api/product/delete/:id",
		func(c echo.Context) error {
			return handlers.DeleteProductById(productRepo, c)
		},
	)
}

func setupHandlers(e *echo.Echo, pool *pgxpool.Pool, producer *kafka.KafkaProducer) {
	setupProductCategoriesHandlers(e, pool)
	setupProductHandlers(e, pool, producer)
}

func main() {
	flag.Parse()

	if len(flag.Args()) < 1 {
		log.Fatalf("Usage: %s <path-to-config>", os.Args[0])
	}
	configPath := flag.Args()[0]
	// Read overall config
	config, err := cfg.ParseProjectConfig(configPath)
	failOnError(err)
	dbConfig, err := cfg.InterpretAsStructure[db.PostgresConfig](config["db"])
	failOnError(err)
	serviceConfig, err := cfg.InterpretAsStructure[internal.ProductServiceConfig](config["product-service"])
	failOnError(err)
	kafkaConfig, err := cfg.InterpretAsStructure[kafka.KafkaConfig](config["kafka"])
	failOnError(err)
	port := serviceConfig.Port

	// Create db connection pool
	pool, err := db.CreatePool(
		context.TODO(),
		dbConfig,
		serviceConfig.DbMinConns,
		serviceConfig.DbMaxConns,
	)
	failOnError(err)
	defer pool.Close()

	// Kafka producer
	kafkaProducer, err := kafka.NewProducer(kafkaConfig)
	failOnError(err)
	defer kafkaProducer.Close()

	// Set up handlers
	e := echo.New()

	setupHandlers(e, pool, kafkaProducer)

	if err := e.Start(":" + port); err != nil && !errors.Is(err, http.ErrServerClosed) {
		slog.Error("failed to start server", "error", err)
	}
}
