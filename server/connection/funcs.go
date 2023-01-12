package connection

import (
	"sort"
	"sync"
	"time"

	"github.com/gorilla/websocket"
)

var tick = 100

func (m *Master) Join(conn *websocket.Conn, prot *Protocol) {
	if prot.Player == nil || prot.Player.ViewDistance < 0 {
		prot.Player.ViewDistance = 2
	}
	player := NewPlayer(m.Game, conn, prot.Player.ViewDistance)
	player.Name = prot.Player.Name
	// m.Clients[conn] = player
	m.Clients.Store(conn, player)
	// fmt.Println("Player joined")
	conn.WriteJSON(prot)
}

func (m *Master) Turn(conn *websocket.Conn, prot *Protocol) {
	// player := m.Clients[conn]
	p, found := m.Clients.Load(conn)
	player, ok := p.(*Player)
	if found && ok && player != nil {
		snake := player.Snake
		if snake != nil {
			if prot.Player.Direction == nil {
				dir := -1
				prot.Player.Direction = &dir
			}
			snake.SetDirection(*prot.Player.Direction)
			player.Direction = &snake.Direction
			player.Score = &snake.Score
			prot.Player = player
		}
	}
}

func (m *Master) RemoveClient(conn *websocket.Conn) {
	// m.Clients[conn] = nil
	m.Clients.Delete(conn)
	// delete(m.Clients, conn)
	conn.Close()
}

func LenSyncMap(m *sync.Map) int {
	var i int
	m.Range(func(k, v interface{}) bool {
		i++
		return true
	})
	return i
}

func (m *Master) Run() {
	ticker := time.NewTicker(time.Duration(tick) * time.Millisecond)
	quit := make(chan struct{})
	frame := 1
	for {
		select {
		case <-ticker.C:
			m.Tick()
			m.Game.Update()
			frame++
		case <-quit:
			ticker.Stop()
			return
		}
	}
}

func (m *Master) Tick() {
	m.Clients.Range(func(key, value any) bool {
		conn, ok := key.(*websocket.Conn)
		if !ok {
			return true
		}
		player, ok := value.(*Player)
		if !ok {
			return true
		}
		// for conn, player := range m.Clients {
		player.Update()
		prot := Protocol{
			Job: "update",
			Stats: Stats{
				SnakeAmount: len(m.Game.Snakes),
			},
		}
		if conn != nil && player != nil {
			snake := player.Snake
			if snake != nil {
				prot.Field = m.Game.FieldsAround(snake.X, snake.Y, player.ViewDistance)
				prot.Player = player
				prot.Player.Score = player.Score
				if !snake.Alive {
					prot.Job = "dead"
				}
			}
			conn.WriteJSON(prot)
		} else {
			m.RemoveClient(conn)
		}
		return true
	})
	// }
	// fmt.Print("\033[H\033[2J")
	// m.Game.Print()
}

func (m *Master) Leaderboard() []*SimpleSnake {
	players := []*SimpleSnake{}
	m.Clients.Range(func(key, value any) bool {
		// conn, ok := key.(*websocket.Conn)
		// if !ok {
		// 	return true
		// }
		player, ok := value.(*Player)
		if !ok {
			return true
		}
		if player != nil && player.Snake != nil && player.Snake.Alive {
			player.Update()
			s := &SimpleSnake{
				Name:  player.Name,
				Score: *player.Score,
			}
			players = append(players, s)
		}
		return true
	})
	// for _, player := range m.Clients {
	// }
	sort.Slice(players, func(i, j int) bool {
		return players[i].Score > players[j].Score
	})
	return players
}
