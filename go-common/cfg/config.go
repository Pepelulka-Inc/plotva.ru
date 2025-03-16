package cfg

import (
	"os"

	"gopkg.in/yaml.v3"
)

type ProjectConfig map[string]any

func ParseProjectConfig(filename string) (ProjectConfig, error) {
	data, err := os.ReadFile(filename)

	if err != nil {
		return ProjectConfig{}, err
	}

	result := make(map[string]any)
	err = yaml.Unmarshal(data, result)
	if err != nil {
		return ProjectConfig{}, err
	}

	return ProjectConfig(result), nil
}

// Функция чтобы преобразовать any к go-структуре. У структуры должны быть проставлены yaml теги полей.
func InterpretAsStructure[T any](cfg any) (T, error) {
	data, err := yaml.Marshal(cfg)
	var result T

	if err != nil {
		return result, err
	}

	err = yaml.Unmarshal(data, &result)
	return result, err
}
