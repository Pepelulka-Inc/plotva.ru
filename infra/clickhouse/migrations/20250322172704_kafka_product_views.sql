-- +goose Up
-- +goose StatementBegin

CREATE OR REPLACE TABLE kafka_product_views
(
    user_id UUID,
    product_id UUID,
    timestamp DateTime
)
ENGINE = Kafka
SETTINGS kafka_broker_list = 'host.docker.internal:9094',
         kafka_topic_list = 'product_views',
         kafka_group_name = 'clickhouse_group',
         kafka_format = 'JSONEachRow',
		 date_time_input_format='best_effort';

CREATE TABLE IF NOT EXISTS product_views (
	user_id UUID,
	product_id UUID,
	timestamp DateTime
)
ENGINE = MergeTree
ORDER BY timestamp;

CREATE MATERIALIZED VIEW IF NOT EXISTS product_views_mv TO product_views
AS
	SELECT
		user_id,
		product_id,
		timestamp
FROM kafka_product_views;

-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
DROP TABLE IF EXISTS product_views;
DROP TABLE IF EXISTS kafka_product_views;
DROP VIEW IF EXISTS product_views_mv;
-- +goose StatementEnd
