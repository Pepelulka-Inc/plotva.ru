package internal

type ProductServiceConfig struct {
	DbMinConns int    `yaml:"db_min_conns"`
	DbMaxConns int    `yaml:"db_max_conns"`
	Port       string `yaml:"port"`
}
