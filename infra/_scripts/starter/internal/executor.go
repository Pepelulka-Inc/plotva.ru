package internal

import (
	"path"

	"example.com/plotva-starter/models"
)

type Executor struct {
	RootPath string
}

func (e *Executor) Run(cmd models.Command) (<-chan error, error) {
	p := path.Join(e.RootPath, cmd.Directory)
	return ExecCommand(models.Command{
		Directory: p,
		Args:      cmd.Args,
	})
}

func (e *Executor) RunSync(cmd models.Command) ([]byte, error) {
	p := path.Join(e.RootPath, cmd.Directory)
	return ExecCommandSync(models.Command{
		Directory: p,
		Args:      cmd.Args,
	})
}
