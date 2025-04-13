package hu

import (
	"errors"
	"net/http"
	"time"

	"plotva.ru/common/auth"

	"github.com/labstack/echo/v4"
	"github.com/labstack/gommon/log"
)

const (
	CookieToken = "token"
)

const (
	ContextVarAuthorized = "authorized"
	ContextVarUserInfo   = "user_info"
)

var (
	ErrNotAuthorized = errors.New("not authorized")
)

func ExpectJSONMiddleware(next echo.HandlerFunc) echo.HandlerFunc {
	return func(c echo.Context) error {
		if c.Request().Header.Get("Content-Type") != "application/json" {
			return c.JSON(
				http.StatusUnsupportedMediaType,
				ErrorStr("server expects Content-Type == \"application/json\""),
			)
		}
		return next(c)
	}
}

func BuildAuthMiddleware(jwtCfg *auth.JwtConfig) func(echo.HandlerFunc) echo.HandlerFunc {
	return func(next echo.HandlerFunc) echo.HandlerFunc {

		return func(c echo.Context) error {
			cookie, err := c.Cookie("token")
			if err != nil {
				c.Set("authorized", false)
			} else {
				jwtData, err := auth.ReadJwt(cookie.Value, jwtCfg)
				if err != nil {
					log.Warnf("can't read jwt token: %v", err)
				}
				if jwtData.Expires.Before(time.Now()) {
					c.Set("authorized", false)
				} else {
					c.Set("authorized", true)
					c.Set("user_info", jwtData)
				}
			}

			return next(c)
		}

	}
}

func IsAuthorized(c echo.Context) bool {
	authorized := c.Get(ContextVarAuthorized)
	if authorized == nil {
		return false
	}
	authorizedBool, ok := authorized.(bool)
	if !ok {
		log.Error("authorized context var is not bool")
		return false
	}
	return authorizedBool
}

func ExtractAuthorizedData(c echo.Context) (auth.AuthJwtToken, error) {
	if !IsAuthorized(c) {
		return auth.AuthJwtToken{}, ErrNotAuthorized
	}
	data, ok := c.Get(ContextVarUserInfo).(auth.AuthJwtToken)
	if !ok {
		return auth.AuthJwtToken{}, errors.New("authorized context var is not bool")
	}
	return data, nil
}
