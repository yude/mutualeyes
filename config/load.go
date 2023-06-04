package config

import (
	"fmt"
	"log"
	"os"
	"reflect"
	"sort"
	"strings"

	"github.com/BurntSushi/toml"
	Types "github.com/yude/kakashiz/types"
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

	var config Types.Config
	meta, err := toml.DecodeFile(f, &config)
	if err != nil {
		log.Fatal(err)
	}

	indent := strings.Repeat(" ", 14)

	typ, val := reflect.TypeOf(config), reflect.ValueOf(config)
	for i := 0; i < typ.NumField(); i++ {
		indent := indent
		if i == 0 {
			indent = strings.Repeat(" ", 7)
		}
		fmt.Printf("%s%-11s → %v\n", indent, typ.Field(i).Name, val.Field(i).Interface())
	}

	fmt.Print("\nKeys")
	keys := meta.Keys()
	sort.Slice(keys, func(i, j int) bool { return keys[i].String() < keys[j].String() })
	for i, k := range keys {
		indent := indent
		if i == 0 {
			indent = strings.Repeat(" ", 10)
		}
		fmt.Printf("%s%-10s %s\n", indent, meta.Type(k...), k)
	}

	fmt.Print("\nUndecoded")
	keys = meta.Undecoded()
	sort.Slice(keys, func(i, j int) bool { return keys[i].String() < keys[j].String() })
	for i, k := range keys {
		indent := indent
		if i == 0 {
			indent = strings.Repeat(" ", 5)
		}
		fmt.Printf("%s%-10s %s\n", indent, meta.Type(k...), k)
	}
}
