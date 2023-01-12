package helpers

import (
	"math/rand"

	gonanoid "github.com/matoous/go-nanoid/v2"
)

func ID() string {
	id, _ := gonanoid.New()
	return id
}

func RandomInt(min, max int) int {
	return min + rand.Intn(max-min)
}

func Increment() func() int {
	i := 0
	return func() int {
		i += 1
		return i
	}
}
