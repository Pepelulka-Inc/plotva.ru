package internal

import (
	"fmt"
	"os"
)

func NiceOutput(outp []byte, header string) {
	fmt.Println(header, " +---------------------------+ ")
	os.Stdout.Write(outp)
	fmt.Println()
	fmt.Println(" +-------------------------------------------+ ")
}
