package connection

import (
	"bytes"
	"encoding/json"
	"fmt"
	"g/game"
	"net/http"
	"sync"
)

type Master struct {
	Game    *game.Playingfield
	Clients *sync.Map
}

// Needed for leaderboard
type SimpleSnake struct {
	Name  string
	Score int
}

// Starts listening and handling requests
func (m *Master) Start() {
	http.HandleFunc("/", m.Echo)
	http.HandleFunc("/ws", m.Websocket)
	http.HandleFunc("/leaderboard", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Access-Control-Allow-Origin", "*")
		if r.Method == "OPTIONS" {
			w.Header().Set("Access-Control-Allow-Headers", "Authorization") // You can add more headers here if needed
		} else {
			// Your code goes here
			leaderboard := m.Leaderboard()
			type Out struct {
				Leaderboard []*SimpleSnake
			}
			lb := Out{
				Leaderboard: leaderboard,
			}
			reqBodyBytes := new(bytes.Buffer)
			json.NewEncoder(reqBodyBytes).Encode(lb)
			w.Write(reqBodyBytes.Bytes())
		}

	})
	fmt.Println("Listenig on localhost:8080")
	http.ListenAndServe(":8080", nil)
}

// by Shivram Sambhus @techboy-coder
