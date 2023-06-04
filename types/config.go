package types

type Config struct {
	Nodes map[string]Node `toml:"nodes"`
}

type Node struct {
	Me       bool
	Domain   string
	Disabled bool
}
