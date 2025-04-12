package repo

import (
	"auth-service/models"
	"context"
	"errors"
	"fmt"

	"github.com/google/uuid"
	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"
	"plotva.ru/common/auth"
)

type UsersRepo interface {
	// Args:
	// 1) true if user exists, otherwise false
	// 2) base64 bcrypt hashed password
	// 3) error
	GetPasswordHashById(context.Context, uuid.UUID) (bool, string, error)
	// Can return ErrPhoneNumberAlreadyExists and ErrBadPassword
	LoginUser(context.Context, models.UserCreate) (models.UserCreateResponse, error)
}

// Errors:
var (
	ErrPhoneNumberAlreadyExists = errors.New("phone number exists")
	ErrBadPassword              = errors.New("bad password")
)

type UsersRepoPg struct {
	Pool *pgxpool.Pool
}

func (repo UsersRepoPg) GetPasswordHashById(ctx context.Context, userId uuid.UUID) (exist bool, password string, err error) {
	queryString := `
SELECT 
	hashed_password_base64
FROM
	plotva.users
WHERE
	user_id = $1;
	`

	conn, err := repo.Pool.Acquire(ctx)
	if err != nil {
		return false, "", fmt.Errorf("can't acquire connection: %w", err)
	}

	row := conn.QueryRow(ctx, queryString, userId)
	err = row.Scan(&password)
	if errors.Is(err, pgx.ErrNoRows) {
		return false, "", nil
	} else if err != nil {
		return false, "", err
	}
	return true, password, nil
}

func (repo UsersRepoPg) LoginUser(ctx context.Context, user models.UserCreate) (models.UserCreateResponse, error) {
	conn, err := repo.Pool.Acquire(ctx)
	if err != nil {
		return models.UserCreateResponse{}, fmt.Errorf("can't acquire connection: %w", err)
	}

	// Check if user with this phone number exists
	row := conn.QueryRow(ctx, "select * from plotva.users where phone_number = $1;", user.PhoneNumber)
	if err := row.Scan(); err != nil && errors.Is(err, pgx.ErrNoRows) {
		return models.UserCreateResponse{}, ErrPhoneNumberAlreadyExists
	}

	queryString := `
INSERT INTO plotva.users (name, surname, phone_number, hashed_password_base64)
VALUES ($1, $2, $3, $4)
RETURNING user_id;
	`

	hashedPassword, err := auth.HashPassword(user.Password)
	if err != nil {
		return models.UserCreateResponse{}, ErrBadPassword
	}
	row = conn.QueryRow(ctx, queryString, user.Name, user.Surname, user.PhoneNumber, hashedPassword)
	var result models.UserCreateResponse
	if err = row.Scan(&result.UserID); err != nil {
		return models.UserCreateResponse{}, err
	}
	return result, nil
}
