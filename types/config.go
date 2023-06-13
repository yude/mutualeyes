package types

type Config struct {
	General General
	Nodes   map[string][]Node
}

type General struct {
	Port int
}

type Node struct {
	Me       bool
	Domain   string
	Disabled bool
	Status   NodeStatus
}

type NodeStatus int

const (
	Ok NodeStatus = iota
	Ng
)
