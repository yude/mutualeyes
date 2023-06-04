package main

import (
	"log"
	"net/http"

	Config "github.com/yude/kakashiz/config"
	Handlers "github.com/yude/kakashiz/handlers"
)

func main() {
	Config.Load()

	mux := http.NewServeMux()
	mux.HandleFunc("/", Handlers.HelloHandler)

	log.Println("kakashiz will be served on :8080")
	log.Fatal(http.ListenAndServe(":8080", mux))
}
