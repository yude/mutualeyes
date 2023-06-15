package routine

import (
	"fmt"
	"log"

	Event "github.com/yude/kakashiz/event"
	Status "github.com/yude/kakashiz/status"
)

// These functions should be used for debugging.

func PrintNodeEvents() {
	events := Event.GetEvents()
	log.Println("Current ongoing events:\n", *events)
}

func PrintNodeStatuses() {
	s := Status.GetNodeStatuses()
	fmt.Println("Current node status:\n", *s)
}
