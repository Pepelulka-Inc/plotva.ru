package internal

import (
	"fmt"
	"log/slog"
	"os"
	"path"
	"time"

	"example.com/plotva-starter/models"
)

type DockerComposeExecutor struct {
	Executor
}

func collectEnvVars(requiredEnvVars []string) (map[string]string, error) {
	res := make(map[string]string)
	for _, name := range requiredEnvVars {
		value, exists := os.LookupEnv(name)
		if !exists {
			return nil, fmt.Errorf("env var %s is not defined but required", name)
		}
		res[name] = value
	}
	return res, nil
}

func NewDockerComposeExecutor(projectRoot string) DockerComposeExecutor {
	return DockerComposeExecutor{
		Executor{
			RootPath: projectRoot,
		},
	}
}

func (e *DockerComposeExecutor) StartService(service models.DockerComposeService) ([]byte, error) {
	slog.Info(fmt.Sprintf("Starting service %s", service.ComposeFilePath))

	if service.CustomBuild != nil {
		outp, err := e.Executor.RunSync(service.CustomBuild.BuildCommand)
		if err != nil {
			return outp, err
		}
	}

	if service.StartCooldown != nil {
		cd := *service.StartCooldown
		time.Sleep(time.Duration(cd) * time.Second)
	}

	envVars, err := collectEnvVars(service.RequiredEnvVars)
	if err != nil {
		return nil, err
	}

	return e.Executor.RunSync(
		models.Command{
			Directory: path.Dir(service.ComposeFilePath),
			Args: []string{
				"docker-compose",
				"-f",
				path.Base(service.ComposeFilePath),
				"up",
				"-d",
			},
			Env: envVars,
		},
	)
}

func (e *DockerComposeExecutor) StopService(service models.DockerComposeService) ([]byte, error) {
	slog.Info(fmt.Sprintf("Stopping service %s", service.ComposeFilePath))
	return e.Executor.RunSync(
		models.Command{
			Directory: path.Dir(service.ComposeFilePath),
			Args: []string{
				"docker-compose",
				"-f",
				path.Base(service.ComposeFilePath),
				"down",
				"-v", // !!! WARNING
				"-t",
				"0",
			},
		},
	)
}

func (e *DockerComposeExecutor) StartManyTasksWithRollbackInServices(tasks []models.Task) error {
	slog.Info("starting tasks...")
	for idx, task := range tasks {
		doRollback := func(idx int) {
			for i := idx - 1; i >= 0; i-- {
				if tasks[i].Service == nil {
					continue
				}
				stopOutp, stopErr := e.StopService(*tasks[i].Service)
				if stopErr != nil {
					slog.Warn(fmt.Sprintf("error while doing rollback (can't stop service): %s", stopErr))
					NiceOutput(stopOutp, tasks[i].Service.ComposeFilePath)
				}
			}
		}

		if task.BasicCommand != nil {
			_, err := collectEnvVars(task.BasicCommand.RequiredEnvVars)
			if err != nil {
				return err
			}

			outp, err := e.Executor.RunSync(task.BasicCommand.Command)
			NiceOutput(outp, fmt.Sprintf("output for basic command: %v", task.BasicCommand.Command.Args))
			if err != nil {
				slog.Warn(fmt.Sprintf("error executing basic command: %v", task.BasicCommand.Command.Args))
				doRollback(idx)
				return err
			}
		}

		if task.Service == nil {
			continue
		}

		outp, err := e.StartService(*task.Service)
		if err != nil {
			// doing rollback
			doRollback(idx)
			slog.Warn("error starting service:")
			NiceOutput(outp, task.Service.ComposeFilePath)
			return err
		}
	}
	return nil
}

func (e *DockerComposeExecutor) StopManyServicesInTasks(tasks []models.Task) (map[int]error, map[int][]byte) {
	errorMap := make(map[int]error)
	outpMap := make(map[int][]byte)
	slog.Info("stopping services...")
	for idx, task := range tasks {
		if task.Service == nil {
			continue
		}
		outp, err := e.StopService(*task.Service)
		if err != nil {
			errorMap[idx] = err
			outpMap[idx] = outp
		}
	}
	return errorMap, outpMap
}
