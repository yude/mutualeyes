package routine

import "github.com/robfig/cron/v3"

func Start() {
	c := cron.New()
	c.AddFunc("@every 5s", func() { NodeAliveCheck() })
	c.Start()
}
