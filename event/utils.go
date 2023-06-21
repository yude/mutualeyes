package event

import (
	"errors"
	"time"

	Types "github.com/yude/kakashiz/types"
)

func ConvQueryToNodeEvent(query Types.NodeEventQuery) (Types.NodeEvent, error) {
	event := new(Types.NodeEvent)

	// Check if the query is properly provided
	// Specifically about DateTime and node name
	if query.DateTime == "" || query.Name == "" {
		return *event, errors.New("InvalidQuery")
	}
	event.Name = query.Name

	// Specifically about event type
	if query.Type == "up" || query.Type == "down" {
		switch query.Type {
		case "up":
			event.Type = Types.Up
		case "down":
			event.Type = Types.Down
		default:
			event.Type = Types.Invalid
		}
	}
	if event.Type == Types.Invalid {
		return *event, errors.New("InvalidQuery")
	}

	// Parse DateTime
	dt, err := time.Parse("", query.DateTime)
	if err != nil {
		return *event, errors.New("InvalidQuery")
	}
	event.DateTime = dt

	return *event, nil
}
