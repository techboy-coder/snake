package main

import (
	"g/connection"
	"g/game"
	"sync"
)

func main() {
	game := game.NewField()
	master := connection.Master{
		Game:    game,
		Clients: &sync.Map{},
	}
	// Runs TCP server
	go master.Start()
	// Runs game loop
	master.Run()
}
