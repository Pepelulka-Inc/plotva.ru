-- +goose Up
-- +goose StatementBegin

BEGIN;

CREATE SCHEMA IF NOT EXISTS plotva;

CREATE TABLE IF NOT EXISTS plotva.product_category (
    category_name VARCHAR(255) PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS plotva.product (
    product_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    seller_id UUID NOT NULL,
    category VARCHAR REFERENCES plotva.product_category (category_name),
    photo_url VARCHAR(255) NOT NULL,
    price_rub BIGINT NOT NULL,
    creation_time TIMESTAMP NOT NULL
);

CREATE INDEX idx_product_name ON plotva.product (name);
CREATE INDEX idx_product_category ON plotva.product (category);
CREATE INDEX idx_product_price_rub ON plotva.product (price_rub);

CREATE TABLE IF NOT EXISTS plotva.comment (
    comment_id BIGSERIAL PRIMARY KEY,
    product_id UUID REFERENCES plotva.product (product_id),
    user_id UUID NOT NULL,
    content TEXT,
    rating SMALLINT NOT NULL,
    time TIMESTAMP
);

CREATE INDEX idx_comment_product_id ON plotva.comment (product_id);
CREATE INDEX idx_comment_user_id ON plotva.comment (user_id);

END;

-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin

BEGIN;

DROP TABLE IF EXISTS plotva.comment CASCADE;
DROP TABLE IF EXISTS plotva.product CASCADE;
DROP TABLE IF EXISTS plotva.product_category CASCADE;

END;

-- +goose StatementEnd
