package internal

import (
	"net/http"

	"github.com/labstack/echo/v4"
	hu "plotva.ru/common/handlers_utils"
)

func ExpectJSONMiddleware(next echo.HandlerFunc) echo.HandlerFunc {
	return func(c echo.Context) error {
		if c.Request().Header.Get("Content-Type") != "application/json" {
			return c.JSON(
				http.StatusUnsupportedMediaType,
				hu.ErrorStr("server expects Content-Type == \"application/json\""),
			)
		}
		return next(c)
	}
}
