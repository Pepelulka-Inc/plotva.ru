package models

import (
	"fmt"
	"os"
	"path"

	"gopkg.in/yaml.v3"
)

// Если приложению нужен нестандартный билд (например product-service)
type CustomDockerBuildConfig struct {
	BuildCommand Command `yaml:"command"`
}

type DockerComposeService struct {
	ComposeFilePath string                   `yaml:"compose_file_path"`
	RequiredEnvVars []string                 `yaml:"req_env_vars"`
	CustomBuild     *CustomDockerBuildConfig `yaml:"custom_build,omitempty"`
	// в секундах
	StartCooldown *int `yaml:"start_cooldown"`
}

type BasicCommandTask struct {
	Command         Command  `yaml:"command"`
	RequiredEnvVars []string `yaml:"req_env_vars"`
}

type Task struct {
	BasicCommand *BasicCommandTask     `yaml:"basic_command"`
	Service      *DockerComposeService `yaml:"service"`
}

type Config struct {
	ProjectRoot string `yaml:"project_root"`
	Tasks       []Task `yaml:"tasks"`
}

func ParseAndValidateConfig(cfgPath string) (Config, error) {
	f, err := os.Open(cfgPath)
	if err != nil {
		return Config{}, fmt.Errorf("failed open config: %w", err)
	}
	defer f.Close()

	var cfg Config
	err = yaml.NewDecoder(f).Decode(&cfg)

	if !path.IsAbs(cfg.ProjectRoot) {
		return Config{}, fmt.Errorf("project root is not absolute path: %s", cfg.ProjectRoot)
	}

	return cfg, err
}
