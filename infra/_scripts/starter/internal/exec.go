package internal

import (
	"fmt"
	"os"
	"os/exec"
	"regexp"
	"strings"

	"example.com/plotva-starter/models"
)

func expandEnvVars(args []string, cmdEnv map[string]string) []string {
	// Создаем полную карту переменных окружения
	envMap := make(map[string]string)

	// Сначала добавляем системные переменные
	for _, env := range os.Environ() {
		parts := strings.SplitN(env, "=", 2)
		if len(parts) == 2 {
			envMap[parts[0]] = parts[1]
		}
	}

	// Затем переменные из команды (они имеют приоритет)
	for k, v := range cmdEnv {
		envMap[k] = v
	}

	// Регулярное выражение для поиска ${VAR_NAME}
	re := regexp.MustCompile(`\$\{([^}]+)\}`)

	expandedArgs := make([]string, len(args))

	for i, arg := range args {
		expandedArgs[i] = re.ReplaceAllStringFunc(arg, func(match string) string {
			// Извлекаем имя переменной из ${VAR_NAME}
			varName := match[2 : len(match)-1] // убираем ${ и }

			if value, exists := envMap[varName]; exists {
				return value
			}

			// Если переменная не найдена, возвращаем исходную строку
			return match
		})
	}

	return expandedArgs
}

func ExecCommandSync(cmd models.Command) (output []byte, err error) {
	if len(cmd.Args) < 1 {
		return nil, fmt.Errorf("args is empty")
	}
	expandedArgs := expandEnvVars(cmd.Args, nil)
	command := exec.Command(expandedArgs[0], expandedArgs[1:]...)
	env := os.Environ()
	for k, v := range cmd.Env {
		env = append(env, fmt.Sprintf("%s=%s", k, v))
	}
	command.Env = env
	command.Dir = cmd.Directory
	return command.CombinedOutput()
}

func ExecCommand(cmd models.Command) (errorChan <-chan error, err error) {
	if len(cmd.Args) < 1 {
		return nil, fmt.Errorf("args is empty")
	}
	expandedArgs := expandEnvVars(cmd.Args, nil)
	command := exec.Command(expandedArgs[0], expandedArgs[1:]...)
	env := os.Environ()
	for k, v := range cmd.Env {
		env = append(env, fmt.Sprintf("%s=%s", k, v))
	}
	command.Env = env
	command.Dir = cmd.Directory

	errChan := make(chan error)

	go func() {
		errChan <- command.Run()
	}()

	return errChan, nil
}
