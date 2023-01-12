from collections import deque
import random
from typing import List
import gym
from gym import spaces
import numpy as np
from . import extracted

# Counter func returnes n+1 every time it is called
def Count(n=0):
    while True:
        yield n
        n += 1


class BaseGame:
    def __init__(self, fieldsize, fieldBuffer, foodItems):
        self.size = fieldsize
        self._fieldBuffer = fieldBuffer
        self._foodItems = foodItems
        self.field = np.zeros(shape=(fieldsize, fieldsize))
        self.snakes = {}
        for _ in range(foodItems):
            self._addFoodToField()

    def _updateSnakes(self):
        ok = {}
        for key, snake in self.snakes.items():
            if snake.alive:
                self.snakes[key].move()
                ok[key] = snake
            else:
                snake._toFood()
        self.snakes = ok

    def update(self):
        self._updateSnakes()

    def getEmptyFieldCertain(self, buffer=0):
        x = random.randint(buffer, self.size - buffer)
        y = random.randint(buffer, self.size - buffer)
        for _ in range(10):
            x = random.randint(buffer, self.size - buffer)
            y = random.randint(buffer, self.size - buffer)
            f = self._getField(x, y)
            if f == 0:
                break
        return x, y

    def getEmptyFieldWithEmptyDistance(self, dist):
        tries = 10
        # This function generates random x,y coordinates and checks if the field and all fields around it are empty in distance dist (using self.FieldsAround) are empty. If not, it tries again tries times. If all tries fail, it returns self.getEmptyFieldUncertain()
        x, y = self.getEmptyFieldUncertain()
        for _ in range(tries):
            fields = self.fieldsAround(x, y, dist)
            if np.all(fields == 0):
                return x, y
            x, y = self.getEmptyFieldUncertain()

        return x, y

    def getEmptyFieldUncertain(self, buffer=0):
        for _ in range(10):
            x = random.randint(buffer, self.size - buffer)
            y = random.randint(buffer, self.size - buffer)
            f = self._getField(x, y)
            if f == 0:
                return x, y
        return -1, -1

    def _inField(self, x, y) -> bool:
        if x < 0 or x >= self.size or y < 0 or y >= self.size:
            return False
        else:
            return True

    def _isEmpty(self, x, y) -> bool:
        if self._isWall(x, y):
            return False
        return self.field[x][y] == 0

    def _isFood(self, x, y) -> bool:
        if self._isWall(x, y):
            return False
        return self.field[x][y] == 1

    def _isBody(self, x, y) -> bool:
        if self._isWall(x, y):
            return False
        return self.field[x][y] == 2

    def _isWall(self, x, y) -> bool:
        return not self._inField(x, y)

    def _getField(self, x, y):
        if self._isWall(x, y):
            return -1
        if self._isEmpty(x, y):
            return 0
        if self._isFood(x, y):
            return 1
        if self._isBody(x, y):
            return 2

        print("hmm?")
        return 0

    def _setField(self, x, y, i) -> bool:
        if self._inField(x, y):
            self.field[x][y] = i
            return True
        return False

    def _addFoodToField(self):
        x, y = self.getEmptyFieldUncertain()
        if self._inField(x, y):
            self._setField(x, y, 1)

    def Print(self):
        print("+", "-" * (self.size * 2 - 2), "+")
        for i in range(self.size):
            print("|", end="")
            for j in range(self.size):
                if self._isEmpty(i, j):
                    print("  ", end="")
                if self._isFood(i, j):
                    print(" f", end="")
                if self._isBody(i, j):
                    print(" °", end="")
                if self._isWall(i, j):
                    print("  ", end="")
            print("|")
        print("+", "-" * (self.size * 2 - 2), "+")
        print("Alive snakes: ", len(self.snakes))

    def _coordinatesAround(self, x, y, dist):
        fields = []
        for i in range(-dist, dist + 1):
            for j in range(-dist, dist + 1):
                fields.append([x + i, y + j])
        return fields

    def fieldsAround(self, x, y, dist):
        cords = self._coordinatesAround(x, y, dist)
        fields = []
        for c in cords:
            fields.append(self._getField(c[0], c[1]))
        len2d = 2 * dist + 1
        out = np.full(shape=(len2d, len2d), fill_value=-1)
        i = 0
        for ix in range(len2d):
            for iy in range(len2d):
                out[ix][iy] = fields[i]
                i += 1

        return out

    def newSnake(self):
        snake = Snake(field=self)
        # self.snakes.append(snake)
        self.snakes[snake.id] = snake
        return snake


class Snake:
    def __init__(self, field: BaseGame):
        self.field: BaseGame = field
        self.direction = random.randint(0, 3)
        self._currentDirection = self.direction
        self.x, self.y = field.getEmptyFieldWithEmptyDistance(dist=1)
        self.body = deque([])
        self.alive = True
        self.score = 0
        self.id = Count()
        # Create 1 body
        self._createBody(self.x, self.y)

    def move(self):
        self._updatePosition()
        self._singleMove()
        # Persist, just in case
        for body in self.body:
            self.field._setField(body[0], body[1], 2)

    def _singleMove(self):
        if self.alive:
            lastElement = self.body.pop()
            self.field._setField(lastElement[0], lastElement[1], 0)
            lastElement[0] = self.x
            lastElement[1] = self.y
            self.field._setField(self.x, self.y, 2)
            self.body.appendleft(lastElement)

    def _createBody(self, x, y):
        self.body.appendleft([x, y])
        self.field._setField(x, y, 2)

    def _updatePosition(self):
        if self.alive:
            self._currentDirection = int(self.direction)
            x = self.x
            y = self.y
            if self._currentDirection == 0:
                y -= 1
            if self._currentDirection == 1:
                y += 1
            elif self._currentDirection == 2:
                x -= 1
            elif self._currentDirection == 3:
                x += 1
            self.x = x
            self.y = y
            if self.field._isBody(x, y) or self.field._isWall(x, y):
                self.alive = False

            else:
                if self.field._isFood(x, y):
                    rand = random.randint(0, 10)
                    self._createBody(x, y)
                    self.score += 1
                    # 30% Chance
                    if rand < 3:
                        self.field._addFoodToField()

    def _setDirection(self, direction):
        # In range
        if direction >= 0 and direction <= 3:
            # Not opposite
            if (
                self._currentDirection == 0
                and direction != 1
                or self._currentDirection == 1
                and direction != 0
                or self._currentDirection == 2
                and direction != 3
                or self._currentDirection == 3
                and direction != 2
            ):
                self.direction = direction

    def _toFood(self):
        if not self.alive:
            for body in self.body:
                rand = random.randint(0, 10)
                # 60% chance
                if rand < 10:
                    self.field._setField(body[0], body[1], 1)
                else:
                    self.field._setField(body[0], body[1], 0)


class Game:
    def __init__(self, fieldsize, fieldBuffer, foodItems):
        self.base = BaseGame(fieldsize, fieldBuffer, foodItems)

    def obs_v1(self, distance, fields, direction):
        obs: np.ndarray = extracted.obs_v1(distance, fields, direction)
        obs = obs.astype(int)
        return obs

    def obs_v2(self, obs: np.ndarray, direction: int, distance: int):
        obs: np.ndarray = extracted.obs_v2(obs, direction, distance)
        obs = obs.astype(int)
        return obs

    def tick(self):
        self.base.update()


class GameManager:
    def __init__(self, fieldsize: int, fooditems: int):
        self.games = {}
        self.fieldsize = fieldsize
        self.fooditems = fooditems

    def newGame(self):
        # Make a new game using a new id with fieldsize and fooditems
        id_ = Count()
        self.games[id_] = Game(self.fieldsize, 5, self.fooditems)
        # return game id
        return id_

    def getGameIds(self):
        return self.games.keys()

    def getGame(self, id_):
        return self.games[id_]

    def getRandomGame(self):
        return random.choice(list(self.games.values()))

    def getRandomGameID(self):
        return random.choice(list(self.games.keys()))


class env_v1(gym.Env):
    def __init__(
        self,
        name,
        manager: GameManager,
        game_id: int,
        others: List[List],
        viewdistance=10,
        admin=False,
    ):
        super(env_v1, self).__init__()
        self.name = name
        self.viewdistance = viewdistance

        # Self.others is a list of [agent, env(not admin with same game_id), obs]
        self.others = others

        self.singledims = ((2 * viewdistance + 1 + 1), (2 * viewdistance + 1))
        self.dims = (2, (2 * viewdistance + 1 + 1), (2 * viewdistance + 1))
        self.action_space = spaces.Discrete(4)
        self.observation_space = spaces.Box(-1, 4, shape=self.dims, dtype=int)
        self.obs = np.zeros(shape=self.dims).astype(dtype=int)
        self.old_obs = np.zeros(shape=self.singledims).astype(dtype=int)

        self.manager = manager
        self.game_id = game_id
        self.game: Game = self.manager.getGame(self.game_id)
        self.key = self.game.base.newSnake().id

        self.score = 0
        self.dead = False
        self.delta = 0
        self.admin = admin

    def step(self, action):
        # Set action and update game if admin
        self.game = self.manager.getGame(self.game_id)
        self.game.base.snakes[self.key]._setDirection(action)

        if self.admin:
            self.game.tick()

        for other in self.others:
            agent = other[0]
            env = other[1]
            obs = other[2]

            agent_action, _ = agent.predict(obs, deterministic=True)
            agent_obs, _, done, _ = env.step(agent_action)
            if done:
                agent_obs = env.reset()
            other[2] = agent_obs

        # Calculate reward
        snake = self.game.base.snakes[self.key]
        self.delta = (snake.score - self.score) * 10 + self.delta * 0.2 - 0.25
        self.score = snake.score
        reward = self.delta
        self.dead = not snake.alive
        if self.dead:
            reward = -10

        # Get observation
        snake = self.game.base.snakes[self.key]
        x, y = snake.x, snake.y
        direction = snake._currentDirection
        view = self.game.base.fieldsAround(x, y, self.viewdistance)
        old = self.old_obs
        obs = self.game.viewToObs(self.viewdistance, view, direction)
        # Frame stack
        self.obs = np.array([obs, old])
        self.old_obs = obs

        # Return observation, reward, done, info
        return self.obs, reward, self.dead, {"x": x, "y": y, "direction": direction}

    def close(self):
        pass

    def reset(self):
        self.score = 0
        self.delta = 0
        self.dead = False
        self.obs = np.zeros(shape=self.dims).astype(dtype=int)
        self.old_obs = np.zeros(shape=self.singledims).astype(dtype=int)
        self.game: Game = self.manager.getGame(self.game_id)
        self.key = self.game.base.newSnake().id
        return self.obs


class env_v2(gym.Env):
    def __init__(
        self,
        name,
        manager: GameManager,
        game_id: int,
        others: List[List],
        viewdistance=10,
        admin=False,
    ):
        super(env_v2, self).__init__()
        # Environment parameters
        self.name = name
        self.viewdistance = viewdistance
        self.others = others

        # Observation space
        # Single frame has 9 elements: 8x (for 8 directions) [element type, distance to element] + [direction, direction]
        self.frame_dims = (9, 2)
        self.frame_stacked_dims = (2, 9, 2)
        self.action_space = spaces.Discrete(4)
        self.observation_space = spaces.Box(
            -1, self.viewdistance + 1, shape=self.frame_stacked_dims, dtype=int
        )
        self.obs = np.zeros(shape=self.frame_stacked_dims).astype(dtype=int)
        self.old_obs = np.zeros(shape=self.frame_dims).astype(dtype=int)

        # Game parameters
        self.manager = manager
        self.game_id = game_id
        self.game: Game = self.manager.getGame(self.game_id)
        self.key = self.game.base.newSnake().id

        self.score = 0
        self.dead = False
        self.delta = 0
        self.admin = admin

    def step(self, action):
        # Set action and update game if admin
        self.game: Game = self.manager.getGame(self.game_id)
        self.game.base.snakes[self.key]._setDirection(action)

        if self.admin:
            self.game.tick()

        for other in self.others:
            agent = other[0]
            env = other[1]
            obs = other[2]

            agent_action, _ = agent.predict(obs, deterministic=True)
            agent_obs, _, done, _ = env.step(agent_action)
            if done:
                agent_obs = env.reset()
            other[2] = agent_obs

        # Calculate reward
        snake = self.game.base.snakes[self.key]
        self.delta = (snake.score - self.score) * 10 + self.delta * 0.2 - 0.25
        self.score = snake.score
        reward = self.delta
        self.dead = not snake.alive
        if self.dead:
            reward = -10

        # Get observation
        snake = self.game.base.snakes[self.key]
        x, y = snake.x, snake.y
        direction = snake._currentDirection
        view = self.game.base.fieldsAround(x, y, self.viewdistance)
        old = self.old_obs
        obs = self.game.obs_v2(view, direction, self.viewdistance)
        # Frame stack
        self.obs = np.array([obs, old])
        self.old_obs = obs
        self.action = action

        # Return observation, reward, done, info
        return self.obs, reward, self.dead, {"x": x, "y": y, "direction": direction}

    def close(self):
        pass

    def reset(self):
        self.score = 0
        self.delta = 0
        self.dead = False
        self.obs = np.zeros(shape=self.frame_stacked_dims).astype(dtype=int)
        self.old_obs = np.zeros(shape=self.frame_dims).astype(dtype=int)
        self.game: Game = self.manager.getGame(self.game_id)
        self.key = self.game.base.newSnake().id
        return self.obs
