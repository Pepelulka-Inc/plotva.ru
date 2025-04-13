package auth

import (
	"errors"
	"fmt"
	"time"

	"github.com/golang-jwt/jwt"
	"github.com/google/uuid"
)

type AuthJwtToken struct {
	Role        string     `json:"role"`
	PhoneNumber *string    `json:"phone_number,omitempty"`
	UserID      *uuid.UUID `json:"user_id,omitempty"`
	SellerID    *uuid.UUID `json:"seller_id,omitempty"`
	Expires     time.Time  `json:"expires"`
}

const (
	RoleUser   = "user"
	RoleSeller = "seller"
	RoleAdmin  = "admin"
)

const JwtExpireTime = time.Hour * 24 * 3

type JwtConfig struct {
	Secret string `json:"secret"`
}

func ptrToString[T any](val *T) string {
	if val == nil {
		return "nil"
	}
	return fmt.Sprintf("%v", *val)
}

func (token *AuthJwtToken) String() string {
	return fmt.Sprintf(
		"Token{role=%s phone_number=%s, user_id=%s, seller_id=%s, expires=%v}",
		token.Role,
		ptrToString(token.PhoneNumber),
		ptrToString(token.UserID),
		ptrToString(token.SellerID),
		token.Expires,
	)
}

func (token *AuthJwtToken) Equal(other *AuthJwtToken) bool {
	return token.String() == other.String()
}

func convertAnyToPointer[T any](val any) *T {
	if vt, ok := val.(T); ok {
		return &vt
	}
	return nil
}

func CreateJwt(tokenData AuthJwtToken, cfg *JwtConfig) (string, error) {
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, jwt.MapClaims{
		"role":         tokenData.Role,
		"phone_number": tokenData.PhoneNumber,
		"user_id":      tokenData.UserID,
		"seller_id":    tokenData.SellerID,
		"expires":      tokenData.Expires.Format(time.RFC3339),
	})

	return token.SignedString([]byte(cfg.Secret))
}

func ReadJwt(token string, cfg *JwtConfig) (AuthJwtToken, error) {
	tokenParsed, err := jwt.Parse(token, func(token *jwt.Token) (interface{}, error) {
		// since we only use the one private key to sign the tokens,
		// we also only use its public counter part to verify
		return []byte(cfg.Secret), nil
	})
	if err != nil {
		return AuthJwtToken{}, err
	}
	if claims, ok := tokenParsed.Claims.(jwt.MapClaims); ok {
		expires, err := time.Parse(time.RFC3339, claims["expires"].(string))
		if err != nil {
			return AuthJwtToken{}, err
		}

		var userId *uuid.UUID
		var sellerId *uuid.UUID

		userIdString := convertAnyToPointer[string](claims["user_id"])
		if userIdString == nil {
			userId = nil
		} else {
			userIdRaw, err := uuid.Parse(*userIdString)
			if err != nil {
				return AuthJwtToken{}, err
			}
			userId = &userIdRaw
		}

		sellerIdString := convertAnyToPointer[string](claims["seller_id"])
		if sellerIdString == nil {
			sellerId = nil
		} else {
			sellerIdRaw, err := uuid.Parse(*sellerIdString)
			if err != nil {
				return AuthJwtToken{}, err
			}
			sellerId = &sellerIdRaw
		}

		token := AuthJwtToken{
			Role:        claims["role"].(string),
			PhoneNumber: convertAnyToPointer[string](claims["phone_number"]),
			UserID:      userId,
			SellerID:    sellerId,
			Expires:     expires,
		}
		return token, nil
	} else {
		return AuthJwtToken{}, errors.New("can't parse jwt")
	}
}
