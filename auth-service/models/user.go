package models

import (
	jt "plotva.ru/common/json_types"
)

type User struct {
	UserID               jt.JsonUUID `json:"user_id"`
	Name                 string      `json:"name"`
	Surname              string      `json:"surname"`
	PhotoURL             *string     `json:"photo_url,omitempty"`
	PhoneNumber          string      `json:"phone_number"`
	Email                *string     `json:"email,omitempty"`
	HashedPasswordBase64 string      `json:"hashed_password_base64"`
}

type UserCreate struct {
	Name        string `json:"name"`
	Surname     string `json:"surname"`
	PhoneNumber string `json:"phone_number"`
	Password    string `json:"password"`
}

type UserCreateResponse struct {
	UserID jt.JsonUUID `json:"user_id"`
}

type UserLoginUUID struct {
	UserID   jt.JsonUUID `json:"user_id"`
	Password string      `json:"string"`
}

type UserLoginPhoneNumber struct {
	PhoneNumber string `json:"phone_number"`
	Password    string `json:"password"`
}
