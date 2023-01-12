package connection

import (
	"fmt"
	"html"
	"net/http"

	"github.com/gorilla/websocket"
)

var upgrader = websocket.Upgrader{
	CheckOrigin: func(r *http.Request) bool {
		return true // Accepting all requests
	},
}

func (m *Master) Echo(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintf(w, "Hello, %q", html.EscapeString(r.URL.Path))
}

func (m *Master) Websocket(w http.ResponseWriter, r *http.Request) {
	// fmt.Println("got someone")
	connection, _ := upgrader.Upgrade(w, r, nil)
	for {
		mt, message, err := connection.ReadMessage()
		if err != nil || mt == websocket.CloseMessage {
			break
		}
		go m.Handle(connection, message)
	}

	m.RemoveClient(connection)
	// connection.Close()
}

func (m *Master) Handle(conn *websocket.Conn, message []byte) {
	prot := &Protocol{}
	prot, err := prot.BytesToProtocol(message)
	if err == nil {
		if prot.Job == "join" {
			m.Join(conn, prot)
		}
		if prot.Job == "turn" {
			m.Turn(conn, prot)
		}
	}
}
