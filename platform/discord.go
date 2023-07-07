package platform

import (
	"bytes"
	"encoding/json"
	"errors"
	"log"
	"net/http"

	Config "github.com/yude/kakashiz/config"
	Types "github.com/yude/kakashiz/types"
)

func SendToDiscord(event Types.NodeEvent) error {
	cfg := Config.GetConfig()
	url := cfg.Platform.Discord

	if url == "" {
		log.Println("Info: the URL of Discord's webhook destination is empty. This node won't use Discord platform.")
		return nil
	}

	me := Config.GetMe()

	var embed_color int
	var event_type string

	switch event.Type {
	case Types.Up:
		embed_color = 0x24FD4D
		event_type = "Up"
	case Types.Down:
		embed_color = 0xF85A5A
		event_type = "Down"
	default:
		embed_color = 0xD2D2D2
		event_type = "Unknown"
	}

	dw := &Types.DiscordWebhook{
		UserName: "kakashiz",
	}
	dw.Embeds = []Types.DiscordEmbed{
		Types.DiscordEmbed{
			Title: event_type + ": " + event.Name,
			Desc:  "Since " + event.DateTime.String(),
			Color: embed_color,
			Author: Types.DiscordAuthor{
				Name: "Source of this notification: " + *me,
			},
		},
	}

	j, err := json.Marshal(dw)
	if err != nil {
		return errors.New("Failed to create json struct.")
	}

	req, err := http.NewRequest("POST", url, bytes.NewBuffer(j))
	if err != nil {
		return err
	}
	req.Header.Set("Content-Type", "application/json")

	client := http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return errors.New("Failed to make our client work.")
	}

	if resp.StatusCode == 204 {
		return nil
	} else {
		return errors.New("Failed to communicate with Discord server.")
	}
}
