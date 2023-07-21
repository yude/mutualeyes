package handlers

import (
	"fmt"
	"log"
	"net/http"

	"github.com/oklog/ulid/v2"
	Event "github.com/yude/kakashiz/event"
	Types "github.com/yude/kakashiz/types"
)

// ReceiveRemoteEventHandler
// Remote event mainly means other nodes' completed tasks
// (e.g. posting notification to chat tools via webhook)
// Here's how these events are proceeded throughout this node:
//  1. These events are recorded to this node.
//  2. If one of these events matches the event which this node knows,
//     the records of these events will be marked as done, and this node
//     forget about it.
func ReceiveRemoteEventHandler(w http.ResponseWriter, r *http.Request) {
	log.Println("Received remote event, parsing...")
	remote_events := Event.GetRemoteEvents()

	// Ignore GET requests
	if r.Method == http.MethodGet {
		e := Types.HandleError{
			Error: Types.InvalidMethod,
		}
		log.Println("Received remote event, but its method is GET. Ignoring.")
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
		log.Println("Failed to parse remote event - [Query]", query, "[Error]", err)
		fmt.Fprintln(w, e)
		return
	}

	remote_event := Types.RemoteEvent{
		Event:      event,
		SourceNode: r.FormValue("source"),
	}
	log.Println("Received remote event - Event:", remote_event)

	ulid := ulid.Make().String()
	(*remote_events)[ulid] = remote_event
}
