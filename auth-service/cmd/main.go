package main

import (
	"auth-service/handlers"
	"auth-service/internal"
	"auth-service/repo"
	"context"
	"errors"
	"flag"
	"log"
	"log/slog"
	"net/http"
	"os"

	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/labstack/echo/v4"
	"golang.org/x/oauth2"
	"plotva.ru/common/auth"
	"plotva.ru/common/cfg"
	"plotva.ru/common/db"
	hu "plotva.ru/common/handlers_utils"
)

func failOnError(err error) {
	if err != nil {
		log.Panic(err)
	}
}

func setupHandlers(e *echo.Echo, pool *pgxpool.Pool, oauthCfg *oauth2.Config, jwtConfig *auth.JwtConfig) {
	userRepo := repo.UsersRepoPg{
		Pool: pool,
	}

	e.POST(
		"/api/user/create",
		func(c echo.Context) error {
			return handlers.PostCreateUser(userRepo, c)
		},
		hu.ExpectJSONMiddleware,
	)

	e.POST(
		"/api/user/login/uuid",
		func(c echo.Context) error {
			return handlers.PostLogin(jwtConfig, userRepo, c)
		},
		hu.ExpectJSONMiddleware,
	)

	e.POST(
		"/api/user/login/phone",
		func(c echo.Context) error {
			return handlers.PostLoginPhoneNumber(jwtConfig, userRepo, c)
		},
		hu.ExpectJSONMiddleware,
	)

	e.GET(
		"/api/user/test",
		handlers.GetTestAuth,
		hu.BuildAuthMiddleware(jwtConfig),
	)

	// OAuth
	e.GET(
		"/api/user/login/oauth",
		func(c echo.Context) error {
			return handlers.GetLoginOAuthYandex(oauthCfg, c)
		},
	)

	e.GET(
		"/api/user/login/callback",
		func(c echo.Context) error {
			return handlers.GetLoginOAuthYandexCallback(jwtConfig, oauthCfg, userRepo, c)
		},
	)
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
	serviceConfig, err := cfg.InterpretAsStructure[internal.AuthServiceConfig](config["auth-service"])
	failOnError(err)
	dbConfig, err := cfg.InterpretAsStructure[db.PostgresConfig](config["db"])
	failOnError(err)
	jwtConfig, err := cfg.InterpretAsStructure[auth.JwtConfig](config["jwt"])
	failOnError(err)

	// db connection pool
	pool, err := db.CreatePgxPool(
		context.TODO(),
		dbConfig,
		serviceConfig.DbMinConns,
		serviceConfig.DbMaxConns,
	)
	failOnError(err)
	defer pool.Close()

	// Yandex OAuth client config
	yandexOauthConfig := &oauth2.Config{
		ClientID:     serviceConfig.OAuth.ClientID,
		ClientSecret: serviceConfig.OAuth.ClientSecret,
		RedirectURL:  serviceConfig.OAuth.RedirectURL,
		Scopes:       serviceConfig.OAuth.Scopes,
		Endpoint: oauth2.Endpoint{
			AuthURL:  serviceConfig.OAuth.AuthURLEndpoint,
			TokenURL: serviceConfig.OAuth.TokenURLEndpoint,
		},
	}

	e := echo.New()

	setupHandlers(e, pool, yandexOauthConfig, &jwtConfig)

	if err := e.Start(":" + serviceConfig.Port); err != nil && !errors.Is(err, http.ErrServerClosed) {
		slog.Error("failed to start server", "error", err)
	}
}
