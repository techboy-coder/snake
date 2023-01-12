import os
from multiprocessing import Process
import threading
import websocket
import numpy as np
import time
import json
import nanoid
from src.main import env_v1, env_v2, GameManager, Game
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize
from stable_baselines3 import DQN

connection_url = 'ws://localhost:8080/ws'
view_distance = 10
name = "bot #"

def obs_v2(obs: np.ndarray, direction: int, distance: int):
    rowlength = 2 * distance + 1
    dirvector = np.full(shape=(rowlength,), fill_value=direction)

    # Given a observation for a single frame, make arrays for 8 direction from center
    center_x = distance
    center_y = distance

    # Reverse order where needed so that snake head is always at left side
    left_side_arr = obs[center_y][:center_x][::-1]
    right_side_arr = obs[center_y][center_x + 1 :]
    # up is column above center
    up_side_arr = obs[:center_y, center_x][::-1]
    # down is column below center
    down_side_arr = obs[center_y + 1 :, center_x]
    # Now get the diagonals

    # top_left_to_bottom_right = obs.diagonal()
    # top_right_to_bottom_left = np.fliplr(obs).diagonal()
    top_left_to_bottom_right = np.diag(obs)
    top_right_to_bottom_left = np.diag(np.fliplr(obs))
    # Now split into 8 directions
    top_left_side_arr = top_left_to_bottom_right[:center_y][::-1]
    bottom_right_side_arr = top_left_to_bottom_right[center_y + 1 :]
    top_right_side_arr = top_right_to_bottom_left[:center_y][::-1]
    bottom_left_side_arr = top_right_to_bottom_left[center_y + 1 :]

    # [element, distance]
    left_side = [0, distance]
    right_side = [0, distance]
    up_side = [0, distance]
    down_side = [0, distance]
    top_left_side = [0, distance]
    bottom_right_side = [0, distance]
    top_right_side = [0, distance]
    bottom_left_side = [0, distance]
    # Now check distance to non zero element from left to right. If only zeros then set to length of array. Add element type to array as first element and distance to that element as second element
    for i in range(len(left_side_arr)):
        if left_side_arr[i] != 0:
            left_side = [left_side_arr[i], i + 1]
            break
    for i in range(len(right_side_arr)):
        if right_side_arr[i] != 0:
            right_side = [right_side_arr[i], i + 1]
            break
    for i in range(len(up_side_arr)):
        if up_side_arr[i] != 0:
            up_side = [up_side_arr[i], i + 1]
            break
    for i in range(len(down_side_arr)):
        if down_side_arr[i] != 0:
            down_side = [down_side_arr[i], i + 1]
            break
    for i in range(len(top_left_side_arr)):
        if top_left_side_arr[i] != 0:
            top_left_side = [top_left_side_arr[i], i + 1]
            break
    for i in range(len(bottom_right_side_arr)):
        if bottom_right_side_arr[i] != 0:
            bottom_right_side = [bottom_right_side_arr[i], i + 1]
            break
    for i in range(len(top_right_side_arr)):
        if top_right_side_arr[i] != 0:
            top_right_side = [top_right_side_arr[i], i + 1]
            break
    for i in range(len(bottom_left_side_arr)):
        if bottom_left_side_arr[i] != 0:
            bottom_left_side = [bottom_left_side_arr[i], i + 1]
            break
    # Now add all the arrays to a list and add direction and return
    return np.array(
        [
            left_side,
            right_side,
            up_side,
            down_side,
            top_left_side,
            bottom_right_side,
            top_right_side,
            bottom_left_side,
            [direction, direction],
        ]
    )

def dictToJson(d):
    return json.dumps(d)
def jsonToDict(j):
    return json.loads(j)

class ProxyEnv:
    def __init__(self) -> None:
        self.fake_games = GameManager(fieldsize=40, fooditems=50)
        id_ = self.fake_games.newGame()
        self.fake_env: env_v2 = env_v2(
            "fake",
            manager = self.fake_games,
            game_id = id_,
            others = [],
            viewdistance=10,
            admin=True,
        )
        self.env = DummyVecEnv([lambda: self.fake_env])
        self.env: VecNormalize = VecNormalize.load(f"./saved/nrom_for_dqn_best.pkl", self.env)
    
    def normalize_obs(self, obs):
        out = self.env.normalize_obs(obs)
        return out

proxy_env = ProxyEnv()

class AI:
    def __init__(self) -> None:
        self.ai = DQN.load(f"./saved/dqn_best", env = proxy_env.env)
    
    def predict(self, obs):
        action, _states = self.ai.predict(obs, deterministic=True)
        action = action[0]
        return action

ai = AI()

# {"Job":"join","Player":{"ViewDistance":200,"Name":"anon"}}
def join_msg(name):
    return dictToJson({
        "Job": "join",
        "Player": {
            "ViewDistance": view_distance,
            "Name": name
        }
    })
# {"Job":"turn","Player":{"Direction":1}}
def turn_msg(direction):
    return dictToJson({
        "Job": "turn",
        "Player": {
            "Direction": direction
        }
    })
# websocket.enableTrace(True)
class WSClient:
    def __init__(self):
        # Create a new client and connect to the server
        self.wsapp = websocket.WebSocketApp(connection_url, on_message=self.on_message, on_open=self.on_open, on_close=self.on_close)
        self.wst = threading.Thread(target=self.wsapp.run_forever)
        self.wst.daemon = True
        self.wst.start()
        conn_timeout = 50
        while not self.wsapp.sock.connected and conn_timeout:
            time.sleep(1)
            conn_timeout -= 1
        
        # Generate a random name for the bot
        self.id = nanoid.generate(size = 4)
        self.name = name + self.id
        self.dead = False
        self.data = {}
        self.current_field_v1 = np.zeros((view_distance * 2 + 1, view_distance * 2 + 1))
        self.current_field_v2 = np.zeros((9,2))
        self.old_field_v2 = np.zeros((9,2))
        self.non_normalized_field = np.zeros((1,2,9,2))
        self.normalized_field = np.zeros((1,2,9,2))
        # Join the game
        if self.wsapp.sock.connected:
            self.join()
            self.t = threading.Thread(target = self.stay_alive)
            self.t.start()
            
    
    def send(self, msg):
        try:
            if not self.dead:
                self.wsapp.send(msg)
        except:
            self.dead = True

    
    def join(self):
        self.send(join_msg(self.name))
    
    def step(self, direction=-1):
        direction = int(ai.predict(self.normalized_field))
        # if direction >= -1 and direction <= 3:
        self.send(turn_msg(direction))
        # msg = dictToJson(msg)
        # self.send(msg)
    
        # return self.data, self.direction, self.score, self.dead

    def stay_alive(self):
        while not self.dead:
            # self.step()
            pass

    def on_open(self, ws):
        ws.send(self.joinMsg())

    def on_message(self, wsappm, msg):
        # msg = {Job: "join|turn|dead|update", Stats: {SnakeAmount: int}, Player: {Direction: int, Score: int, ViewDistance: int, Name: string}, Field: [[int]]}
        msg = jsonToDict(msg)
        # check dead
        if msg["Job"] == "dead":
            self.dead = True
            return
        if msg["Job"] == "update":
            # print("update")
            self.old_field_v2 = self.current_field_v2
            self.current_field_v1 = np.array(msg["Field"])
            self.current_field_v2 = obs_v2(self.current_field_v1, msg["Player"]["Direction"], view_distance)
            self.non_normalized_field = np.array([[self.current_field_v2, self.old_field_v2]])
            self.normalized_field = proxy_env.normalize_obs(self.non_normalized_field)
            self.step()
            # print(self.non_normalized_field.shape)
            # print(self.normalized_field)
            # print(self.normalized_field.shape)
            
        self.data = msg
        # print("Received message: ", msg)
    
    def on_close(self, ws, close_status_code, close_msg):
        self.dead = True
        print("Connection closed")
    
    def close(self):
        self.dead = True
        self.wsapp.close()
        self.t.join()


def client():
    while True:
        print("Starting new client")
        client = WSClient()
        while not client.dead:
            time.sleep(1)
        client.close()
        # check if "./RUN.txt" exists and has "OK" in it
        if not os.path.exists("./RUN.txt"):
            print("STOP")
            break
        with open("./RUN.txt", "r") as f:
            if f.read() != "OK":
                print("STOP")
                break

# def runInParallel(*fns):
#   proc = []
#   for fn in fns:
#     p = Process(target=fn)
#     p.start()
#     proc.append(p)
#   for p in proc:
#     p.join()

# if __name__ == "__main__":
#     number_of_clients = 12
#     print("Starting", number_of_clients, "clients")
#     runInParallel(*[client() for _ in range(number_of_clients)])

if __name__ == "__main__":
    client()