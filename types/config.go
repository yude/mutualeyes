package types

type Config struct {
	General  General
	Platform Platform
	Nodes    map[string][]NodeConfig
}

type General struct {
	Port int
}

type Platform struct {
	Discord string
}

type NodeConfig struct {
	Me       bool
	Domain   string
	Disabled bool
}
