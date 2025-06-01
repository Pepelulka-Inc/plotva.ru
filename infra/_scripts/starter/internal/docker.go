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

func (e *DockerComposeExecutor) StartManyServicesWithRollback(services []models.DockerComposeService) error {
	slog.Info("starting services...")
	for idx, service := range services {
		outp, err := e.StartService(service)
		if err != nil {
			// doing rollback
			for i := idx - 1; i >= 0; i-- {
				stopOutp, stopErr := e.StopService(services[i])
				if stopErr != nil {
					slog.Warn(fmt.Sprintf("error while doing rollback (can't stop service): %s", stopErr))
					NiceOutput(stopOutp, services[i].ComposeFilePath)
				}
			}
			slog.Warn("error starting service:")
			NiceOutput(outp, service.ComposeFilePath)
			return err
		}
	}
	return nil
}

func (e *DockerComposeExecutor) StopManyServices(services []models.DockerComposeService) (map[int]error, map[int][]byte) {
	errorMap := make(map[int]error)
	outpMap := make(map[int][]byte)
	slog.Info("stopping services...")
	for idx, service := range services {
		outp, err := e.StopService(service)
		if err != nil {
			errorMap[idx] = err
			outpMap[idx] = outp
		}
	}
	return errorMap, outpMap
}
