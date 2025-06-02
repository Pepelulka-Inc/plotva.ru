package main

import (
	"flag"
	"fmt"
	"strconv"

	"example.com/plotva-starter/internal"
	"example.com/plotva-starter/models"
	"github.com/joho/godotenv"
)

func failOnError(err error) {
	if err != nil {
		panic(err)
	}
}

func main() {
	flag.Parse()
	args := flag.Args()

	if len(args) < 1 {
		panic("missing start.yaml path!")
	}

	if len(args) < 2 {
		panic("missing command ('start', 'stop' or 'restart')")
	}

	godotenv.Load(".env", "env.env")

	cfg, err := models.ParseAndValidateConfig(args[0])
	failOnError(err)

	dockerExec := internal.NewDockerComposeExecutor(cfg.ProjectRoot)

	if args[1] == "start" {
		err := dockerExec.StartManyTasksWithRollbackInServices(cfg.Tasks)
		failOnError(err)
	} else if args[1] == "stop" {
		errorMap, outpMap := dockerExec.StopManyServicesInTasks(cfg.Tasks)
		for idx, err := range errorMap {
			fmt.Printf("%d service: error while stopping: %s\n", idx, err)
			internal.NiceOutput(outpMap[idx], strconv.FormatInt(int64(idx), 10))
		}
	} else if args[1] == "restart" {
		errorMap, outpMap := dockerExec.StopManyServicesInTasks(cfg.Tasks)
		for idx, err := range errorMap {
			fmt.Printf("%d service: error while stopping: %s\n", idx, err)
			internal.NiceOutput(outpMap[idx], strconv.FormatInt(int64(idx), 10))
		}
		err := dockerExec.StartManyTasksWithRollbackInServices(cfg.Tasks)
		failOnError(err)
	} else {
		fmt.Printf("unknown command %s\n", args[1])
	}
}
