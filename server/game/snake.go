package game

import (
	"fmt"
	"g/helpers"
)

func (s *Snake) ToFood() {
	if !s.Alive {
		for element := s.Body.Front(); element != nil; element = element.Next() {
			body, ok := element.Value.(*Snakebody)
			if ok {
				randval := helpers.RandomInt(0, 10)
				if randval < 8 {
					body.ToFood()
				} else {
					body.ToEmpty()
				}
			}
		}
	}
}

func (s *Snake) CreateBody(x int, y int) *Snakebody {
	b := &Snakebody{
		X:     x,
		Y:     y,
		Snake: s,
		field: s.field,
	}
	s.Body.PushFront(b)
	s.field.Set(x, y, 2)
	return b
}

func (s *Snake) Move() {
	s.UpdatePosition()
	s.SingleMove()
	for element := s.Body.Front(); element != nil; element = element.Next() {
		body, ok := element.Value.(*Snakebody)
		if ok {
			body.Persist()
		}
	}
}
func (s *Snake) SingleMove() {
	if s.Alive {
		lastelement := s.Body.Back()
		lastbody, ok := lastelement.Value.(*Snakebody)
		if ok {
			s.field.Set(lastbody.X, lastbody.Y, 0)
			lastbody.X = s.X
			lastbody.Y = s.Y
			s.field.Set(s.X, s.Y, 2)
			s.Body.MoveToFront(lastelement)
		}
	}
}

func (s *Snake) UpdatePosition() {
	if s.Alive {
		s.CurrentDirection = s.Direction
		x := s.X
		y := s.Y
		if s.CurrentDirection == 0 {
			y -= 1
		}
		if s.CurrentDirection == 1 {
			y += 1
		}
		if s.CurrentDirection == 2 {
			x -= 1
		}
		if s.CurrentDirection == 3 {
			x += 1
		}
		if s.field.DeadlyCollision(x, y) {
			s.Alive = false
			fmt.Println("Collision")
		} else {
			if s.field.FoodCollision(x, y) {
				rand := helpers.RandomInt(0, 10)
				s.CreateBody(x, y)
				s.Score += 1
				if rand < 3 {
					for i := 0; i < 10; i++ {
						X := helpers.RandomInt(0, fieldsize)
						Y := helpers.RandomInt(0, fieldsize)
						if s.field.IsEmpty(X, Y) {
							s.field.Set(X, Y, 1)
							break
						}
					}
				}
			}
			s.X = x
			s.Y = y
		}
	}
}

func (s *Snake) SetDirection(direction int) {
	if direction >= 0 && direction <= 3 {
		if s.CurrentDirection == 0 && direction != 1 || s.CurrentDirection == 1 && direction != 0 || s.CurrentDirection == 2 && direction != 3 || s.CurrentDirection == 3 && direction != 2 {
			s.Direction = direction
		}
	}
}
