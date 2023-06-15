package routine

import (
	"log"
	"net/http"
	"time"

	"github.com/oklog/ulid/v2"
	Config "github.com/yude/kakashiz/config"
	Event "github.com/yude/kakashiz/event"
	Status "github.com/yude/kakashiz/status"
	Types "github.com/yude/kakashiz/types"
)

func NodeAliveCheck() {
	cfg := Config.GetConfig()
	events := Event.GetEvents()

	for key, node := range cfg.Nodes {
		for _, n := range node {
			if !n.Me {
				log.Println("Trying to ping node `" + key + "`.")

				resp, err := http.Get(n.Domain)
				// If the node becomes down status (Case: connection timeout)
				if err != nil {
					if !Status.IsDown(key) {
						log.Println("Node `" + key + "` is not working properly.")
						Status.DownNode(key)
						Event.AddDownNode(key)
					} else {
						log.Println("Node `" + key + "` is still ongoing in the disaster.")
					}
				} else {
					// If the node becomes down status (Case: no 202 status code)
					if resp.StatusCode != 200 && !Status.IsDown(key) {
						log.Println("Node `" + key + "` is not working properly.")
						Status.DownNode(key)
						Event.AddDownNode(key)
					} else {
						if !Status.IsDown(key) {
							log.Println("Node `" + key + "` is working fine.")
						} else {
							// If the node becomes up status
							log.Println("Node `" + key + "` is recovered from disaster.")
							Status.UpNode(key)

							// Remove events that implies this node is down
							for i, v := range *events {
								if v.Name == key && v.Type == Types.Down {
									e := *events
									e = append(e[:i], e[i+1:]...)
									*events = e
								}
							}

							// Add this node event to event listing
							*events = append(*events, Types.NodeEvent{
								// Generate unique event id based on ULID.
								// This unique id only works in each node.
								Id:       ulid.Make().String(),
								Name:     key,
								DateTime: time.Now(),
								Type:     Types.Up,
							})
						}
					}
				}
			}
		}
	}
}
