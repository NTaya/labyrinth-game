import typing
from numpy import random


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
    }

    def __init__(self, name, health=0):
        self.name = name
        self.max_health = int(health)
        self.current_health = int(health)
        # self.descriptors = descriptors

    def __str__(self):
        return f"{self.name}: {self.current_health} / {self.max_health}"


class IntegratedBodypart(Bodypart):
    def __init__(self, name, parent, health):
        super().__init__(name, health)
        self.parent = parent


class Entity:
    def __init__(self, name: str, body_parts: list[Bodypart]):
        self.name = name
        self.body_parts = body_parts


class Player(Entity):
    def __init__(self):
        name = "Player"
        body_parts = [
            Bodypart("head", 100, None),
            Bodypart("left arm", 100, None),
            Bodypart("right arm", 100, None),
            Bodypart("left leg", 200, None),
            Bodypart("right leg", 200, None),
            Bodypart("torso", 400, None),
        ]
        super().__init__(name, body_parts)


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
        3: ["Frightening", "Horrifying"],
    }
    suffixes = {
        0: ["Thing", "Creature", "Vermin", "Monster"],
        1: ["Varmint", "Monster", "Beast"],
        2: ["Monster", "Beast", "Abomination"],
        3: ["Monster"],
    }

    def __init__(self, danger_rating, name=None, body_parts=[]):
        self.danger_rating = danger_rating
        self.danger_class = self.danger_rating // 100
        self.name = name
        self.body_parts = body_parts

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
                return base_health * (self.danger_class + 1) + random.normal(
                    float(base_health) / 6, scale=float(base_health) / 12
                )

            head = Bodypart(
                name="head", health=get_health(Bodypart.parts_health["head"])
            )
            self.body_parts.append(head)
            resource -= Bodypart.parts_costs["head"]

            if resource < Bodypart.parts_costs["torso"]:
                return
            torso = Bodypart(
                name="torso", health=get_health(Bodypart.parts_health["torso"])
            )
            self.body_parts.append(torso)
            resource -= Bodypart.parts_costs["torso"]

            if resource < Bodypart.parts_costs["leg"]:
                return
            if resource >= Bodypart.parts_costs["wings"] and resource < (
                Bodypart.parts_costs["wings"] + Bodypart.parts_costs["leg"]
            ):
                wings = Bodypart(
                    name="wings", health=get_health(Bodypart.parts_health["wings"])
                )
                self.body_parts.append(wings)
                resource -= Bodypart.parts_costs["wings"]
                return
            if resource < Bodypart.parts_costs["leg"] * 2:
                if resource < Bodypart.parts_costs["leg"]:
                    return
                else:
                    leg = Bodypart(
                        name="leg", health=get_health(Bodypart.parts_health["leg"])
                    )
                    self.body_parts.append(leg)
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

        self.descrption = self.create_description()

        # super().__init__(name, body_parts)

    def create_description(self):
        unique_descriptions = {
            ("head",): [
                f"{self.name} is just a rolling head that really wants to take a bite of you.",
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
                f"How many monsters does it take to screw in a lightbulb? One more than {self.name}, since that one doesn't have any limbs.",
            ],
            ("head", "torso", "leg"): [
                f"This monster is a head hopping around on a single leg. What an achievement in locomotion!",
                f"It's a head propped hilariously by a single leg. Nevertheless, it can and will try to bite/claw you.",
            ],
            ("head", "torso", "leg", "leg", "leg"): [
                f"{self.name} is tri-pedal.",
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

        # uniques
        if body_parts_names in unique_descriptions:
            descrption = random.choice(unique_descriptions[body_parts_names]) + " "

        # detailed head descrption
        if random.random() > 0.75:
            head_descr = [
                f"It has an elongated, canine-like head.",
                f"The monester's head is rather large for its torso.",
                f"{self.name} has a small, lizard-like head with bulging eyes.",
                f"{self.name}'s enormously huge eyes pierce into your soul.",
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
            elif random.random() > 0.2:
                leg_descr = [f"It's single-legged.", f"The monster has only one limb."]
                descrption += random.choice(leg_descr) + " "

        if descrption.strip() == "":
            descrs = [
                f"This sure is a monster.",
                f"The {self.name} is quite a monster.",
                f"{self.name} is fairly typical for a monster.",
            ]
            descrption = random.choice(descrs)

        return descrption

    def __str__(self):
        return f"""{self.name}
        {', '.join([x.__str__() for x in self.body_parts if x.current_health > 0])}
        {self.descrption}"""


print(Monster(danger_rating=random.normal(100, 50)))
# print(Monster(danger_rating=10))
