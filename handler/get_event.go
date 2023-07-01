package handlers

import (
	"fmt"
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

	// Parse query
	query := Types.NodeEventQuery{
		Name:     r.FormValue("name"),
		DateTime: r.FormValue("datetime"),
		Type:     r.FormValue("type"),
	}
	event, err := Event.ConvQueryToNodeEvent(query)
	if err != nil {
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
		if v.Name == event.Name && v.Type == event.Type {
			// Append the target event candidates
			candidates = append(candidates, v)
		}
	}

	// Caluculate time diff
	// Allow 15s lag
	for _, v := range candidates {
		diff := v.DateTime.Sub(event.DateTime)

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
