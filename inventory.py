from items import Item, Guidewatch, GeneralAttribute, functional_attributes
from util import COLORS, func_wrapper
from menu import Menu
from numpy import random
import typing


full_items = {
    "sword": "hands",
    "knife": "hands",
    "bow": "hands",
    "handgun": "hands",
    "rifle": "hands",
    "jacket": "jacket",
    "cape": "cape",
    "pants": "pants",
    "boots": "boots",
    "food": "left_pocket",
    "water": "right_pocket",
    "backpack": "backpacks",
    "materia": "materia",
}

reverse_full_items = {
    "hands": GeneralAttribute("sword"),
    "jacket": GeneralAttribute("jacket"),
    "cape": GeneralAttribute("cape"),
    "pants": GeneralAttribute("pants"),
    "boots": GeneralAttribute("boots"),
    "left_pocket": GeneralAttribute("food"),
    "right_pocket": GeneralAttribute("water"),
    "backpack": GeneralAttribute("backpack"),
}


class Inventory:
    def __init__(self):
        self.guidewatch = Guidewatch(0)
        self.items = {
            "hands": COLORS["reset"] + " None",
            "jacket": COLORS["reset"] + " None",
            "cape": COLORS["reset"] + " None",
            "pants": COLORS["reset"] + " None",
            "boots": COLORS["reset"] + " None",
            "left_pocket": COLORS["reset"] + " None",
            "right_pocket": COLORS["reset"] + " None",
            "backpacks": [""],
            "materia": [""],
            # "guidewatch": f"guidewatch [{self.guidewatch.level}]",
        }

    def set_guidewatch_level(self, level):
        self.guidewatch.level = level
        return self

    def show_inventory(self):
        items_list = {}
        for item in self.items:
            if item in forbidden_types:
                item_contents = self.items[item]
                if item_contents != [""]:
                    for inner_item_index in range(len(item_contents)):
                        val = item_contents[inner_item_index]
                        items_list[item] = [None for i in range(len(item_contents))]
                        items_list[item][inner_item_index] = hide_color_if_low_lvl(
                            val, self
                        )
            else:
                val = self.items[item]
                # delete color if the level of guidewatch is insufficient
                items_list[item] = hide_color_if_low_lvl(val, self)
        # print(items_list)
        for key, value in items_list.items():
            if isinstance(value, list):
                print(key, *value)
            else:
                print(key, value)

        text = f"""Guidewatch lvl: {self.guidewatch.level}
Hands: {items_list["hands"]}
Jacket: {items_list["jacket"]}
Cape: {items_list["cape"]}
Pants: {items_list["pants"]}
Boots: {items_list["boots"]}
Food pocket: {items_list["left_pocket"]}
Water pocket: {items_list["right_pocket"]}
Backpacks: {self.items["backpacks"]}
Materia: {self.items["materia"]}
"""
        return text

    def equip_item(self, item):
        """Return the item if equipment failed,
        otherwise return None."""
        if str(item.type_of) == "materia":
            if self.items["materia"] == [""]:
                self.items["materia"].pop(0)
            self.items["materia"].append(item)
            return None

        if str(item.type_of) == "backpack":
            if self.items["backpacks"] == [""]:
                self.items["backpacks"][0] = item
                return None
            elif len(self.items["backpacks"] >= 4):
                print("You can't carry more backpacks!")
                return item
            self.items["backpacks"].append(item)
            return None

        slot = full_items[str(item.type_of)]
        if (
            self.items[slot] != COLORS["reset"] + " None"
            and self.items[slot] != " None"
            and self.items[slot] != "None"
            and self.items[slot] != [""]
        ):
            print(f"Slot for {slot} is full!")
            return item
        self.items[slot] = item
        return None

    def unequip_item(self, item):
        if (
            self.items["backpacks"][0] == ""
            or sum([x.empty_slots for x in self.items["backpacks"]]) == 0
        ):
            print("No suitable backpacks, dropping item.")
            self.drop_item(item)
        else:
            for i in self.items["backpacks"]:
                if i.empty_slots > 0:
                    i.add_item(item)
                    break
        return self

    def drop_item(self, item):
        # TODO: floor integration
        self.items[item] = COLORS["reset"] + " None"
        return item

    def fill(self):
        for item in reverse_full_items:
            if (
                item not in forbidden_types
                and self.items[item] == COLORS["reset"] + " None"
            ):
                type_of = reverse_full_items[item]
                self.equip_item(Item(type_of=type_of))
        if self.items["backpacks"] == [""]:
            self.equip_item(Backpack())

    def empty(self):
        for i in self.items:
            if i in ("backpacks", "materia"):
                self.items[i] = [""]
            if i == "guidewatch":
                continue
            else:
                self.items[i] = COLORS["reset"] + " None"

    # -- Utility functions for item-opening -- #
    def prelim_open_item(item):
        def unequip_item():
            unequip_item(item)
            return

        def drop_item():
            drop_item(item)
            return

        def back():
            return

    def open_item(self, item):
        item.print_description(self.guidewatch.level)
        # if str(item.type_of) == "backpack":
        #     item.open_bag()
        # else:
        #     text = ""
        #     opening_wrapper = func_wrapper(func, val)
        #     options = {
        #         "Unequip Item  ": unequip_item,
        #         "Drop Item  ": drop_item,
        #         "Back  ": back,
        #     }
        #     # item = Item(sort_of="backpack")
        #     while not chosen:
        #         chosen = Menu(text, options)
        #     options[chosen]()
        #     inventory_playground()


class Backpack(Item):
    def __init__(self, name=None, attribute_num=3, attributes=None, slots=8):
        self.name = name
        self.type_of = GeneralAttribute("backpack")
        self.total_slots = slots
        self.empty_slots = slots
        self.items = {}

        self.attribute_num = attribute_num
        if self.attribute_num <= 3:
            self.rarity = "common"
        elif self.attribute_num <= 5:
            self.rarity = "rare"
        elif self.attribute_num <= 6:
            self.rarity = "epic"
        elif self.attribute_num <= 7:
            self.rarity = "legendary"

        if attributes is None:
            self.attributes = random.choice(
                functional_attributes, self.attribute_num, replace=False
            )

        if name is None:
            self.name = self.get_name()

    def show_inventory(self):
        text = ",\n".join([items.keys()])
        return text

    def add_item(self, item: Item):
        if str(item.type_of) == "backpack":
            print("No Bags of Holding!")
            return self
        self.items[item.name] = item
        self.empty_slots -= 1
        return self

    def equip_item(self, item, inventory_instance):
        if not inventory_instance.equip_item(item):  # if equipped successfully
            self.empty_slots += 1
        return self

    def unequip_item(self, item):
        super().drop_item(item)
        self.empty_slots += 1
        return self

    def open_bag(self, item, inventory):
        # item = self
        # Item is as-item representation
        # self is as-inventory representation
        item.print_description(inventory.guidewatch.level)

    def __str__(self):
        return f"{self.name}: {self.total_slots - self.empty_slots}/{self.total_slots}"


def fill_inventory():
    inv.fill()


def empty_inventory():
    inv.empty()


def set_guidewatch_level_to_1():
    inv.guidewatch.level = 1


def set_guidewatch_level_to_100():
    inv.guidewatch.level = 100


def back():
    if type(inv) == Backpack:
        inv = backup_inv
    else:
        pass


# -- util --
def hide_color_if_low_lvl(item_name, inventory):
    return (
        COLORS["reset"] + " " + str(item_name)[5:]
        if inventory.guidewatch.level < 5
        else str(item_name)
    )


inv = Inventory()
# most stuff will have special interactions with these items
forbidden_types = ["backpacks", "backpack", "materia"]


def inventory_playground():
    while True:
        # text = "r: sort by rarity, t: sort by type, y: sort by name; e: equip, u: unequip"
        text = ""
        # responses that don't require special treatment
        options = [
            "Fill Inventory  ",
            "Empty Inventory  ",
            "Set Guidewatch lvl to 1  ",
            "Set Guidewatch level to 100  ",
        ]
        non_variate_responses = {
            "Fill Inventory  ": fill_inventory,
            "Empty Inventory  ": empty_inventory,
            "Set Guidewatch lvl to 1  ": set_guidewatch_level_to_1,
            "Set Guidewatch level to 100  ": set_guidewatch_level_to_100,
        }
        # special responses, need to pass an argument to a func
        answers_to_item = {}
        for item_type, item in inv.items.items():
            answer_text = item
            if item_type not in forbidden_types:
                answer_text = hide_color_if_low_lvl(item, inv)
                if answer_text != COLORS["reset"] + " None":
                    options.append(answer_text)
                    # Friendly reminder:
                    # answer_text = str
                    # item = Item
                    answers_to_item[answer_text] = item
            # elif answer_text != [""]:
            #     full_answer_text = []
            #     for inner_item_index in range(len(item)):
            #         answer_text = hide_color_if_low_lvl(item, inv)
            #         full_answer_text.append(answer_text)
            #     options.append(full_answer_text)
            #     answers_to_item[answer_text] = item[inner_item_index]

        options.extend(
            ["Take a look at Backpacks  ", "Take a look at Materia  ", "Quit  "]
        )
        close_menu = ["Quit  "]

        inv.show_inventory()

        chosen = Menu(text, options).answer

        if chosen in non_variate_responses.keys():
            non_variate_responses[chosen]()

        elif chosen == "Take a look at Backpacks  ":
            # new menu
            if inv.items["backpacks"] == [""]:
                print(COLORS["red"] + "Nothing to look at (yet)!" + COLORS["reset"])
            else:
                while True:
                    answers_to_bag = {}
                    for i in range(len(inv.items["backpacks"])):
                        item = inv.items["backpacks"][i]
                        answer_text = hide_color_if_low_lvl(item, inv)
                        answers_to_bag[answer_text] = inv.items["backpacks"][i]
                    bag_options = list(answers_to_bag.keys())
                    bag_options.append("Close  ")
                    bag_text = ""
                    bag_chosen = Menu(bag_text, bag_options).answer
                    if bag_chosen == "Close  ":
                        break
                    bag = answers_to_bag[bag_chosen]
                    bag.open_bag(bag, inv)

        elif chosen == "Take a look at Materia ":
            # same, new menu
            if inv.items["materia"] == [""]:
                print(COLORS["red"] + "Nothing to look at (yet)!" + COLORS["reset"])
            else:
                print(COLORS["red"] + "Unimplemented for now, sowwy." + COLORS["reset"])
                continue

        elif chosen in close_menu:
            break

        # special cases
        else:
            inv.open_item(answers_to_item[chosen])


inventory_playground()
