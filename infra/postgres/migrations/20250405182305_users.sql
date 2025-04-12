-- +goose Up
-- +goose StatementBegin

BEGIN;

CREATE TABLE IF NOT EXISTS plotva.users (
    user_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name VARCHAR(128) NOT NULL,
    surname VARCHAR(128) NOT NULL,
    photo_url VARCHAR(255),
    phone_number VARCHAR(12) NOT NULL UNIQUE,
    email VARCHAR(255),
    hashed_password_base64 VARCHAR(255) NOT NULL
);

CREATE INDEX idx_phone_number ON plotva.users (phone_number);
CREATE INDEX idx_email ON plotva.users (email);
CREATE INDEX idx_name ON plotva.users (name);
CREATE INDEX idx_surname ON plotva.users (surname);
CREATE INDEX idx_name_surname ON plotva.users (name, surname);

END;

-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin

DROP TABLE IF EXISTS plotva.users;

-- +goose StatementEnd
