package event

import (
	Types "github.com/yude/kakashiz/types"
)

var events []Types.NodeEvent
var remote_events []Types.RemoteEvent

func GetEvents() *[]Types.NodeEvent {
	return &events
}

func GetRemoteEvents() *[]Types.RemoteEvent {
	return &remote_events
}
