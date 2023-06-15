package config

import (
	"log"
	"os"
	"sort"
	"strings"

	"github.com/BurntSushi/toml"
)

func Load() {
	args := os.Args[1:]

	if len(args) != 1 {
		log.Fatal("Error: Please specify the location of config.toml")
	}

	f := args[0]
	if _, err := os.Stat(f); err != nil {
		log.Fatal(err)
	}

	config := GetConfig()
	meta, err := toml.DecodeFile(f, &config)
	if err != nil {
		log.Fatal(err)
	}

	keys := meta.Keys()
	sort.Slice(keys, func(i, j int) bool { return keys[i].String() < keys[j].String() })

	// Init node list
	nodes := GetNodes()
	for _, k := range keys {
		// Retrieve node list
		if strings.Count(k.String(), ".") == 1 {
			if strings.HasPrefix(k.String(), "nodes.") {
				*nodes = append(*nodes, strings.Split(k.String(), ".")[1])
			}
		}
	}
}
