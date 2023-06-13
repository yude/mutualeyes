package routine

import (
	"log"
	"net/http"

	Config "github.com/yude/kakashiz/config"
	Types "github.com/yude/kakashiz/types"
)

func NodeAliveCheck() {
	cfg := Config.GetConfig()

	for key, node := range cfg.Nodes {
		for _, n := range node {
			if !n.Me {
				log.Println("Trying to ping node `" + key + "`.")

				resp, err := http.Get(n.Domain)
				if err != nil {
					log.Println(err)
				} else {
					if resp.StatusCode != 200 {
						log.Println("Node `" + key + "` is not working properly.")
						n.Status = Types.Ng
					} else {
						if n.Status == Types.Ok {
							log.Println("Node `" + key + "` is working fine.")
						} else {
							log.Println("Node `" + key + "` is recovered from disaster.")
							n.Status = Types.Ok
						}
					}
				}
			}
		}
	}
}
