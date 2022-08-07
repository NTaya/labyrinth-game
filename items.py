from numpy import random
from util import COLORS


class Attribute:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name


class GeneralAttribute(Attribute):
    type_to_meta_type = {
        "sword": "weapon",
        "knife": "weapon",
        "bow": "weapon",
        "handgun": "weapon",
        "rifle": "weapon",
        "jacket": "armor",
        "pants": "armor",
        "boots": "armor",
        "cape": "armor",
        "food": "food",
        "water": "food",
        "potion": "food",
        "scroll": "magic",
        "materia": "magic",
        "backpack": "other",
        "other": "other" "",
    }

    main_names = {
        "sword": ("Sword", "Blade"),
        "knife": ("Knife", "Dagger"),
        "bow": ("Bow", "Crossbow"),
        "handgun": ("Gun", "Handgun"),
        "rifle": ("Assault Rifle", "Rifle"),
        "jacket": ("Jacket", "Coat"),
        "pants": ("Pants", "Cargo Pants"),
        "boots": ("Boots", "Footwear"),
        "cape": ("Cape", "Cloak"),
        "food": ("MRI", "Food"),
        "water": ("Drinking Bottle", "Water Bottle"),
        "potion": ("Potion", "Mysterious Bottle"),
        "scroll": ("Scroll", "Parchment"),
        "materia": ("Materia", "Tiny Orb"),
        "backpack": ("Backpack", "Bag"),
        "other": ("Other", "Other"),
    }

    def __init__(self, name):
        super().__init__(name)
        self.type_of = name
        self.meta_type = self.type_to_meta_type[self.type_of]


general_attributes = [
    GeneralAttribute(item)
    for item in [
        "sword",
        "knife",
        "bow",
        "handgun",
        "rifle",
        "jacket",
        "pants",
        "boots",
        "cape",
        "food",
        "water",
        "potion",
        "scroll",
        "materia",
        "backpack",
        "other",
    ]
]


class FunctionalAttribute(Attribute):
    prefixes = {
        "fire": ("Fire", "Flaming", "Fiery"),
        "ice": ("Cold", "Freezing", "Ice", "Winter"),
        "death": ("Deathly", "Blacked"),
        "cure": ("Healing", "Green"),
        "defense": ("Defensive", "Protecting", "Protective"),
        "speed": ("Quick", "Swift"),
        "arcane": ("Arcane", "Cabalistic"),
        "attack": ("Bloodthirsty", "Battle-worn", "Attacking", "Striking"),
    }
    suffixes = {
        "fire": ("Ablaze", "Aflame", "of Fire"),
        "ice": ("of Cold", "of Ice", "of Winter"),
        "death": ("of Death", "of Destruction", "of the Deathbringer"),
        "cure": ("of Life", "of Healing"),
        "defense": ("That Defends", "That Protects"),
        "speed": ("of Swiftness", "of Quickness"),
        "arcane": ("of Occult", "of the Arcane"),
        "attack": ("of the Battle", "of Aggression"),
    }

    def __init__(self, name):
        super().__init__(name)


# functional_attributes = [
#     FunctionalAttribute(item)
#     for item in ["fire", "ice", "death", "cure", "defense", "speed", "arcane"]
# ]

functional_attributes = [
    "fire",
    "ice",
    "death",
    "cure",
    "defense",
    "speed",
    "arcane",
    "attack",
]


class Item:
    def __init__(self, type_of=None, attribute_num=0, attributes=None):
        self.attributes = attributes
        self.attribute_num = attribute_num
        self.type_of = type_of

        if not type_of:
            self.type_of = random.choice(general_attributes)

        if not attribute_num:
            rand = random.random()
            if rand < 0.2:
                self.attribute_num = 1
            elif rand < 0.4:
                self.attribute_num = 2
            elif rand < 0.6:
                self.attribute_num = 3
            elif rand < 0.7:
                self.attribute_num = 4
            elif rand < 0.8:
                self.attribute_num = 5
            elif rand < 0.95:
                self.attribute_num = 6
            else:
                self.attribute_num = 7
        else:
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

        self.name = self.get_name()

    def get_name(self):
        rarities = {
            "common": COLORS["white"],
            "rare": COLORS["green"],
            "epic": COLORS["magenta"],
            "legendary": COLORS["yellow"],
        }

        self.name = rarities[self.rarity]

        if self.rarity == "common":
            self.used_attribute = random.choice(self.attributes, 1, replace=False)
            # prefix
            self.name += random.choice(
                list(FunctionalAttribute.prefixes[self.used_attribute[0]])
            )
            self.name += " "
            # main
            self.name += random.choice(
                list(GeneralAttribute.main_names[self.type_of.name])
            )
        elif self.rarity == "rare":
            self.used_attributes = random.choice(self.attributes, 2, replace=False)
            # prefix
            self.name += random.choice(
                list(FunctionalAttribute.prefixes[self.used_attributes[0]])
            )
            self.name += " "
            # main
            self.name += random.choice(
                list(GeneralAttribute.main_names[self.type_of.name])
            )
            self.name += " "
            # suffix
            self.name += random.choice(
                list(FunctionalAttribute.suffixes[self.used_attributes[1]])
            )
        elif self.rarity == "epic":
            self.used_attributes = random.choice(self.attributes, 3, replace=False)
            # prefix 1
            self.name += random.choice(
                list(FunctionalAttribute.prefixes[self.used_attributes[0]])
            )
            self.name += " "
            # prefix 2
            self.name += random.choice(
                list(FunctionalAttribute.prefixes[self.used_attributes[1]])
            )
            self.name += " "
            # main
            self.name += random.choice(
                list(GeneralAttribute.main_names[self.type_of.name])
            )
            self.name += " "
            # suffix
            self.name += random.choice(
                list(FunctionalAttribute.suffixes[self.used_attributes[2]])
            )
        elif self.rarity == "legendary":
            self.used_attributes = random.choice(self.attributes, 4, replace=False)
            # prefix 1
            self.name += random.choice(
                list(FunctionalAttribute.prefixes[self.used_attributes[0]])
            )
            self.name += " "
            # prefix 2
            self.name += random.choice(
                list(FunctionalAttribute.prefixes[self.used_attributes[1]])
            )
            self.name += " "
            # main
            self.name += random.choice(
                list(GeneralAttribute.main_names[self.type_of.name])
            )
            self.name += " "
            # suffix 1
            self.name += random.choice(
                list(FunctionalAttribute.suffixes[self.used_attributes[2]])
            )
            self.name += " and "
            # suffix 2
            self.name += random.choice(
                list(FunctionalAttribute.suffixes[self.used_attributes[3]])
            )

        self.name += COLORS["reset"]
        return self.name

    def print_description(self, guidewatch_lvl):
        name = (
            "\u001b[0m" + " " + self.name.__str__()[5:]
            if guidewatch_lvl < 5
            else self.name.__str__()
        )
        article = "an" if name[5].lower() in ["a", "o", "u", "e", "i"] else "a"
        print(f"It's {article} {name}.")
        if guidewatch_lvl >= 20:
            print(f"Attributes: {self.attributes}.")

    def __str__(self):
        return self.name


class Guidewatch:
    def __init__(self, level):
        self.level = level

        options_levels = {
            "current_sector": 0,
            "current_floor": 1,
            "current_room": 2,
            "use_color": 5,
            "show_weather": 10,
            "show_properties": 20,
            "constant_info": 30,
            "next_room_sectors": 40,
            "navigate_to_constant": 50,
        }

        params = []
