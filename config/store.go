package config

import Types "github.com/yude/kakashiz/types"

var cfg Types.Config
var me string
var nodes []string

func GetConfig() *Types.Config {
	return &cfg
}

func GetNodes() *[]string {
	return &nodes
}

func GetMe() *string {
	return &me
}
