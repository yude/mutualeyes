package routine

import (
	"log"
	"time"

	Event "github.com/yude/kakashiz/event"
)

// Notify
// Triggers the notification
func Notify() {
	events := Event.GetEvents()
	remote_events := Event.GetRemoteEvents()

	// eK: key of local event array
	// eV: value of local event array
	for eK, eV := range *events {
		// reK: key of remote event array
		// reV: value of remote event array
		for reK, reV := range *remote_events {
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

			// Pop this event
			*events = append((*events)[:eK], (*events)[eK+1:]...)
			*remote_events = append((*remote_events)[:reK], (*remote_events)[reK+1:]...)
		}
	}
}
