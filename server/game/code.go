package game

import (
	"container/list"
	"g/helpers"
	"sync"
)

var snakelength int = 1

var fieldsize int = 100

// var fieldsize int = 30
var fieldbuffer int = 10
var fooditems int = 300

func matrix(n int) [][]int {
	m := make([][]int, n)
	for i := range m {
		m[i] = make([]int, n)
	}
	return m
}

type Playingfield struct {
	Size   int
	field  [][]int
	Snakes []*Snake
	mu     *sync.Mutex
}

func (f *Playingfield) NewSnake() *Snake {
	id := helpers.ID()
	direction := helpers.RandomInt(0, 3)
	X := helpers.RandomInt(fieldbuffer, fieldsize-fieldbuffer)
	Y := helpers.RandomInt(fieldbuffer, fieldsize-fieldbuffer)
	body := list.New()
	s := &Snake{
		ID:        id,
		Direction: direction,
		X:         X,
		Y:         Y,
		Body:      body,
		field:     f,
		Alive:     true,
	}
	for i := 0; i < snakelength; i++ {
		s.CreateBody(s.X, s.Y)
	}
	for i := 0; i < snakelength; i++ {
		s.Move()
	}
	f.Snakes = append(f.Snakes, s)
	return s
}

type Snakebody struct {
	X, Y  int
	Snake *Snake
	field *Playingfield
}

func (sb *Snakebody) ToFood() {
	sb.field.Set(sb.X, sb.Y, 1)
}
func (sb *Snakebody) ToEmpty() {
	sb.field.Set(sb.X, sb.Y, 0)
}

func (sb *Snakebody) Persist() {
	sb.field.Set(sb.X, sb.Y, 2)
}

type Snake struct {
	ID string
	// up = 0, down = 1, left = 2, right = 3
	Direction        int
	CurrentDirection int
	X, Y             int
	Body             *list.List
	field            *Playingfield
	Alive            bool
	Score            int
}

func (f *Playingfield) DeadlyCollision(x, y int) bool {
	coll := f.IsBody(x, y)
	if !f.InField(x, y) {
		coll = true
	}
	return coll
}
func (f *Playingfield) FoodCollision(x, y int) bool {
	return f.IsFood(x, y)
}

func (f *Playingfield) InField(x, y int) bool {
	f.mu.Lock()
	if x < 0 || x >= f.Size || y < 0 || y >= f.Size {
		f.mu.Unlock()
		return false
	}
	f.mu.Unlock()
	return true
}
