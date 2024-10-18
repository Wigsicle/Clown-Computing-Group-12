package main

import (
	"os"

	"github.com/Wigsicle/Clown-Computing-Group-12/cli"
	"github.com/Wigsicle/Clown-Computing-Group-12/wallet"
)

func main() {
	defer os.Exit(0)
	cmd := cli.CommandLine{}
	cmd.Run()

	w := wallet.MakeWallet()
	w.Address()
}
