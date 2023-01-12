package connection

import (
	"encoding/json"
	"fmt"
	"g/game"

	"github.com/gorilla/websocket"
)

func (p *Protocol) BytesToProtocol(msg []byte) (*Protocol, error) {
	// Use json.Unmarshal to convert msg to Handler
	h := &Protocol{}
	err := json.Unmarshal(msg, h)
	return h, err
}

func (p *Protocol) ProtocolToBytes() []byte {
	// Use json.Marshal to convert h to []byte
	msg, _ := json.Marshal(p)
	return msg
}

type Stats struct {
	SnakeAmount int
}

type Protocol struct {
	Job    string
	Stats  Stats
	Player *Player
	Field  [][]int
}

type Player struct {
	Connection   *websocket.Conn
	ViewDistance int
	Score        *int
	Direction    *int
	Name         string
	Snake        *game.Snake
}

func (p *Player) Update() {
	p.Score = &p.Snake.Score
	p.Direction = &p.Snake.Direction
}

func NewPlayer(f *game.Playingfield, c *websocket.Conn, viewdist int) *Player {
	fmt.Println("New Player joined")
	s := f.NewSnake()
	p := Player{
		Connection:   c,
		ViewDistance: viewdist,
		Snake:        s,
		Score:        &s.Score,
		Direction:    &s.Direction,
	}
	return &p
}
