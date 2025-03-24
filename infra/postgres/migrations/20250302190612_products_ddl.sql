-- +goose Up
-- +goose StatementBegin

BEGIN;

CREATE SCHEMA IF NOT EXISTS plotva;

CREATE TABLE IF NOT EXISTS plotva.product_categories (
    category_name VARCHAR(255) PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS plotva.products (
    product_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    seller_id UUID NOT NULL,
    category VARCHAR REFERENCES plotva.product_categories (category_name),
    photo_url VARCHAR(255) NOT NULL,
    price_rub BIGINT NOT NULL,
    price_last_updated TIMESTAMP NOT NULL DEFAULT NOW(),
    creation_time TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_products_name ON plotva.products (name);
CREATE INDEX idx_products_category ON plotva.products (category);
CREATE INDEX idx_products_price_rub ON plotva.products (price_rub);

CREATE TABLE IF NOT EXISTS plotva.comments (
    comment_id BIGSERIAL PRIMARY KEY,
    product_id UUID REFERENCES plotva.products (product_id),
    user_id UUID NOT NULL,
    content TEXT,
    rating SMALLINT NOT NULL,
    time TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_comments_product_id ON plotva.comments (product_id);
CREATE INDEX idx_comments_user_id ON plotva.comments (user_id);

END;

-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin

BEGIN;

DROP TABLE IF EXISTS plotva.comments CASCADE;
DROP TABLE IF EXISTS plotva.products CASCADE;
DROP TABLE IF EXISTS plotva.product_categories CASCADE;

END;

-- +goose StatementEnd
