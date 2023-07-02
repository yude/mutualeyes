package routine

import (
	"log"
	"sort"
	"time"

	Config "github.com/yude/kakashiz/config"
	Event "github.com/yude/kakashiz/event"
	Platform "github.com/yude/kakashiz/platform"
	Status "github.com/yude/kakashiz/status"
	Types "github.com/yude/kakashiz/types"
)

// SendNotify
// Triggers the notification
func SendNotify() {
	me := Config.GetMe()
	events := Event.GetEvents()
	remote_events := Event.GetRemoteEvents()

	// Determine the order of alive node slice
	// The priority of node which is used for notification
	// is the same as the name order of nodes (ascending order)
	node_status := Status.GetNodeStatuses()
	var alive_nodes []string
	for k, v := range *node_status {
		if v.Status == Types.Up {
			alive_nodes = append(alive_nodes, k)
		}
	}
	alive_nodes = append(alive_nodes, *me)
	sort.SliceStable(alive_nodes, func(i, j int) bool {
		return alive_nodes[i] < alive_nodes[j]
	})
	if len(alive_nodes) <= 0 {
		log.Println("No node available to use for notification")
	}

	// eK: key of local event array
	// eV: value of local event array
	for eK, eV := range *events {
		// reK: key of remote event array
		// reV: value of remote event array
		for reK, reV := range *remote_events {
			// Determine whether carries out the notification process
			// about this event
			// 1. Check if this event is older than 2 minutes
			if eV.DateTime.Sub(time.Now()) <= time.Minute*2 {
				// 2. Check if this node is the top batter
				if alive_nodes[0] != *Config.GetMe() {
					return
				}
			}

			if eV.Name != reV.Event.Name { // Check the target node of this event
				return
			}
			if eV.Type != reV.Event.Type { // Check the type of this event
				return
			}

			// Caluculate time diff
			// Allow 15s lag
			time_diff := reV.Event.DateTime.Sub(eV.DateTime)
			if time_diff >= time.Second*15 {
				return
			}

			// If the loop reaches here, carries out the notification process
			log.Println("Info: Sending notification about this event:\n", "Target node: ", eV.Name, "\nEvent type: ", eV.Type, "\nEvent Timestamp: ", eV.DateTime)
			err := Platform.SendToDiscord(eV)
			if err != nil {
				log.Println("Error: [Discord] ", err)
			}

			// Pop this event
			*events = append((*events)[:eK], (*events)[eK+1:]...)
			*remote_events = append((*remote_events)[:reK], (*remote_events)[reK+1:]...)
		}
	}
}
