from items import Item, Guidewatch, GeneralAttribute
from menu import Menu
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
}

reverse_full_items = {
    "hands": GeneralAttribute("sword"),
    "jacket": GeneralAttribute("jacket"),
    "cape": GeneralAttribute("cape"),
    "pants": GeneralAttribute("pants"),
    "boots": GeneralAttribute("boots"),
    "left_pocket": GeneralAttribute("food"),
    "right_pocket": GeneralAttribute("water"),
}


class Inventory:
    def __init__(self):
        self.items = {
            "hands": "\u001b[0m" + " None",
            "jacket": "\u001b[0m" + " None",
            "cape": "\u001b[0m" + " None",
            "pants": "\u001b[0m" + " None",
            "boots": "\u001b[0m" + " None",
            "left_pocket": "\u001b[0m" + " None",
            "right_pocket": "\u001b[0m" + " None",
            "backpacks": [""],
            "materia": [""],
            "guidewatch": Guidewatch(2),
        }

    def show_inventory(self):
        items_list = {}
        guidewatch_lvl = self.items["guidewatch"].level
        for item in self.items:
            if item in ["backpacks", "materia", "guidewatch"]:
                continue
            else:
                val = self.items[item]
                # delete color if the level of guidewatch is insufficient
                items_list[item] = (
                    "\u001b[0m" + " " + val.__str__()[5:]
                    if guidewatch_lvl < 5
                    else val.__str__()
                    # val.__str__()
                )

        text = f"""Guidewatch lvl: {guidewatch_lvl}
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
        if item.type_of == "materia":
            if self.items["materia"] == [""]:
                self.items["materia"].pop(0)
            self.items["materia"].append(item)
            return None

        if item.type_of == "backpack":
            if self.items["backpacks"] == [""]:
                self.items["backpacks"].pop(0)
            if len(self.items["backpacks"] >= 4):
                print("You can't carry more backpacks!")
                return item
            self.items["backpacks"].append(item)
            return None

        slot = full_items[str(item.type_of)]
        if (
            self.items[slot] != "\u001b[0m" + " None"
            and self.items[slot] != " None"
            and self.items[slot] != "None"
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
            self.drop_item(item)
        else:
            for i in self.items["backpacks"]:
                if i.empty_slots > 0:
                    i.add_item(item)
                    break
        return self

    def drop_item(self, item):
        # TODO: floor integration
        self.items[item] = "\u001b[0m" + " None"
        return item

    def fill(self):
        for item in reverse_full_items:
            if self.items[item] == "\u001b[0m" + " None":
                type_of = reverse_full_items[item]
                self.equip_item(Item(type_of=type_of))

    def empty(self):
        for i in self.items:
            if i in ("backpacks", "materia"):
                self.items[i] = [""]
            if i == "guidewatch":
                continue
            else:
                self.items[i] = "\u001b[0m" + " None"


class Backpack(Inventory):
    def __init__(self, name, slots):
        self.name = name
        self.total_slots = slots
        self.empty_slots = slots
        self.items = {}

    def show_inventory(self):
        text = ",\n".join([items.keys()])
        return text

    def add_item(self, item: Item):
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

    def __str__(self):
        return f"{self.name}: {self.empty_slots}/{self.total_slots}"


inv = Inventory()


def fill_inventory():
    global inv
    inv.fill()
    inventory_playground()


def empty_inventory():
    global inv
    inv.empty()
    inventory_playground()


def set_guidewatch_level_to_1():
    global inv
    inv.items["guidewatch"].level = 1
    inventory_playground()


def set_guidewatch_level_to_100():
    global inv
    inv.items["guidewatch"].level = 100
    inventory_playground()


def inventory_playground():
    text = "r: sort by rarity, t: sort by type, y: sort by name; e: equip, u: unequip"
    print(inv.show_inventory())
    options = {
        "Fill Inventory  ": fill_inventory,
        "Empty Inventory ": empty_inventory,
        "Set Guidewatch lvl to 1  ": set_guidewatch_level_to_1,
        "Set Guidewatch level to 100  ": set_guidewatch_level_to_100,
    }
    # item = Item(sort_of="backpack")
    Menu(text, options)


inventory_playground()
