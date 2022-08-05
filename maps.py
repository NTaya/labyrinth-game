import numpy as np
import copy
from menu import Menu
from util import COLORS

FLOOR_SIZE_X = 8
FLOOR_SIZE_Y = 8


class FloorMap:
    def __init__(self):
        """
        Directions (of player sight):
            n = north,
            e = east,
            w = west,
            s = south
        """
        self.map = self.generate_map()
        self.curr_room = 0
        self.update_curr_position()
        if self.curr_position_x == 0:  # west-most room
            self.direction = "east"
        elif self.curr_position_x == FLOOR_SIZE_X - 1:  # east-most room
            self.direction = "west"
        elif self.curr_position_y == 0:  # north-most room
            self.direction = "south"
        else:
            self.direction = "north"

    def update_curr_position(self):
        self.curr_position = [x[0] for x in np.where(self.map == self.curr_room)]
        self.curr_position_x = self.curr_position[1]
        self.curr_position_y = self.curr_position[0]
        return self.curr_position

    def generate_map(self):
        floor_map = np.arange(FLOOR_SIZE_X * FLOOR_SIZE_Y)
        np.random.shuffle(floor_map)
        floor_map = np.reshape(floor_map, (FLOOR_SIZE_X, FLOOR_SIZE_Y))
        return floor_map

    def draw_map(self, as_player_sees=False):
        text = ""
        if as_player_sees:
            if self.direction == "north":
                temp_map = self.map
            if self.direction == "west":
                temp_map = np.rot90(self.map, 3)
            if self.direction == "south":
                temp_map = np.rot90(self.map, 2)
            if self.direction == "east":
                temp_map = np.rot90(self.map)
        else:
            temp_map = self.map

        for i in temp_map:
            for j in i:
                if j == 0:
                    # unformatted_text = COLORS["green"] + str(j) + COLORS["reset"]
                    text += f'{COLORS["green"]}{j: 3}{COLORS["reset"]}'
                elif j == self.curr_room:
                    # unformatted_text = COLORS["blue"] + str(j) + COLORS["reset"]
                    text += f'{COLORS["blue"]}{j: 3}{COLORS["reset"]}'
                else:
                    text += f"{j: 3}"
            text += "\n"
        return text

    class Room:
        def __init__(self, room_id, floor_instance, room_num=0):
            self.floor_instance = floor_instance
            self.room_id = room_id
            self.position = [x[0] for x in np.where(self.floor_instance.map == room_id)]
            self.position_x = self.position[1]
            self.position_y = self.position[0]
            self.relative_pos = {
                "left": None,
                "right": None,
                "front": None,
                "back": None,
            }

            is_on_edge = {
                "west": self.position_x == 0,
                "east": self.position_x == FLOOR_SIZE_X - 1,
                "north": self.position_y == 0,
                "south": self.position_y == FLOOR_SIZE_Y - 1,
            }
            self.skip = {
                "west": False,
                "east": False,
                "north": False,
                "south": False,
            }

            self.room_num = room_num
            if not room_num:
                self.room_num = 4
                for i in is_on_edge:
                    if is_on_edge[i]:
                        self.skip[i] = True
                        others = {j: is_on_edge[j] for j in is_on_edge if j != i}
                        for j in others:
                            # double time on edge
                            if is_on_edge[j]:
                                self.skip[j] = True
                                self.floor_instance.room_num = 2
                                break
                            # once on edge
                            self.floor_instance.room_num = 3
                        break

            self.adj_rooms = {
                "west": None,
                "east": None,
                "north": None,
                "south": None,
            }
            if not self.skip["west"]:
                self.adj_rooms["west"] = self.floor_instance.map[
                    self.position_y, self.position_x - 1
                ]
            if not self.skip["east"]:
                self.adj_rooms["east"] = self.floor_instance.map[
                    self.position_y, self.position_x + 1
                ]
            if not self.skip["north"]:
                self.adj_rooms["north"] = self.floor_instance.map[
                    self.position_y - 1, self.position_x
                ]
            if not self.skip["south"]:
                self.adj_rooms["south"] = self.floor_instance.map[
                    self.position_y + 1, self.position_x
                ]

            self.relative_pos = self.get_relative_pos()
            # return self

        def get_relative_pos(self):
            # map_copy = copy.copy(self.floor_instance.map)
            if self.floor_instance.direction == "north":
                mapping = {
                    "left": "west",
                    "right": "east",
                    "front": "north",
                    "back": "south",
                }
                for i in self.relative_pos:
                    self.relative_pos[i] = self.adj_rooms[mapping[i]]
            elif self.floor_instance.direction == "south":
                mapping = {
                    "left": "east",
                    "right": "west",
                    "front": "south",
                    "back": "north",
                }
                for i in self.relative_pos:
                    self.relative_pos[i] = self.adj_rooms[mapping[i]]
            elif self.floor_instance.direction == "west":
                mapping = {
                    "left": "south",
                    "right": "north",
                    "front": "west",
                    "back": "east",
                }
                for i in self.relative_pos:
                    self.relative_pos[i] = self.adj_rooms[mapping[i]]
            else:
                mapping = {
                    "left": "north",
                    "right": "south",
                    "front": "east",
                    "back": "west",
                }
                for i in self.relative_pos:
                    self.relative_pos[i] = self.adj_rooms[mapping[i]]
            return self.relative_pos

        def move_left(self):
            direction_map = {
                "west": "south",
                "east": "north",
                "north": "west",
                "south": "east",
            }
            self.floor_instance.direction = direction_map[self.floor_instance.direction]
            if self.skip[self.floor_instance.direction] == True:
                # raise ValueError
                print("Ineligible direction")
                return self
            self.floor_instance.curr_room = self.relative_pos["left"]
            self.floor_instance.update_curr_position()
            return self.floor_instance.Room(
                self.floor_instance.curr_room, self.floor_instance
            )

        def move_right(self):
            direction_map = {
                "west": "north",
                "east": "south",
                "north": "east",
                "south": "west",
            }
            self.floor_instance.direction = direction_map[self.floor_instance.direction]
            if self.skip[self.floor_instance.direction] == True:
                # raise ValueError
                print("Ineligible direction")
                return self
            self.floor_instance.curr_room = self.relative_pos["right"]
            self.floor_instance.update_curr_position()
            return self.floor_instance.Room(
                self.floor_instance.curr_room, self.floor_instance
            )

        def move_forward(self):
            direction_map = {
                "west": "west",
                "east": "east",
                "north": "north",
                "south": "south",
            }
            self.floor_instance.direction = direction_map[self.floor_instance.direction]
            if self.skip[self.floor_instance.direction] == True:
                # raise ValueError
                print("Ineligible direction")
                return self
            self.floor_instance.curr_room = self.relative_pos["front"]
            self.floor_instance.update_curr_position()
            return self.floor_instance.Room(
                self.floor_instance.curr_room, self.floor_instance
            )

        def move_back(self):
            direction_map = {
                "west": "east",
                "east": "west",
                "north": "south",
                "south": "north",
            }
            self.floor_instance.direction = direction_map[self.floor_instance.direction]
            if self.skip[self.floor_instance.direction] == True:
                # raise ValueError
                print("Ineligible direction")
                return self
            self.floor_instance.curr_room = self.relative_pos["back"]
            self.floor_instance.update_curr_position()
            return self.floor_instance.Room(
                self.floor_instance.curr_room, self.floor_instance
            )


f = FloorMap()
r = f.Room(0, f)


def map_playground():
    print(f.draw_map(as_player_sees=True))

    def wrapped_move_left():
        global r
        r = r.move_left()
        map_playground()

    def wrapped_move_right():
        global r
        r = r.move_right()
        map_playground()

    def wrapped_move_forward():
        global r
        r = r.move_forward()
        map_playground()

    def wrapped_move_back():
        global r
        r = r.move_back()
        map_playground()

    options = {
        "← move_left ←": wrapped_move_left,
        "→ move_right →": wrapped_move_right,
        "↑ move_forward ↑": wrapped_move_forward,
        "↓ move_back ↓": wrapped_move_back,
    }

    text = ""

    Menu(text, options)
