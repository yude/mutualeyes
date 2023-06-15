package routine

import "github.com/robfig/cron/v3"

func Start() {
	c := cron.New()

	// The routines for production use.
	c.AddFunc("@every 5s", func() { NodeAliveCheck() })

	// The routines for debugging.
	c.AddFunc("@every 5s", func() { PrintNodeEvents() })
	c.AddFunc("@every 5s", func() { PrintNodeStatuses() })

	c.Start()
}
