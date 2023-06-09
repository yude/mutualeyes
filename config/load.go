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

	// indent := strings.Repeat(" ", 14)

	// typ, val := reflect.TypeOf(*config), reflect.ValueOf(*config)
	// // for i := 0; i < typ.NumField(); i++ {
	// // 	indent := indent
	// // 	if i == 0 {
	// // 		indent = strings.Repeat(" ", 7)
	// // 	}
	// // 	fmt.Printf("%s%-11s → %v\n", indent, typ.Field(i).Name, val.Field(i).Interface())
	// // }

	keys := meta.Keys()
	sort.Slice(keys, func(i, j int) bool { return keys[i].String() < keys[j].String() })

	nodes := GetNodes()

	for _, k := range keys {
		// if i == 0 {
		// 	indent = strings.Repeat(" ", 10)
		// }

		// Retrieve node list
		if strings.Count(k.String(), ".") == 1 {
			if strings.HasPrefix(k.String(), "nodes.") {
				*nodes = append(*nodes, strings.Split(k.String(), ".")[1])
			}
		}

		// For debug: List all keys in config.toml
		// fmt.Printf("%s%-10s %s\n", indent, meta.Type(k...), k)
	}

}
