package event

import (
	"fmt"
	"log"
	"net/http"
	"net/url"

	Config "github.com/yude/kakashiz/config"
	Types "github.com/yude/kakashiz/types"
)

// SendRemoteEvent
// Send the event done by this node.
// remote_event: Types.RemoteEvent
// How it works:
// 1. Convert internal remote_event to HTTP POST query.
// 2. Send it to every working nodes' endpoint.
func SendRemoteEvent(node_event_id string, node_event Types.NodeEvent) {
	query, err := ConvNodeEventToQuery(node_event)
	if err != nil {
		log.Println("Error: Failed to understand the event shown below:\n", node_event)
	}

	ps := url.Values{}
	ps.Add("name", query.Name)
	ps.Add("datetime", query.DateTime)
	ps.Add("type", query.Type)
	ps.Add("source", *Config.GetMe())
	ps.Encode()

	cfg := Config.GetConfig()

	for key, node := range cfg.Nodes {
		for _, n := range node {
			log.Println("Posting the event to node " + key + " (" + n.Domain + ")")
			res, err := http.PostForm(fmt.Sprintf("%s/receive_event", n.Domain), ps)
			if err != nil {
				log.Println("Error: Failed to post the event (event id: " + string(node_event_id) + ") to " + key + " - Node " + key + " is possibly down.")
			}

			if err == nil {
				defer res.Body.Close()
			}
		}
	}
}
