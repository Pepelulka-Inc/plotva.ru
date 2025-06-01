package internal

import (
	"fmt"
	"os"
	"os/exec"

	"example.com/plotva-starter/models"
)

func ExecCommandSync(cmd models.Command) (output []byte, err error) {
	if len(cmd.Args) < 1 {
		return nil, fmt.Errorf("args is empty")
	}
	command := exec.Command(cmd.Args[0], cmd.Args[1:]...)
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
	command := exec.Command(cmd.Args[0], cmd.Args[1:]...)
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
