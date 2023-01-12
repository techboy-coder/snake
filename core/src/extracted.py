import random
import numba as nb
from numba import njit
import numpy as np


# ========== BaseGame ==========


@njit
def obs_v1(distance, fields, direction):
    rowlength = 2 * distance + 1
    dirvector = np.full(shape=(rowlength,), fill_value=direction)
    obs = np.vstack([fields, dirvector])
    return obs


@njit
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
