package event

import (
	"time"

	"github.com/oklog/ulid/v2"

	Types "github.com/yude/kakashiz/types"
)

// This function should be called on node event: Down
// name: The name of target node
func AddNodeEvent(name string, event_type Types.NodeStatusType) {
	events := GetEvents()

	event := Types.NodeEvent{
		// Generate unique event id based on ULID.
		// This unique id only works in each node.
		Id:       ulid.Make().String(),
		Name:     name,
		DateTime: time.Now(),
		Type:     event_type,
	}

	// Add this node event to event listing
	*events = append(*events, event)

	// Send this event to other nodes
	SendRemoteEvent(event)
}
