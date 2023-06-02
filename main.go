package main

import (
	"log"
	"net/http"

	Handlers "github.com/yude/kakashiz/handlers"
)

func main() {
	mux := http.NewServeMux()
	mux.HandleFunc("/", Handlers.HelloHandler)

	log.Println("kakashiz will be served on :8080")
	log.Fatal(http.ListenAndServe(":8080", mux))
}
