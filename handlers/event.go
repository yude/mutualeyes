package handlers

import (
	"fmt"
	"log"
	"net/http"
	"time"

	Event "github.com/yude/kakashiz/event"
	Types "github.com/yude/kakashiz/types"
)

func GetEventHandler(w http.ResponseWriter, r *http.Request) {
	// Ignore GET requests
	if r.Method == http.MethodPost {
		e := Types.HandleError{
			Error: Types.InvalidMethod,
		}
		fmt.Fprintln(w, e)
		return
	}

	query_datetime := r.FormValue("datetime") // DateTime
	query_name := r.FormValue("name")         // Node name
	query_type := r.FormValue("type")         // Event type

	// Check if the query is properly provided
	// Specifically about DateTime and node name
	if query_datetime == "" || query_name == "" {
		e := Types.HandleError{
			Error: Types.InvalidQuery,
		}
		fmt.Fprintln(w, e)
		return
	}

	// Specifically about event type
	var event_type Types.NodeStatusType
	if query_type == "up" || query_type == "down" {
		switch query_type {
		case "up":
			event_type = Types.Up
		case "down":
			event_type = Types.Down
		default:
			event_type = Types.Invalid
		}
	}
	if event_type == Types.Invalid {
		e := Types.HandleError{
			Error: Types.InvalidQuery,
		}
		fmt.Fprintln(w, e)
		return
	}

	// Check if this node has the queried event
	events := Event.GetEvents()
	candidates := []Types.NodeEvent{}
	for _, v := range *events {
		if v.Name == query_name && v.Type == event_type {
			// Append the target event candidates
			candidates = append(candidates, v)
		}
	}

	// Caluculate time diff
	// Allow 15s lag
	time_parsed, err := time.Parse("", query_datetime)
	if err != nil {
		log.Println("Something bad happened during handling GetEvent request: ", err)
	}
	for _, v := range candidates {
		diff := v.DateTime.Sub(time_parsed)

		if diff <= time.Second*15 {
			fmt.Fprintln(w, v)
			return
		}
	}

	e := Types.HandleError{
		Error: Types.NoResult,
	}
	fmt.Fprintln(w, e)
}
