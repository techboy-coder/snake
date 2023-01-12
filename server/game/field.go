package game

import (
	"fmt"
	"g/helpers"
	"strings"
	"sync"
)

func (f *Playingfield) UpdatePositions() {
	for _, snake := range f.Snakes {
		snake.Move()
	}
}

func (f *Playingfield) UpdateSnakes() {
	ok := []*Snake{}
	for _, snake := range f.Snakes {
		if snake != nil {

			if snake.Alive {
				snake.Move()
				ok = append(ok, snake)
			} else {
				snake.ToFood()
				// f.Snakes[i] = nil
			}
		}
	}
	f.Snakes = ok
}
func (f *Playingfield) Update() {
	// f.UpdatePositions()
	f.UpdateSnakes()
}

func NewField() *Playingfield {
	p := &Playingfield{
		Size:  fieldsize,
		field: matrix(fieldsize),
		mu:    &sync.Mutex{},
	}
	for i := 0; i < fooditems; i++ {
		X := helpers.RandomInt(0, fieldsize)
		Y := helpers.RandomInt(0, fieldsize)
		p.Set(X, Y, 1)
	}
	return p
}

func (f *Playingfield) Set(x, y, i int) bool {
	if f.InField(x, y) {
		f.field[x][y] = i
		return true
	}
	return false
}

func (f *Playingfield) IsEmpty(x, y int) bool {
	if !f.InField(x, y) {
		return false
	}
	return f.field[x][y] == 0
}

func (f *Playingfield) IsFood(x, y int) bool {
	if !f.InField(x, y) {
		return false
	}
	return f.field[x][y] == 1
}

func (f *Playingfield) IsBody(x, y int) bool {
	if !f.InField(x, y) {
		return false
	}
	return f.field[x][y] == 2
}

func (f *Playingfield) IsWall(x, y int) bool {
	return !f.InField(x, y)
}

func (f *Playingfield) Get(x, y int) int {
	if f.IsWall(x, y) {
		return -1
	}
	if f.IsEmpty(x, y) {
		return 0
	}
	if f.IsFood(x, y) {
		return 1
	}
	if f.IsBody(x, y) {
		return 2
	}
	return -1
}

func (f *Playingfield) Print() {
	// Make border around grid
	fmt.Println("+" + strings.Repeat("-", f.Size*2) + "+")
	for i := 0; i < f.Size; i++ {
		fmt.Print("|")
		for j := 0; j < f.Size; j++ {
			// "  " = empty, " f" = food, " °" = snake, " h" = snake head, "  " = nil
			// Check if item is nil
			if f.IsEmpty(i, j) {
				fmt.Print("  ")
			}
			if f.IsFood(i, j) {
				fmt.Print(" f")
			}
			if f.IsBody(i, j) {
				fmt.Print(" °")
			}
			if f.IsWall(i, j) {
				fmt.Print("++")
			}
		}
		fmt.Print("|\n")
	}
	fmt.Println("+" + strings.Repeat("-", f.Size*2) + "+")
	fmt.Println("Alive Snakes: ", len(f.Snakes))
}

func (f Playingfield) CoordinatesAround(x, y, dist int) [][2]int {
	fields := make([][2]int, 0)
	for i := -dist; i <= dist; i++ {
		for j := -dist; j <= dist; j++ {
			fields = append(fields, [2]int{x + i, y + j})
		}
	}
	// ==> If you want wrapping uncomment stuff below. by @shivramsambhus
	// for i := 0; i < len(fields); i++ {
	// 	point := fields[i]
	// 	px, py := point[0], point[1]
	// 	d := f.size
	// 	h := d / 2
	// 	px = x - px
	// 	py = y - py
	// 	if px < -h {
	// 		px = d + px
	// 	} else if px > h {
	// 		px = d - px
	// 	}
	// 	if py < -h {
	// 		py = d + py
	// 	} else if py > h {
	// 		py = d - py
	// 	}
	// 	fields[i] = [2]int{px, py}
	// }
	return fields
}

func (f Playingfield) FieldsAround(x, y, dist int) [][]int {
	cords := f.CoordinatesAround(x, y, dist)
	fields := make([]int, 0)
	for _, coord := range cords {
		fields = append(fields, f.Get(coord[0], coord[1]))
	}
	len := 2*dist + 1
	out := matrix(len)
	i := 0
	for ix, row := range out {
		for iy := range row {
			out[ix][iy] = fields[i]
			i++
		}
	}
	return out
}
