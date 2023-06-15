package main

import (
	"log"

	Config "github.com/yude/kakashiz/config"
	Handlers "github.com/yude/kakashiz/handlers"
	Routine "github.com/yude/kakashiz/routine"
	Status "github.com/yude/kakashiz/status"
)

func main() {
	Config.Load()
	Status.InitNodeStatuses()
	log.Printf("Current nodes: %s\n", *Config.GetNodes())

	Routine.Start()
	Handlers.Start()
}
