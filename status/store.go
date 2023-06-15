package status

import (
	Config "github.com/yude/kakashiz/config"
	Types "github.com/yude/kakashiz/types"
)

// Node statuses
var nodes map[string]Types.NodeStatus

func GetNodeStatuses() *map[string]Types.NodeStatus {
	return &nodes
}

func InitNodeStatuses() {
	nodes = make(map[string]Types.NodeStatus)
	init := Types.NodeStatus{
		Status: Types.Up,
	}
	cfg := Config.GetConfig()

	for key := range cfg.Nodes {
		nodes[key] = init
	}
}

func UpNode(name string) {
	nodes[name] = Types.NodeStatus{
		Status: Types.Up,
	}
}

func DownNode(name string) {
	nodes[name] = Types.NodeStatus{
		Status: Types.Down,
	}
}

func IsDown(name string) bool {
	m := nodes[name]
	if m.Status == Types.Down {
		return true
	} else {
		return false
	}
}
