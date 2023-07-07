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
		return *event, errors.New("invalid event type")
	}

	// Parse DateTime
	dt, err := time.Parse("2006-01-02 15:04:05.000000000 -0700 MST", query.DateTime)
	if err != nil {
		return *event, errors.New("invalid timestamp")
	}
	event.DateTime = dt

	return *event, nil
}

func ConvNodeEventToQuery(event Types.NodeEvent) (Types.NodeEventQuery, error) {
	query := new(Types.NodeEventQuery)

	if &event.DateTime == nil || event.Id == "" || event.Name == "" || &event.Type == nil {
		return *query, errors.New("some field of this query is empty")
	}

	query.DateTime = event.DateTime.Format("2006-01-02 15:04:05.000000000 -0700 MST")
	query.Name = event.Name
	switch event.Type {
	case Types.Up:
		query.Type = "up"
	case Types.Down:
		query.Type = "down"
	default:
		query.Type = "invalid"
	}

	return *query, nil
}
