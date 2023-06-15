package event

import (
	Types "github.com/yude/kakashiz/types"
)

var events []Types.NodeEvent

func GetEvents() *[]Types.NodeEvent {
	return &events
}
