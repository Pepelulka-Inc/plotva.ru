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
	GetPasswordHashById(context.Context, uuid.UUID) (exists bool, base64BCryptHashedPassword string, err error)
	GetPasswordHashByPhoneNumber(context.Context, string) (exists bool, base64BCryptHashedPassword string, err error)
	GetIdByPhoneNumber(context.Context, string) (exists bool, uuid uuid.UUID, err error)
	GetPhoneNumberById(context.Context, uuid.UUID) (exists bool, phoneNumber string, err error)
	// Can return ErrPhoneNumberAlreadyExists and ErrBadPassword
	CreateUser(context.Context, models.UserCreate) (models.UserCreateResponse, error)
}

// Errors:
var (
	ErrPhoneNumberAlreadyExists = errors.New("phone number exists")
	ErrBadPassword              = errors.New("bad password")
)

type UsersRepoPg struct {
	Pool *pgxpool.Pool
}

func (repo UsersRepoPg) GetIdByPhoneNumber(ctx context.Context, phoneNumber string) (bool, uuid.UUID, error) {
	queryString := `
SELECT 
	user_id
FROM
	plotva.users
WHERE
	phone_number = $1;
	`

	conn, err := repo.Pool.Acquire(ctx)
	if err != nil {
		return false, uuid.UUID{}, fmt.Errorf("can't acquire connection: %w", err)
	}

	row := conn.QueryRow(ctx, queryString, phoneNumber)
	var id uuid.UUID
	err = row.Scan(&id)
	if errors.Is(err, pgx.ErrNoRows) {
		return false, uuid.UUID{}, nil
	} else if err != nil {
		return false, uuid.UUID{}, err
	}
	return true, id, nil
}

func (repo UsersRepoPg) GetPhoneNumberById(ctx context.Context, userId uuid.UUID) (bool, string, error) {
	queryString := `
SELECT 
	phone_number
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
	var phoneNumber string
	err = row.Scan(&phoneNumber)
	if errors.Is(err, pgx.ErrNoRows) {
		return false, "", nil
	} else if err != nil {
		return false, "", err
	}
	return true, phoneNumber, nil
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

func (repo UsersRepoPg) GetPasswordHashByPhoneNumber(ctx context.Context, phoneNumber string) (exist bool, password string, err error) {
	queryString := `
SELECT 
	hashed_password_base64
FROM
	plotva.users
WHERE
	phone_number = $1;
	`

	conn, err := repo.Pool.Acquire(ctx)
	if err != nil {
		return false, "", fmt.Errorf("can't acquire connection: %w", err)
	}

	row := conn.QueryRow(ctx, queryString, phoneNumber)
	err = row.Scan(&password)
	if errors.Is(err, pgx.ErrNoRows) {
		return false, "", nil
	} else if err != nil {
		return false, "", err
	}
	return true, password, nil
}

func (repo UsersRepoPg) CreateUser(ctx context.Context, user models.UserCreate) (models.UserCreateResponse, error) {
	conn, err := repo.Pool.Acquire(ctx)
	if err != nil {
		return models.UserCreateResponse{}, fmt.Errorf("can't acquire connection: %w", err)
	}

	// Check if user with this phone number exists
	row := conn.QueryRow(ctx, "select * from plotva.users where phone_number = $1;", user.PhoneNumber)
	if err := row.Scan(); err == nil || !errors.Is(err, pgx.ErrNoRows) {
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
