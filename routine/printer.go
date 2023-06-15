package routine

import (
	"fmt"

	Event "github.com/yude/kakashiz/event"
	Status "github.com/yude/kakashiz/status"
)

// These functions should be used for debugging.

func PrintNodeEvents() {
	events := Event.GetEvents()
	fmt.Println("Current ongoing events:\n", *events)
}

func PrintNodeStatuses() {
	fmt.Println("Current node status")

	s := Status.GetNodeStatuses()
	fmt.Println(*s)
}
