package types

type Config struct {
	General General
	Nodes   map[string][]NodeConfig
}

type General struct {
	Port int
}

type NodeConfig struct {
	Me       bool
	Domain   string
	Disabled bool
}
