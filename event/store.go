package event

import (
	Types "github.com/yude/kakashiz/types"
)

var events map[string]Types.NodeEvent
var remote_events map[string]Types.RemoteEvent

func GetEvents() *map[string]Types.NodeEvent {
	if events == nil {
		events = make(map[string]Types.NodeEvent)
	}

	return &events
}

func GetRemoteEvents() *map[string]Types.RemoteEvent {
	if remote_events == nil {
		remote_events = make(map[string]Types.RemoteEvent)
	}

	return &remote_events
}
