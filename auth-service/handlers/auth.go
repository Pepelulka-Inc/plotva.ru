package handlers

import (
	"auth-service/models"
	"auth-service/repo"
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"net/http"
	"time"

	"golang.org/x/oauth2"
	"plotva.ru/common/auth"
	hu "plotva.ru/common/handlers_utils"

	"github.com/google/uuid"
	"github.com/labstack/echo/v4"
	"github.com/labstack/gommon/log"
)

const (
	oauthStateString   = "meow"
	oauthYandexInfoUrl = "https://login.yandex.ru/info?format=json"
)

// POST /api/user/create
//
// Response json:
//
//   - status_code == 200: models.UserCreateResponse
//   - statuc_code != 200: hu.BasicResponse
//
// Request json: models.UserCreate
//
// Middlewares:
//
//   - Expect json
func PostCreateUser(userRepo repo.UsersRepo, c echo.Context) error {
	ctx, cancel := context.WithTimeout(context.Background(), EndpointTimeout)
	defer cancel()

	var userCreate models.UserCreate
	err := c.Bind(&userCreate)
	if err != nil {
		return c.JSON(400, hu.Error(err))
	}

	resp, err := userRepo.CreateUser(ctx, userCreate)
	if errors.Is(err, repo.ErrBadPassword) {
		return c.JSON(400, hu.ErrorStr("bad password"))
	} else if errors.Is(err, repo.ErrPhoneNumberAlreadyExists) {
		return c.JSON(400, hu.ErrorStr("phone number already exists"))
	} else if err != nil {
		log.Warnf("can't create new user: %v", err)
		return c.JSON(500, err)
	}

	return c.JSON(200, resp)
}

// GET /api/user/login/oauth
func GetLoginOAuthYandex(oauthCfg *oauth2.Config, c echo.Context) error {
	url := oauthCfg.AuthCodeURL(oauthStateString)
	return c.Redirect(http.StatusTemporaryRedirect, url)
}

// Get /api/user/login/callback
func GetLoginOAuthYandexCallback(jwtCfg *auth.JwtConfig, oauthCfg *oauth2.Config, userRepo repo.UsersRepo, c echo.Context) error {
	ctx, cancel := context.WithTimeout(context.Background(), EndpointTimeout)
	defer cancel()

	state := c.QueryParam("state")
	if state != oauthStateString {
		return c.JSON(400, hu.ErrorStr("invalid state"))
	}

	code := c.QueryParam("code")
	token, err := oauthCfg.Exchange(context.Background(), code)
	if err != nil {
		log.Warnf("code exchange failed: %v", err)
		return c.JSON(400, hu.ErrorStr("code exchange failed"))
	}

	client := oauthCfg.Client(ctx, token)
	resp, err := client.Get(oauthYandexInfoUrl)
	if err != nil {
		log.Warnf("user info get failed: %v", err)
		return c.JSON(400, hu.ErrorStr("user info get failed"))
	}
	defer resp.Body.Close()

	var userInfo map[string]any
	err = json.NewDecoder(resp.Body).Decode(&userInfo)
	if err != nil {
		log.Warnf("user info get failed, can't parse json : %v", err)
		return c.JSON(400, hu.ErrorStr("user info get failed"))
	}

	phoneNumber, ok := userInfo["default_phone"].(map[string]any)["number"].(string)
	if !ok {
		log.Warnf("can't extract phone number from user info json")
		return c.JSON(400, hu.ErrorStr("can't extract phone number from user info json"))
	}
	exists, id, err := userRepo.GetIdByPhoneNumber(ctx, phoneNumber)
	if err != nil {
		log.Warnf("can't get id by phone number: %v", err)
		return c.JSON(500, hu.ErrorStr("strange shit with db"))
	}
	if !exists {
		return c.JSON(401, hu.ErrorStr("no user with such phone number"))
	}

	jwtToken := auth.AuthJwtToken{
		Role:        auth.RoleUser,
		PhoneNumber: &phoneNumber,
		UserID:      &id,
		SellerID:    nil,
		Expires:     time.Now().Add(auth.JwtExpireTime),
	}

	tokenString, err := auth.CreateJwt(jwtToken, jwtCfg)
	if err != nil {
		log.Warnf("can't create jwt token: %v", err)
		return c.JSON(500, hu.ErrorStr("strange shit with jwt token"))
	}

	c.SetCookie(&http.Cookie{
		Name:     "token",
		Value:    tokenString,
		HttpOnly: true,
		Path:     "/",
	})

	return c.JSON(200, userInfo)
}

// POST /api/user/login/uuid
//
// Response json: hu.BasicResponse
//
// Request json: models.UserLoginUUID
//
// # Sets the token in cookie if success
//
// Middlewares:
//
//   - Expect json
func PostLogin(jwtCfg *auth.JwtConfig, userRepo repo.UsersRepo, c echo.Context) error {
	ctx, cancel := context.WithTimeout(context.Background(), EndpointTimeout)
	defer cancel()

	var userLogin models.UserLoginUUID
	err := c.Bind(&userLogin)
	if err != nil {
		return c.JSON(400, hu.Error(err))
	}

	exists, pswd, err := userRepo.GetPasswordHashById(ctx, uuid.UUID(userLogin.UserID))
	if err != nil {
		log.Warnf("Can't get user password by id: %v", err)
		return c.JSON(500, hu.Error(err))
	}
	if !exists {
		return c.JSON(404, hu.ErrorStr(fmt.Sprintf("User with id %v not found", userLogin.UserID)))
	}

	success, err := auth.CheckPasswords(pswd, userLogin.Password)
	if err != nil {
		log.Warnf("error checking passwords: %v", err)
		return c.JSON(500, hu.Error(err))
	}
	if !success {
		return c.JSON(401, hu.ErrorStr("wrong credentials"))
	}

	exists, phoneNumber, err := userRepo.GetPhoneNumberById(ctx, uuid.UUID(userLogin.UserID))

	if err != nil {
		return c.JSON(500, err)
	}
	if !exists {
		return c.JSON(404, hu.ErrorStr("user was deleted while processing request"))
	}

	userId := uuid.UUID(userLogin.UserID)

	tokenData := auth.AuthJwtToken{
		Role:        "user",
		PhoneNumber: &phoneNumber,
		UserID:      &userId,
		SellerID:    nil,
		Expires:     time.Now().Add(auth.JwtExpireTime),
	}

	jwtToken, err := auth.CreateJwt(tokenData, jwtCfg)
	if err != nil {
		return c.JSON(500, err)
	}

	c.SetCookie(&http.Cookie{
		Name:     "token",
		Value:    jwtToken,
		HttpOnly: true,
		Path:     "/",
	})

	return c.JSON(200, hu.Ok())
}

// POST /api/user/login/phone
//
// Response json: hu.BasicResponse
//
// Request json: models.UserLoginPhoneNumber
//
// # Sets the token in cookie if success
//
// Middlewares:
//
//   - Expect json
func PostLoginPhoneNumber(jwtCfg *auth.JwtConfig, userRepo repo.UsersRepo, c echo.Context) error {
	ctx, cancel := context.WithTimeout(context.Background(), EndpointTimeout)
	defer cancel()

	var userLogin models.UserLoginPhoneNumber
	err := c.Bind(&userLogin)
	if err != nil {
		return c.JSON(400, hu.Error(err))
	}

	exists, id, err := userRepo.GetIdByPhoneNumber(ctx, userLogin.PhoneNumber)
	if err != nil {
		log.Warnf("Can't get user id by phone number: %v", err)
		return c.JSON(500, hu.Error(err))
	}
	if !exists {
		return c.JSON(404, hu.ErrorStr(fmt.Sprintf("User with phone number %v not found", userLogin.PhoneNumber)))
	}

	exists, pswd, err := userRepo.GetPasswordHashById(ctx, id)
	if err != nil {
		log.Warnf("Can't get user password by id: %v", err)
		return c.JSON(500, hu.Error(err))
	}
	if !exists {
		return c.JSON(404, hu.ErrorStr(fmt.Sprintf("User with id %v not found", id)))
	}

	success, err := auth.CheckPasswords(pswd, userLogin.Password)
	if err != nil {
		log.Warnf("error checking passwords: %v", err)
		return c.JSON(500, hu.Error(err))
	}
	if !success {
		return c.JSON(401, hu.ErrorStr("wrong credentials"))
	}

	tokenData := auth.AuthJwtToken{
		Role:        "user",
		PhoneNumber: &userLogin.PhoneNumber,
		UserID:      &id,
		SellerID:    nil,
		Expires:     time.Now().Add(auth.JwtExpireTime),
	}

	jwtToken, err := auth.CreateJwt(tokenData, jwtCfg)
	if err != nil {
		return c.JSON(500, err)
	}

	c.SetCookie(&http.Cookie{
		Name:     "token",
		Value:    jwtToken,
		HttpOnly: true,
		Path:     "/",
	})

	return c.JSON(200, hu.Ok())
}

// GET /api/user/test
//
// Middlewares:
//
//   - Auth
func GetTestAuth(c echo.Context) error {
	if !hu.IsAuthorized(c) {
		return c.HTML(200, "Not authorized")
	}
	data, _ := hu.ExtractAuthorizedData(c)
	return c.JSON(200, data)
}
