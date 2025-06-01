package models

type Command struct {
	Directory string            `yaml:"dir"`
	Args      []string          `yaml:"args"`
	Env       map[string]string `yaml:"env"`
}
