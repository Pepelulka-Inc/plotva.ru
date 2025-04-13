package internal

type AuthServiceConfig struct {
	DbMinConns int    `yaml:"db_min_conns"`
	DbMaxConns int    `yaml:"db_max_conns"`
	Port       string `yaml:"port"`
	OAuth      struct {
		ClientID         string   `yaml:"client_id"`
		ClientSecret     string   `yaml:"client_secret"`
		RedirectURL      string   `yaml:"redirect_url"`
		Scopes           []string `yaml:"scopes"`
		AuthURLEndpoint  string   `yaml:"auth_url_endpoint"`
		TokenURLEndpoint string   `yaml:"token_url_endpoint"`
	} `yaml:"oauth"`
}
