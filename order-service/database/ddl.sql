CREATE TABLE "products"(
    "product_id" UUID ,
    "name" VARCHAR(255) ,
    "description" TEXT ,
    "seller_id" UUID ,
    "category" VARCHAR(255) ,
    "photo_url" VARCHAR(255) ,
    "creation_time" TIMESTAMP(0) WITHOUT TIME ZONE ,
    "price_rub" BIGINT ,
    "price_last_updated" TIMESTAMP(0) WITHOUT TIME ZONE 
);
ALTER TABLE
    "products" ADD PRIMARY KEY("product_id");
CREATE INDEX "products_name_index" ON
    "products"("name");
CREATE INDEX "products_seller_id_index" ON
    "products"("seller_id");
CREATE INDEX "products_category_index" ON
    "products"("category");
CREATE INDEX "products_creation_time_index" ON
    "products"("creation_time");
CREATE TABLE "product_categories"(
    "category_name" VARCHAR(255) 
);
ALTER TABLE
    "product_categories" ADD PRIMARY KEY("category_name");
CREATE TABLE "comments"(
    "comment_id" BIGINT ,
    "product_id" UUID ,
    "user_id" UUID ,
    "content" TEXT ,
    "rating" SMALLINT ,
    "time" TIMESTAMP(0) WITHOUT TIME ZONE 
);
ALTER TABLE
    "comments" ADD PRIMARY KEY("comment_id");
CREATE INDEX "comments_product_id_index" ON
    "comments"("product_id");
CREATE INDEX "comments_user_id_index" ON
    "comments"("user_id");
CREATE TABLE "sellers"(
    "seller_id" UUID ,
    "name" VARCHAR(255) ,
    "description" TEXT ,
    "photo_url" VARCHAR(255) ,
    "phone_number" VARCHAR(255) ,
    "email" BIGINT 
);
ALTER TABLE
    "sellers" ADD PRIMARY KEY("seller_id");
CREATE INDEX "sellers_name_index" ON
    "sellers"("name");
CREATE TABLE "users"(
    "user_id" UUID SERIAL ,
    "name" VARCHAR(255) ,
    "surname" VARCHAR(255) ,
    "photo_url" VARCHAR(255) ,
    "phone_number" VARCHAR(255) ,
    "email" VARCHAR(255),
    "hashed_password_base64" VARCHAR(255)
);
ALTER TABLE
    "users" ADD PRIMARY KEY("user_id");
ALTER TABLE
    "users" ADD CONSTRAINT "users_phone_number_unique" UNIQUE("phone_number");
CREATE TABLE "user_addresses"(
    "address_id" UUID ,
    "user_id" UUID ,
    "country" VARCHAR(255) ,
    "settlement" VARCHAR(255) ,
    "street" VARCHAR(255) ,
    "house_number" VARCHAR(255) ,
    "apartment_number" VARCHAR(255) ,
    "extra_info" TEXT NULL
);
ALTER TABLE
    "user_addresses" ADD PRIMARY KEY("address_id");
CREATE TABLE "shopping_cart_entries"(
    "entry_id" BIGINT ,
    "product_id" UUID ,
    "user_id" UUID ,
    "quantity" INTEGER 
);
ALTER TABLE
    "shopping_cart_entries" ADD PRIMARY KEY("entry_id");
CREATE INDEX "shopping_cart_entries_product_id_index" ON
    "shopping_cart_entries"("product_id");
CREATE INDEX "shopping_cart_entries_user_id_index" ON
    "shopping_cart_entries"("user_id");
CREATE TABLE "orders"(
    "order_id" UUID ,
    "user_id" UUID ,
    "address_id" UUID ,
    "status" VARCHAR(255) ,
    "order_date" TIMESTAMP(0) WITHOUT TIME ZONE ,
    "shipped_date" TIMESTAMP(0) WITHOUT TIME ZONE NULL,
    "total_cost_rub" BIGINT 
);
ALTER TABLE
    "orders" ADD PRIMARY KEY("order_id");
CREATE INDEX "orders_user_id_index" ON
    "orders"("user_id");
CREATE INDEX "orders_status_index" ON
    "orders"("status");
CREATE TABLE "order_entries"(
    "entry_id" BIGINT ,
    "order_id" UUID ,
    "product_id" UUID ,
    "quantity" BIGINT ,
    "product_name" VARCHAR(255) ,
    "product_price_rub" BIGINT ,
    "product_seller_id" UUID ,
    "product_seller_name" VARCHAR(255) 
);
ALTER TABLE
    "order_entries" ADD PRIMARY KEY("entry_id");
CREATE TABLE "product_prices_history"(
    "entry_id" BIGINT ,
    "product_id" UUID ,
    "price_rub" BIGINT ,
    "valid_from" TIMESTAMP(0) WITHOUT TIME ZONE ,
    "valid_to" TIMESTAMP(0) WITHOUT TIME ZONE 
);
ALTER TABLE
    "product_prices_history" ADD PRIMARY KEY("entry_id");
CREATE INDEX "product_prices_history_product_id_index" ON
    "product_prices_history"("product_id");
ALTER TABLE
    "shopping_cart_entries" ADD CONSTRAINT "shopping_cart_entries_product_id_foreign" FOREIGN KEY("product_id") REFERENCES "products"("product_id");
ALTER TABLE
    "shopping_cart_entries" ADD CONSTRAINT "shopping_cart_entries_user_id_foreign" FOREIGN KEY("user_id") REFERENCES "users"("user_id");
ALTER TABLE
    "comments" ADD CONSTRAINT "comments_product_id_foreign" FOREIGN KEY("product_id") REFERENCES "products"("product_id");
ALTER TABLE
    "order_entries" ADD CONSTRAINT "order_entries_product_id_foreign" FOREIGN KEY("product_id") REFERENCES "products"("product_id");
ALTER TABLE
    "orders" ADD CONSTRAINT "orders_user_id_foreign" FOREIGN KEY("user_id") REFERENCES "users"("user_id");
ALTER TABLE
    "product_prices_history" ADD CONSTRAINT "product_prices_history_product_id_foreign" FOREIGN KEY("product_id") REFERENCES "products"("product_id");
ALTER TABLE
    "comments" ADD CONSTRAINT "comments_user_id_foreign" FOREIGN KEY("user_id") REFERENCES "users"("user_id");
ALTER TABLE
    "user_addresses" ADD CONSTRAINT "user_addresses_user_id_foreign" FOREIGN KEY("user_id") REFERENCES "users"("user_id");
ALTER TABLE
    "products" ADD CONSTRAINT "products_category_foreign" FOREIGN KEY("category") REFERENCES "product_categories"("category_name");
ALTER TABLE
    "products" ADD CONSTRAINT "products_seller_id_foreign" FOREIGN KEY("seller_id") REFERENCES "sellers"("seller_id");
ALTER TABLE
    "order_entries" ADD CONSTRAINT "order_entries_order_id_foreign" FOREIGN KEY("order_id") REFERENCES "orders"("order_id");
ALTER TABLE
    "orders" ADD CONSTRAINT "orders_address_id_foreign" FOREIGN KEY("address_id") REFERENCES "user_addresses"("address_id");