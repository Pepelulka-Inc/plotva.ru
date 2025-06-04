-- +goose Up

-- +goose StatementBegin
CREATE OR REPLACE TABLE kafka_orders
(
    user_id UUID,
    order_id UUID,
    product_id UUID,
    quantity UInt32,
    price Decimal(10, 2),
    timestamp DateTime
)
ENGINE = Kafka
SETTINGS kafka_broker_list = 'host.docker.internal:9094',
         kafka_topic_list = 'orders',
         kafka_group_name = 'clickhouse_orders_group',
         kafka_format = 'JSONEachRow',
		 date_time_input_format='best_effort'
-- +goose StatementEnd

-- +goose StatementBegin
CREATE TABLE IF NOT EXISTS orders (
	user_id UUID,
	order_id UUID,
	product_id UUID,
	quantity UInt32,
	price Decimal(10, 2),
	timestamp DateTime
)
ENGINE = MergeTree
ORDER BY timestamp
-- +goose StatementEnd

-- +goose StatementBegin
CREATE MATERIALIZED VIEW IF NOT EXISTS orders_mv TO orders
AS
	SELECT
		user_id,
		order_id,
		product_id,
		quantity,
		price,
		timestamp
FROM kafka_orders;
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
DROP TABLE IF EXISTS orders;
-- +goose StatementEnd
-- +goose StatementBegin
DROP TABLE IF EXISTS kafka_orders;
-- +goose StatementEnd
-- +goose StatementBegin
DROP VIEW IF EXISTS orders_mv;
-- +goose StatementEnd
