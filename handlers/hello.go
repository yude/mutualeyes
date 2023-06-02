package handlers

import (
	"bytes"
	"encoding/json"
	"fmt"
	"log"
	"net/http"

	Types "github.com/yude/kakashiz/types"
)

func HelloHandler(w http.ResponseWriter, _ *http.Request) {
	status := Types.Status{
		ID: "aaa",
	}

	var buf bytes.Buffer
	enc := json.NewEncoder(&buf)
	if err := enc.Encode(&status); err != nil {
		log.Fatal("Error:", err)
	}

	_, err := fmt.Fprint(w, buf.String())
	if err != nil {
		return
	}
}
