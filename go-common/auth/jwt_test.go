package auth

import (
	"testing"
	"time"

	"github.com/google/uuid"
)

func TestJwtToken(t *testing.T) {
	cfg := JwtConfig{
		Secret: "abcabc",
	}
	userId := uuid.New()
	number := "123456"

	truncTime, _ := time.Parse(time.RFC3339, time.Now().Format(time.RFC3339))

	data := AuthJwtToken{
		Role:        "meow",
		UserID:      &userId,
		SellerID:    nil,
		PhoneNumber: &number,
		Expires:     truncTime,
	}

	jwtData, err := CreateJwt(data, &cfg)
	if err != nil {
		t.Fatalf("error creating jwt: %v", err)
	}

	newData, err := ReadJwt(jwtData, &cfg)
	if err != nil {
		t.Fatalf("error creating jwt: %v", err)
	}

	if !data.Equal(&newData) {
		t.Fatalf("tokens doesn't match! expected: %v, \ngot: %v", data.String(), newData.String())
	}
}
