package db

import (
	"context"
	"fmt"

	"github.com/jackc/pgx/v5/pgxpool"
)

type PostgresConfig struct {
	Host     string `yaml:"host"`
	Port     string `yaml:"port"`
	User     string `yaml:"user"`
	Password string `yaml:"password"`
	DbName   string `yaml:"db_name"`
}

func GetPostgresUrl(cfg PostgresConfig) string {
	return fmt.Sprintf(
		"postgres://%s:%s@%s:%s/%s",
		cfg.User,
		cfg.Password,
		cfg.Host,
		cfg.Port,
		cfg.DbName,
	)
}

func CreatePool(ctx context.Context, cfg PostgresConfig, minConns, maxConns int) (*pgxpool.Pool, error) {
	connString := GetPostgresUrl(cfg)
	poolConfig, err := pgxpool.ParseConfig(connString)
	if err != nil {
		return nil, err
	}

	poolConfig.MinConns = int32(minConns)
	poolConfig.MaxConns = int32(maxConns)

	return pgxpool.NewWithConfig(ctx, poolConfig)
}
