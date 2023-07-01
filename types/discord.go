package types

type DiscordImg struct {
	URL string `json:"url"`
	H   int    `json:"height"`
	W   int    `json:"width"`
}
type DiscordAuthor struct {
	Name string `json:"name"`
	URL  string `json:"url"`
	Icon string `json:"icon_url"`
}
type DiscordField struct {
	Name   string `json:"name"`
	Value  string `json:"value"`
	Inline bool   `json:"inline"`
}
type DiscordEmbed struct {
	Title  string         `json:"title"`
	Desc   string         `json:"description"`
	URL    string         `json:"url"`
	Color  int            `json:"color"`
	Image  DiscordImg     `json:"image"`
	Thum   DiscordImg     `json:"thumbnail"`
	Author DiscordAuthor  `json:"author"`
	Fields []DiscordField `json:"fields"`
}

type DiscordWebhook struct {
	UserName  string         `json:"username"`
	AvatarURL string         `json:"avatar_url"`
	Content   string         `json:"content"`
	Embeds    []DiscordEmbed `json:"embeds"`
	TTS       bool           `json:"tts"`
}
