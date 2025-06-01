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
		panic("missing command ('start' or 'stop')")
	}

	godotenv.Load(".env", "env.env")

	cfg, err := models.ParseAndValidateConfig(args[0])
	failOnError(err)

	dockerExec := internal.NewDockerComposeExecutor(cfg.ProjectRoot)

	if args[1] == "start" {
		err := dockerExec.StartManyServicesWithRollback(cfg.Services)
		failOnError(err)
	} else if args[1] == "stop" {
		errorMap, outpMap := dockerExec.StopManyServices(cfg.Services)
		for idx, err := range errorMap {
			fmt.Printf("%d service: error while stopping: %s\n", idx, err)
			internal.NiceOutput(outpMap[idx], strconv.FormatInt(int64(idx), 10))
		}
	} else {
		fmt.Printf("unknown command %s\n", args[1])
	}
}
