from items import (
    Item,
    Guidewatch,
    GeneralAttribute,
    general_attributes,
    functional_attributes,
)
from util import COLORS, func_wrapper, hide_color_if_low_lvl
from menu import Menu
from numpy import random
import typing
import keyboard


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
    "potion": None,
    "scroll": None,
    "other": None,
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
            "backpacks": ["None"],
            "materia": ["None"],
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
                if item_contents != ["None"]:
                    for inner_item_index in range(len(item_contents)):
                        val = item_contents[inner_item_index]
                        items_list[item] = [None for i in range(len(item_contents))]
                        items_list[item][inner_item_index] = hide_color_if_low_lvl(
                            val, self.guidewatch
                        )
            else:
                val = self.items[item]
                # delete color if the level of guidewatch is insufficient
                items_list[item] = hide_color_if_low_lvl(val, self.guidewatch)
        # for key, value in items_list.items():
        #     if isinstance(value, list):
        #         print(key, *value)
        #     else:
        #         print(key, value)

        text = f"""Guidewatch lvl: {self.guidewatch.level}
Hands: {items_list["hands"]}
Jacket: {items_list["jacket"]}
Cape: {items_list["cape"]}
Pants: {items_list["pants"]}
Boots: {items_list["boots"]}
Food pocket: {items_list["left_pocket"]}
Water pocket: {items_list["right_pocket"]}
"""
        print(text, end="")
        print(
            "Backpacks: ",
            *[
                hide_color_if_low_lvl(x, self.guidewatch)
                for x in self.items["backpacks"]
            ],
        )
        print("Materia: ", end="")

        print(
            *[hide_color_if_low_lvl(x, self.guidewatch) for x in self.items["materia"]],
            sep=", ",
        )
        # return text

    def equip_item(self, item):
        """Returns the item if equipment failed,
        otherwise return None."""
        if str(item.type_of) == "materia":
            if self.items["materia"] == ["None"]:
                self.items["materia"][0] = item
                return None
            self.items["materia"].append(item)
            print("DEBUG: ", self.items["materia"])
            return None

        if str(item.type_of) == "backpack":
            if self.items["backpacks"] == ["None"]:
                self.items["backpacks"][0] = item
                return None
            elif len(self.items["backpacks"]) >= 4:
                print("You can't carry more backpacks!")
                return item
            self.items["backpacks"].append(item)
            return None

        slot = full_items[str(item.type_of)]

        # if can't equip, can only hold
        # (potions and scrolls)
        if slot is None:
            print(COLORS["cyan"], "Item using is not supported yet.", COLORS["reset"])
            return self.put_into_backpack(item)

        # I ran out of fucks debugging this
        if (
            self.items[slot] != COLORS["reset"] + " None"
            and self.items[slot] != " None"
            and self.items[slot] != "None"
            and self.items[slot] != ["None"]
        ):
            print(COLORS["red"], f"Slot for {slot} is full!", COLORS["reset"])
            return item
        self.items[slot] = item
        return None

    def unequip_item(self, item):
        result = self.put_into_backpack(item)
        if result:
            self.remove_item(item)
        return self

    def put_into_backpack(self, item):
        if not (
            self.items["backpacks"] == ["None"]
            or sum([x.empty_slots for x in self.items["backpacks"]]) == 0
        ):
            for i in self.items["backpacks"]:
                if i.empty_slots > 0:
                    i.add_item(item)
                    return item
        else:
            print(
                COLORS["red"]
                + "No suitable backpacks, dropping item."
                + COLORS["reset"]
            )
            self.drop_item(item)
            return None

    def drop_item(self, item):
        # TODO: floor integration
        dropped_item = self.remove_item(item)

    def remove_item(self, item):
        """Shouldn't be called from outside,
        use drop_item() or unequip_item() instead.
        """
        reverse_items = {
            v: k for k, v in self.items.items() if k not in forbidden_types
        }
        try:
            item = reverse_items[item]
        # the item we try to remove is not an equipment piece
        except KeyError:
            return item
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
        if self.items["backpacks"] == ["None"]:
            self.equip_item(Backpack())

    def empty(self):
        for i in self.items:
            if i in ("backpacks", "materia"):
                self.items[i] = ["None"]
            else:
                self.items[i] = COLORS["reset"] + " None"

    def open_item(self, item):
        # Just in case, you shouldn't normally be able to call it with a bag
        if str(item.type_of) == "backpack":
            item.open_bag()
        else:
            self.item_menu(item)

    def item_menu(self, item):
        while True:
            item.print_description(self.guidewatch.level)
            text = ""
            options = ["Unequip Item  ", "Drop Item  ", "Back  "]
            close_menu = ["Unequip Item  ", "Drop Item  ", "Back  "]
            answer = Menu(text, options).answer
            if answer == "Equip or Use Item  ":
                self.equip_item(item, inv)
            if answer == "Unequip Item  ":
                self.unequip_item(item)
            elif answer == "Drop Item  ":
                self.drop_item(item)
            if answer in close_menu:
                break


class Backpack(Item, Inventory):
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
        text = "\n* ".join(
            list([hide_color_if_low_lvl(i, inv.guidewatch) for i in self.items.keys()])
        )
        text = "* " + text
        print(text)
        # return text

    def add_item(self, item: Item):
        if str(item.type_of) == "backpack":
            print(
                COLORS["red"],
                "No Bags-of-Holding-Inside-Bags-of-Holding!",
                COLORS["reset"],
            )
            return self
        self.items[str(item)] = item
        self.empty_slots -= 1
        return self

    def equip_item(self, item, inventory_instance):
        if inventory_instance.equip_item(item) is None:  # if equipped successfully
            self.drop_item(item)
        return self

    def unequip_item(self, item):
        reverse_items = {v: k for k, v in self.items.items()}
        self.items.pop(reverse_items[item])
        super().drop_item(item)
        self.empty_slots += 1
        return self

    # just an alias for unequip_item()
    def drop_item(self, item):
        self.unequip_item(item)

    def open_bag(self, item, inventory):
        # item = self
        # Item is as-item representation
        # self is as-inventory representation
        item_for_desc = item
        sorting = None
        while True:
            item_for_desc.print_description(inventory.guidewatch.level)
            self.show_inventory()
            # text = "r: sort by rarity, t: sort by type, y: sort by name"
            text = ""
            answers_to_item = {}
            options = []

            sort_options = [
                COLORS["cyan"] + "Sort by type" + COLORS["reset"],
                COLORS["cyan"] + "Sort by name" + COLORS["reset"],
            ]
            options.extend(sort_options)

            if self.empty_slots != self.total_slots:
                for item_type, item in self.items.items():
                    answer_text = item
                    answer_text = hide_color_if_low_lvl(item, inv.guidewatch)
                    if answer_text != COLORS["reset"] + " None":
                        options.append(answer_text)
                        answers_to_item[answer_text] = item
            if sorting == "type":
                options.sort(
                    key=lambda x: str(answers_to_item[x].type_of.meta_type)
                    if x not in sort_options
                    else "",
                )
            elif sorting == "name":
                options.sort(key=lambda x: x[5:] if x not in sort_options else "")
            options.append("Back  ")
            chosen = Menu(text, options).answer
            if chosen == COLORS["cyan"] + "Sort by type" + COLORS["reset"]:
                sorting = "type"
            elif chosen == COLORS["cyan"] + "Sort by name" + COLORS["reset"]:
                sorting = "name"
            elif chosen == "Back  ":
                break
            else:
                self.open_item(answers_to_item[chosen])

    def item_menu(self, item):
        while True:
            item.print_description(inv.guidewatch.level)
            text = ""
            options = ["Equip or Use Item  ", "Drop Item  ", "Back  "]
            close_menu = ["Unequip Item  ", "Drop Item  ", "Back  "]
            answer = Menu(text, options).answer
            if answer == "Equip or Use Item  ":
                self.equip_item(item, inv)
            elif answer == "Drop Item  ":
                self.drop_item(item)
            break

    def __str__(self):
        return f"{self.name}: {self.total_slots - self.empty_slots}/{self.total_slots}"


# TODO: refactor this into the playground
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
# most stuff will have special interactions with these items
forbidden_types = ["backpacks", "backpack", "materia"]


def inventory_playground():
    global inv
    global forbidden_types
    while True:
        # chosen = None
        text = ""
        # some playground responses
        options = [
            "Fill Inventory  ",
            "Empty Inventory  ",
            "Set Guidewatch lvl to 1  ",
            "Set Guidewatch level to 100  ",
        ]
        # responses that don't require special treatment
        non_variate_responses = {
            "Fill Inventory  ": fill_inventory,
            "Empty Inventory  ": empty_inventory,
            "Set Guidewatch lvl to 1  ": set_guidewatch_level_to_1,
            "Set Guidewatch level to 100  ": set_guidewatch_level_to_100,
        }
        # item generator
        gen_item_options = [
            "Equip Generated Item  ",
            "Put Generated Item Into A Backpack  ",
        ]
        # this lists the items as options
        options.extend(gen_item_options)
        # special responses, need to pass an argument to a func
        answers_to_item = {}
        for item_type, item in inv.items.items():
            answer_text = item
            if item_type not in forbidden_types:
                answer_text = hide_color_if_low_lvl(item, inv.guidewatch)
                if answer_text != COLORS["reset"] + " None":
                    options.append(answer_text)
                    # Friendly reminder:
                    # answer_text = str
                    # item = Item
                    answers_to_item[answer_text] = item
        # more buttons
        options.extend(
            ["Take a look at Backpacks  ", "Take a look at Materia  ", "Quit  "]
        )
        close_menu = ["Quit  "]

        inv.show_inventory()

        type_of_gen_item = random.choice(general_attributes)
        # type_of_gen_item = GeneralAttribute("materia")
        if str(type_of_gen_item) == "backpack":
            generated_item = Backpack()
        else:
            generated_item = Item(type_of=type_of_gen_item)

        print(
            COLORS["cyan"],
            "I generated an item for you:",
            COLORS["reset"],
            str(generated_item),
        )

        chosen = Menu(text, options).answer

        if chosen in non_variate_responses.keys():
            non_variate_responses[chosen]()

        elif chosen == "Take a look at Backpacks  ":
            # new menu
            if inv.items["backpacks"] == ["None"]:
                print(COLORS["red"] + "Nothing to look at (yet)!" + COLORS["reset"])
                Menu("", ["Continue"])
            else:
                while True:
                    answers_to_bag = {}
                    for i in range(len(inv.items["backpacks"])):
                        item = inv.items["backpacks"][i]
                        answer_text = hide_color_if_low_lvl(item, inv.guidewatch)
                        answers_to_bag[answer_text] = inv.items["backpacks"][i]
                    bag_options = list(answers_to_bag.keys())
                    bag_options.append("Close  ")
                    bag_text = ""
                    bag_chosen = Menu(bag_text, bag_options).answer
                    if bag_chosen == "Close  ":
                        break
                    bag = answers_to_bag[bag_chosen]
                    bag.open_bag(bag, inv)

        elif chosen == "Take a look at Materia  ":
            # same, new menu
            if inv.items["materia"] == ["None"]:
                print(COLORS["red"] + "Nothing to look at (yet)!" + COLORS["reset"])
                Menu("", ["Continue"])
            else:
                print(COLORS["red"] + "Unimplemented for now, sowwy." + COLORS["reset"])
                Menu("", ["Continue"])
                continue

        elif chosen == "Equip Generated Item  ":
            inv.equip_item(generated_item)
        elif chosen == "Put Generated Item Into A Backpack  ":
            inv.put_into_backpack(generated_item)

        elif chosen in close_menu:
            break

        elif chosen is None:
            pass

        # special cases
        else:
            inv.open_item(answers_to_item[chosen])


if __name__ == "__main__":
    inv = Inventory()
    inventory_playground()
