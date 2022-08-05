"""
    def init_room(self, room_id, room_num=0):
        self.room_id = room_id
        self.room_position = [x[0] for x in np.where(self.map == room_id)]
        self.room_position_x = self.room_position[1]
        self.room_position_y = self.room_position[0]
        self.relative_pos = {
            "left": None,
            "right": None,
            "front": None,
            "back": None,
        }

        is_on_edge = {
            "west": self.room_position_x == 0,
            "east": self.room_position_x == FLOOR_SIZE_X - 1,
            "north": self.room_position_y == 0,
            "south": self.room_position_y == FLOOR_SIZE_Y - 1,
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
                            self.room_num = 2
                            break
                        # once on edge
                        self.room_num = 3
                    break

        self.adj_rooms = {
            "west": None,
            "east": None,
            "north": None,
            "south": None,
        }
        if not self.skip["west"]:
            self.adj_rooms["west"] = self.map[
                self.room_position_y, self.room_position_x - 1
            ]
        if not self.skip["east"]:
            self.adj_rooms["east"] = self.map[
                self.room_position_y, self.room_position_x + 1
            ]
        if not self.skip["north"]:
            self.adj_rooms["north"] = self.map[
                self.room_position_y - 1, self.room_position_x
            ]
        if not self.skip["south"]:
            self.adj_rooms["south"] = self.map[
                self.room_position_y + 1, self.room_position_x
            ]

        self.relative_pos = self.get_relative_pos()
        return self

    def get_relative_pos(self):
        # map_copy = copy.copy(self.map)
        if self.direction == "north":
            mapping = {
                "left": "west",
                "right": "east",
                "front": "north",
                "back": "south",
            }
            for i in self.relative_pos:
                self.relative_pos[i] = self.adj_rooms[mapping[i]]
        elif self.direction == "south":
            mapping = {
                "left": "east",
                "right": "west",
                "front": "south",
                "back": "north",
            }
            for i in self.relative_pos:
                self.relative_pos[i] = self.adj_rooms[mapping[i]]
        elif self.direction == "west":
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
        self.direction = direction_map[self.direction]
        if self.skip[self.direction] == True:
            # raise ValueError
            print("Ineligible direction")
            return
        self.curr_room = self.relative_pos["left"]
        print(self.relative_pos)
        self.update_curr_position()
        """
