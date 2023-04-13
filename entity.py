import typing
from items import att_or_def_func_attributes
import inventory
from util import hide_color_if_low_lvl, COLORS
from numpy import random, ndarray
from collections import defaultdict


class Bodypart:
    parts_costs = {
        "head": 10,  # can only be one for now,
        "torso": 10,  # same, can only be one for now
        "leg": 25,
        "tail": 45,
        "wings": 100,
        "extra eyes": 100,
        "spikes": 50,
        "venom sac": 70,  # also can only be one for now
        "healing gland": 100,  # same,
        "lifesucker": 100,  # same
    }

    parts_health = {
        "head": 50,
        "torso": 100,
        "leg": 50,
        "tail": 50,
        "wings": 50,
        "extra eyes": 0,
        "spikes": 0,
        "venom sac": 0,
        "healing gland": 0,
        "lifesucker": 0,
    }

    def __init__(
        self,
        name,
        inventory_name=None,
        health=0,
        att_pwr=0,
        def_pwr=0,
        att_buffs=None,
        def_buffs=None,
        att_debuffs=None,
        def_debuffs=None,
    ):
        self.name = name
        if inventory_name is None:
            if self.name == "left arm" or self.name == "right arm":
                self.inventory_name = "hands"
            elif self.name == "left leg" or self.name == "right leg":
                self.inventory_name = "pants"
            elif self.name == "torso":
                self.inventory_name = "jacket"

            else:
                self.inventory_name = name
        else:
            self.inventory_name = inventory_name

        self.max_health = int(health)
        self.current_health = int(health)
        self.att_pwr = int(att_pwr)
        self.def_pwr = int(def_pwr)
        if att_buffs is None:
            self.att_buffs = list()
        else:
            self.att_buffs = att_buffs
        if def_buffs is None:
            self.def_buffs = list()
        else:
            self.def_buffs = def_buffs
        if att_debuffs is None:
            self.att_debuffs = defaultdict(int)
        else:
            self.att_debuffs = att_debuffs
        if def_debuffs is None:
            self.def_debuffs = defaultdict(int)
        else:
            self.def_debuffs = def_debuffs
        # self.descriptors = descriptors

    def __str__(self):
        return f"{self.name}: {self.current_health} / {self.max_health}"


class IntegratedBodypart(Bodypart):
    def __init__(self, name, parent, health, dmg_pwr=0, def_pwr=0):
        super().__init__(name, health)
        self.parent = parent


class Entity:
    def __init__(self, name: str, body_parts: list[Bodypart], speed=0, ev_rating=0):
        self.name = name
        self.body_parts = body_parts
        self.speed = speed
        self.ev_rating = ev_rating


class Player(Entity):
    def __init__(self, speed=20, ev_rating=0):
        self.name = "Player"
        self.body_parts = [
            Bodypart("head", health=100, att_pwr=20, def_pwr=15),
            Bodypart("left arm", health=100, att_pwr=40, def_pwr=15),
            Bodypart("right arm", health=100, att_pwr=40, def_pwr=15),
            Bodypart("left leg", health=200, att_pwr=40, def_pwr=30),
            Bodypart("right leg", health=200, att_pwr=40, def_pwr=30),
            Bodypart("torso", health=300, att_pwr=0, def_pwr=45),
        ]
        self.inventory = inventory.Inventory()
        super().__init__(self.name, self.body_parts, speed=5, ev_rating=0)


class Monster(Entity):
    prefixes = {
        0: [
            "Ugly",
            "Disfigured",
            "Disformed",
            "Quirky",
            "Misshapen",
            "Weird-ass",
            "Foul",
            "Grisly",
            "Hairy",
        ],
        1: [
            "Atrocious",
            "Disgusting",
            "Disfigured",
            "Disformed",
            "Ugly",
            "Foul",
            "Heinous",
            "Crude",
            "Corpselike",
            "Revolting",
            "Beastly",
        ],
        2: [
            "Weird",
            "Frightening",
            "Strange",
            "Outlandinsh",
            "Esoteric",
            "Corpselike",
            "Alien",
        ],
        3: [
            "Frightening",
            "Horrifying",
        ],
    }
    suffixes = {
        0: ["Thing", "Creature", "Vermin", "Monster"],
        1: ["Varmint", "Monster", "Beast"],
        2: ["Monster", "Beast", "Abomination"],
        3: ["Monster"],
    }

    def __init__(self, danger_rating, name=None, body_parts=[], speed=0, ev_rating=0):
        self.danger_rating = danger_rating
        self.danger_class = self.danger_rating // 100
        self.name = name
        self.body_parts = body_parts
        self.speed = speed
        self.ev_rating = ev_rating
        self.bonus_def = 0
        self.att_buffs = []
        self.def_buffs = []

        if not name:
            self.name = (
                "\u001b[31m"
                + random.choice(self.prefixes[self.danger_class])
                + " "
                + random.choice(self.suffixes[self.danger_class])
                + "\u001b[0m"
            )

        def buy_self():
            """
            Monster 'buys' its parts using its danger_rating.
            Parts' costs and parameters are shown above.
            It always starts with head,
            then with torso if it's available,
            then it makes a specific calculation:
            if it has enough *only* for wings, it buys them;
            if it doesn't have enough, it tries to buy a leg.
            After that, it buys everything randomly
            until it runs out of danger_rating.
            """
            resource = self.danger_rating

            def get_health(base_health):
                return base_health * (self.danger_class + 2) + random.normal(
                    float(base_health) / 6, scale=float(base_health) / 12
                )

            def get_damage(base_damage):
                return (
                    base_damage * (self.danger_class + 3)
                    + random.normal(float(base_damage), scale=float(base_damage) / 2)
                    * 1.5
                )

            def get_defense(base_defense):
                return base_defense * (self.danger_class + 2) + random.normal(
                    float(base_defense), scale=float(base_defense) / 2
                )

            head = Bodypart(
                name="head",
                health=get_health(Bodypart.parts_health["head"]),
                att_pwr=get_damage(Bodypart.parts_costs["head"]),
                def_pwr=get_defense(Bodypart.parts_costs["head"]),
            )
            self.body_parts.append(head)
            resource -= Bodypart.parts_costs["head"]

            if resource < Bodypart.parts_costs["torso"]:
                return
            torso = Bodypart(
                name="torso",
                health=get_health(Bodypart.parts_health["torso"]),
                att_pwr=0,
                def_pwr=get_defense(Bodypart.parts_costs["torso"]),
            )
            self.body_parts.append(torso)
            resource -= Bodypart.parts_costs["torso"]

            if resource < Bodypart.parts_costs["leg"]:
                return
            if resource >= Bodypart.parts_costs["wings"] and resource < (
                Bodypart.parts_costs["wings"] + Bodypart.parts_costs["leg"]
            ):
                wings = Bodypart(
                    name="wings",
                    health=get_health(Bodypart.parts_health["wings"]),
                    att_pwr=get_damage(Bodypart.parts_costs["wings"]),
                    def_pwr=get_defense(Bodypart.parts_costs["wings"]),
                )
                self.body_parts.append(wings)
                self.speed += 10
                resource -= Bodypart.parts_costs["wings"]
                return
            if resource < Bodypart.parts_costs["leg"] * 2:
                if resource < Bodypart.parts_costs["leg"]:
                    return
                else:
                    leg = Bodypart(
                        name="leg",
                        health=get_health(Bodypart.parts_health["leg"]),
                        att_pwr=get_damage(Bodypart.parts_costs["leg"]),
                        def_pwr=get_defense(Bodypart.parts_costs["leg"]),
                    )
                    self.body_parts.append(leg)
                    self.speed += 5
                    resource -= Bodypart.parts_costs["leg"]
                    return

            else:
                while resource >= Bodypart.parts_costs["leg"]:
                    available_parts = [
                        x
                        for x in Bodypart.parts_costs
                        if Bodypart.parts_costs[x] <= resource
                        and x != "head"
                        and x != "torso"
                    ]
                    part = random.choice(available_parts)
                    added_part = Bodypart(
                        name=part, health=get_health(Bodypart.parts_health[part])
                    )
                    self.body_parts.append(added_part)
                    resource -= Bodypart.parts_costs[part]
            return

        if not body_parts:
            buy_self()
        else:
            self.body_parts = body_parts

        for part in self.body_parts:
            num_att_attributes = random.randint(0, self.danger_class + 2)
            if num_att_attributes > 0:
                part.att_buffs.extend(
                    random.choice(
                        att_or_def_func_attributes["att"], num_att_attributes
                    ).tolist()
                )

            num_def_attributes = random.randint(0, self.danger_class + 2)
            if num_def_attributes > 0:
                part.def_buffs.extend(
                    random.choice(
                        att_or_def_func_attributes["def"], num_def_attributes
                    ).tolist()
                )

        for part in self.body_parts:
            if isinstance(part.att_buffs, ndarray):
                part.att_buffs = part.att_buffs.tolist()
            if isinstance(part.def_buffs, ndarray):
                part.def_buffs = part.def_buffs.tolist()

        self.descrption = None

        # super().__init__(name, body_parts)

    def create_description(self, guidewatch):
        unique_descriptions = {
            ("head",): [
                f"{hide_color_if_low_lvl(self.name, guidewatch)} is just a rolling head that really wants to take a bite of you.",
                f"This is a head that somehow floats in the air but doesn't seem to be moving otherwise",
            ],
            ("head", "torso"): [
                f"This is a blob with a head—has problems moving, but zero problems biting.",
                f"The monster looks like a head glued to a limbless body. It seems pretty disappointed with its postition.",
            ],
            ("head", "torso", "wings"): [
                f"This monster is Beholder-ish in appearance, except there are wings instead of extra eyes.",
                f"Before you is a head that's awkwardly flying around.",
                f"This is basically a Cacodemon, except it uses wings to fly.",
                f"How many monsters does it take to screw in a lightbulb? One more than {hide_color_if_low_lvl(self.name, guidewatch)}, since that one doesn't have any limbs.",
            ],
            ("head", "torso", "leg"): [
                f"This monster is a head hopping around on a single leg. What an achievement in locomotion!",
                f"It's a head propped hilariously by a single leg. Nevertheless, it can and will try to bite/claw you.",
            ],
            ("head", "torso", "leg", "leg", "leg"): [
                f"{hide_color_if_low_lvl(self.name, guidewatch)} is tri-pedal.",
                f"This monster is triangular in shape, which is surely helped by its three legs.",
            ],
        }
        unique_descriptions = {
            tuple(sorted(k)): v for k, v in unique_descriptions.items()
        }
        if len(self.body_parts) == 1:
            body_parts_names = ("head",)
        if len(self.body_parts) == 2:
            body_parts_names = ("head", "torso")
        else:
            body_parts_names = tuple(sorted([x.name for x in self.body_parts]))

        descrption = ""
        descrption += COLORS["reset"]

        # uniques
        if body_parts_names in unique_descriptions:
            descrption = random.choice(unique_descriptions[body_parts_names]) + " "

        # detailed head descrption
        if random.random() > 0.75:
            head_descr = [
                f"It has an elongated, canine-like head.",
                f"The monester's head is rather large for its torso.",
                f"{hide_color_if_low_lvl(self.name, guidewatch)} has a small, lizard-like head with bulging eyes.",
                f"{hide_color_if_low_lvl(self.name, guidewatch)}'s enormously huge eyes pierce into your soul.",
                f"This monster has a feline-like head, and it twitches its ears ever so often.",
            ]
            descrption += random.choice(head_descr) + " "

        # detailed neck descrption
        if random.random() > 0.95 and "torso" in body_parts_names:
            neck_descr = [
                f"The head is connected to the torso with a thick neck; you swear you can see some buldging veins.",
                f"The monster doesn't really have a neck—its head is directly plopped to its body.",
                f"It has a very thin neck that's defying the laws of physics with its stick-like appearance.",
            ]
            descrption += random.choice(neck_descr) + " "

        # description of a single leg
        if body_parts_names.count("leg") == 1:
            if random.random() > 0.9:
                leg_descr = [
                    f"This monster has a single leg—tough and strong to carry the weight of its body.",
                    f"It has only one limb, but god forbid you get in the swiping range of said limb.",
                ]
                descrption += random.choice(leg_descr) + " "
            elif random.random() > 0.3:
                leg_descr = [f"It's single-limbed.", f"The monster has only one limb."]
                descrption += random.choice(leg_descr) + " "

        # TODO: descrption of two legs
        # TODO: description of three legs
        # TODO: description of four legs
        # TODO: description of more legs
        # TODO: description of one (pair of) wings
        # TODO: description of two+ pairs of wings
        # TODO: description for the rest

        if descrption.strip() == "":
            descrs = [
                f"This sure is a monster.",
                f"The {hide_color_if_low_lvl(self.name, guidewatch)} is quite a monster.",
                f"{hide_color_if_low_lvl(self.name, guidewatch)} is fairly typical for a monster.",
            ]
            descrption = random.choice(descrs)

        return descrption

    def show_description(
        self, guidewatch: inventory.Guidewatch, print_text_description=False
    ):
        name = self.name
        body_parts = [x for x in self.body_parts if x.current_health > 0]
        # body_parts_names = [x.name for x in body_parts]
        advanced_stats = {
            "speed": self.speed,
            "evasion rating": self.ev_rating,
            "attack buffs": self.att_buffs,
            "defense buffs": self.def_buffs,
        }
        if self.descrption is None:
            self.descrption = self.create_description(guidewatch)
        description = self.descrption
        description = COLORS["reset"] + " " + description + " " + COLORS["reset"]
        options_levels = guidewatch.options_levels
        guidewatch_lvl = guidewatch.level

        # also < monster_health_info
        if guidewatch_lvl < options_levels["use_color"]:
            print(
                hide_color_if_low_lvl(name, guidewatch),
                f" - class: {self.danger_class}",
            )
            for part in body_parts:
                if part.current_health / part.max_health == 1:
                    print(f"{part.name}: untouched", end="; ")
                elif part.current_health / part.max_health >= 0.66:
                    print(f"{part.name}: slightly battered", end="; ")
                elif part.current_health / part.max_health >= 0.33:
                    print(f"{part.name}: damaged", end="; ")
                elif part.current_health / part.max_health >= 0:
                    print(f"{part.name}: in terrible shape", end="; ")
            print()

        elif guidewatch_lvl < options_levels["monster_advanced_stats_info"]:
            print(name)
            for x in body_parts:
                print(
                    str(x),
                    f"buffs: {x.att_buffs + x.def_buffs}",
                    f"debuffs: {list(x.att_debuffs.keys()) + list(x.def_debuffs.keys())}",
                    end=";\n",
                    sep=", ",
                )

        else:
            print(name)
            for x in body_parts:
                print(
                    str(x),
                    f"buffs: {x.att_buffs + x.def_buffs}",
                    f"debuffs: {list(x.att_debuffs.keys()) + list(x.def_debuffs.keys())}",
                    end=";\n",
                    sep=", ",
                )
            print(advanced_stats)

        if print_text_description:
            print(hide_color_if_low_lvl(description, guidewatch))

    def __str__(self):
        return self.name


if __name__ == "__main__":
    print(Monster(danger_rating=random.normal(100, 50)))
# print(Monster(danger_rating=10))
