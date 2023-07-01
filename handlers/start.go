package handlers

import (
	"log"
	"net/http"
	"strconv"

	Config "github.com/yude/kakashiz/config"
)

func Start() {
	mux := http.NewServeMux()
	mux.HandleFunc("/", HelloHandler)
	mux.HandleFunc("/receive_event", ReceiveRemoteEventHandler)

	cfg := Config.GetConfig()
	port := strconv.Itoa(cfg.General.Port)

	log.Println("kakashiz will be served on :" + port)
	log.Fatal(http.ListenAndServe(":"+port, mux))
}
