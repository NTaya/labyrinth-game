from inventory import Inventory
from items import Item
from entity import Entity, Bodypart, Monster, Player
from menu import Menu
from util import COLORS, hide_color_if_low_lvl, game_over

from typing import Union
import numpy as np
import random


numeric_att_buffs = {
    "death": 1.25,
    "cure": 0.8,
    "attack": 1.5,
}

monster_ai = ["dumb", "good", "smart"]


class Attack:
    """Attack phase."""

    def __init__(
        self,
        defender: Entity,
        attacker: Entity,
        target_part: Bodypart,
        attacking_part: Union[Bodypart, Item],
        att_pwr,
        def_pwr,
        att_buffs=[],
        def_buffs=[],
        chance_to_hit=None,
    ):
        self.defender = defender
        self.attacker = attacker
        self.target_part = target_part
        self.attacking_part = attacking_part
        self.att_pwr = att_pwr
        self.def_pwr = def_pwr
        self.att_buffs = attacking_part.att_buffs
        self.def_buffs = target_part.def_buffs
        if chance_to_hit is None:
            if isinstance(attacking_part, Item):
                if "bonus_to_hit" in att_buffs:
                    bonus = attacking_part.bonus_to_hit
                else:
                    bonus = 0
            else:
                bonus = 0

            self.chance_to_hit = min(
                0.5
                + bonus
                + self.target_part.max_health
                / sum([x.max_health for x in defender.body_parts]),
                1,
            )
        else:
            self.chance_to_hit = chance_to_hit

    def attack(self, action_after=None):
        print(f"DEBUG: att_buffs: {self.att_buffs}")
        for buff in self.att_buffs:
            if buff in numeric_att_buffs.keys():
                self.att_pwr += numeric_att_buffs[buff]

        defense = Defense(
            self.defender,
            self.attacker,
            self.target_part,
            self.attacking_part,
            self.att_pwr,
            self.def_pwr,
            self.att_buffs,
            self.def_buffs,
        )

        if isinstance(self.defender, Player):
            if action_after == "Evade":
                print(f"Monster attacks! Player tries to evade...")
                defense.evade()
            elif action_after == "Defend":
                (f"Monster attacks! Player defends...")
                defense.defend()

        else:
            if self.chance_to_hit > np.random.random():
                if np.random.random() < 0.4:
                    print(f"{self.attacker.name} attacks! Monster tries to evade...")
                    defense.evade()
                else:
                    print(f"{self.attacker.name} attacks! Monster defends...")
                    defense.defend()
            else:
                print(f"{self.attacker.name}'s attack missed.")


class Defense(Attack):
    """Defense phase."""

    def __init__(
        self,
        defender: Entity,
        attacker: Entity,
        target_part: Bodypart,
        attacking_part: Union[Bodypart, Item],
        att_pwr,
        def_pwr,
        att_buffs,
        def_buffs,
        chance_to_hit=0,
    ):
        super().__init__(
            defender,
            attacker,
            target_part,
            attacking_part,
            att_pwr,
            def_pwr,
            att_buffs,
            def_buffs,
            chance_to_hit,
        )

    def proc_damage(self):
        # attack buffs
        if "fire" in self.att_buffs:
            possible_narration = [
                f"{self.attacker.name}'s {self.attacking_part.name} burns {self.defender.name}'s {self.target_part.name}!",
                f"{self.attacker.name}'s {self.attacking_part.name} sets {self.defender.name}'s {self.target_part.name} on fire.",
            ]
            print(np.random.choice(possible_narration))
            if "fire" in self.def_buffs:
                self.target_part.def_debuffs["burn_weak"] += 2
            else:
                self.target_part.def_debuffs["burn"] += 2

        if "ice" in self.att_buffs:
            possible_narration = [
                f"{self.attacker.name}'s {self.attacking_part.name} gives {self.defender.name}'s {self.target_part.name} a frostburn!",
                f"{self.attacker.name}'s {self.attacking_part.name} encases {self.defender.name}'s {self.target_part.name} in ice.",
            ]
            print(np.random.choice(possible_narration))
            if "ice" in self.def_buffs:
                self.target_part.def_debuffs["frostburn_weak"] += 1
            else:
                self.target_part.def_debuffs["frostburn"] += 1

        if "death" in self.att_buffs:
            possible_narration = [
                f"{self.attacker.name}'s {self.attacking_part.name} shoots a black bolt at {self.defender.name}'s {self.target_part.name}!",
                f"{self.attacker.name}'s {self.attacking_part.name} slices with a black cleave at {self.defender.name}'s {self.target_part.name}.",
            ]
            print(np.random.choice(possible_narration))
            self.att_pwr += np.random.normal(40, 10)

        if "arcane" in self.att_buffs:
            possible_narration = [
                f"{self.attacker.name}'s {self.attacking_part.name} shoots a magic missile at {self.defender.name}'s {self.target_part.name}!",
                f"{self.attacker.name}'s {self.attacking_part.name} additionally hits {self.defender.name}'s {self.target_part.name} with arcane energy.",
            ]
            print(np.random.choice(possible_narration))
            self.att_pwr *= 1 + np.random.random() / 2

        if "vampiric" in self.att_buffs:
            heal_strength = self.att_pwr / 8
            # if attacking part not at full health and is damaged enough
            if isinstance(self.attacking_part, Item) or (
                self.attacking_part.max_health - self.attacking_part.current_health
                >= heal_strength
            ):
                possible_narration = [
                    f"{self.attacker.name}'s {self.attacking_part.name} restored a bit of health from the attack!",
                    f"{self.attacker.name}'s {self.attacking_part.name} feeds on {self.defender}'s {self.target_part.name} pain.",
                ]
                print(np.random.choice(possible_narration))
                self.heal_part(self.attacking_part, heal_strength)
            else:
                parts_missing_health = {}
                for part in self.attacker.body_parts:
                    parts_missing_health[part] = (
                        self.target_part.max_health - self.target_part.current_health
                    )
                most_damaged_part = max(
                    parts_missing_health, key=parts_missing_health.get
                )
                possible_narration = [
                    f"{self.attacker.name}'s {self.attacking_part.name} restored a bit of health to their {most_damaged_part.name}.",
                    f"{self.attacker.name}'s {self.attacking_part.name} fed their {most_damaged_part.name} on {self.defender.name}'s {self.target_part.name} pain.",
                ]
                print(np.random.choice(possible_narration))
                self.heal_part(
                    most_damaged_part,
                    heal_strength,
                )

        if "poison" in self.att_buffs:
            possible_narration = [
                f"{self.attacker.name}'s {self.attacking_part.name} poisons {self.defender.name}'s {self.target_part.name}!",
                f"{self.attacker.name}'s {self.attacking_part.name} poisons {self.defender.name}'s {self.target_part.name}.",
            ]
            print(np.random.choice(possible_narration))
            if "poison" in self.def_buffs:
                self.target_part.def_debuffs["poison_weak"] += 2
            else:
                self.target_part.def_debuffs["poison"] += 2

        if "corruption" in self.att_buffs:
            corruption_type = 1 if random.random() < 0.5 else 0
            if corruption_type:
                self.target_part = random.choice(self.defender.body_parts)
                possible_narration = [
                    f"{self.attacker.name}'s {self.attacking_part.name} creates a small ripple in reality. It actually hit {self.defender.name}'s {self.target_part.name}!",
                    f"{self.attacker.name}'s {self.attacking_part.name} l̸̢̇a̸̢̭͑͛ṇ̶̒ď̸̹s̴͍̑ ̷̣͔̐a̵͙̣͛̉ ̸͖̂ḧ̶͖̜́i̸͖͉̿t̶̪́. on {self.defender.name}'s {self.target_part.name}.",
                    f"{self.attacker.name}'s {self.attacking_part} hits {self.defender}'s {self.target_part}!",
                ]
            else:
                possible_narration = [
                    f"{self.attacker.name}'s {self.attacking_part.name} spreads corruption through {self.defender.name}'s body.",
                ]

            print(np.random.choice(possible_narration))

        # defense buffs

        # main event
        self.target_part.current_health -= int(self.att_pwr)

        # health check
        if self.target_part.current_health <= 0:
            if (
                self.target_part.name == "head" or self.target_part.name == "torso"
            ) and isinstance(self.defender, Player):
                game_over()
            self.target_part.current_health = 0
            return 0
        return self.target_part.current_health

    def heal_part(self, target_part, pwr):
        target_part.current_health = int(
            min(self.target_part.current_health + pwr, self.target_part.max_health)
        )
        return target_part.current_health

    def defend(self):
        self.att_pwr = np.random.normal(self.att_pwr, self.att_pwr / 10)
        self.def_pwr = np.random.normal(self.def_pwr, self.def_pwr / 10)
        self.att_pwr = int(max(self.att_pwr - (self.def_pwr / 1.9), 1))
        print(f"Defense reduced damage to around {self.att_pwr}.")
        return self.proc_damage()

    def evade(self):
        ev_rating = self.defender.ev_rating
        """Evasion rating should be between 0 and 75. 100 = 100% chance to evade."""
        if "speed" in self.att_buffs:
            ev_rating -= 10
        if "speed" in self.def_buffs:
            ev_rating += 10
        if ev_rating > 75:
            ev_rating = 75

        if ev_rating / 100 < np.random.random():
            print(f"Evasion failed. Around {self.att_pwr} damage dealt.")
            self.proc_damage()
        else:
            print("Evasion succeeded.")

        return self.target_part.current_health


def battle_playground():
    player = Player()
    monster = Monster(danger_rating=50)
    go_first = 1 if player.speed > monster.speed else 0
    turn = go_first
    show_inventory = False
    show_monster_description = True
    show_non_hands = True
    target_part = np.random.choice(
        [x for x in monster.body_parts if x.current_health > 0]
    )
    curr_health = target_part.current_health
    guidewatch = player.inventory.guidewatch

    # DEBUG:
    for part in monster.body_parts:
        part.att_buffs += monster.att_buffs

    while True:
        print(f"\nTurn {turn}.")
        # if monster's turn
        if turn % 2:
            print(f"{COLORS['cyan']} Monster's turn. {COLORS['reset']}")
            attacking_part = np.random.choice(
                [
                    part
                    for part in monster.body_parts
                    if part.current_health > 0 and part.name != "torso"
                ]
            )
            target_part = np.random.choice(
                [part for part in player.body_parts if part.current_health > 0]
            )
            print(
                f"Monster targets {player.name}'s {target_part.name} with its {attacking_part.name}!"
            )
            options = ["Defend", "Evade"]
            answer = Menu("", options).answer

            att_pwr = attacking_part.att_pwr
            def_pwr = target_part.def_pwr

            attack_phase = Attack(
                player,
                monster,
                target_part,
                attacking_part,
                att_pwr,
                def_pwr,
                attacking_part.att_buffs,
                target_part.def_buffs,
            )

            if answer == "Defend":
                attack_phase.attack(action_after="Defend")
            else:
                attack_phase.attack(action_after="Evade")

            turn += 1

        # if player's turn
        else:
            print(f"{COLORS['cyan']} {player.name}'s turn. {COLORS['reset']}")
            # show health & other stats
            print("Player's health: ")
            for part in player.body_parts:
                print(part, end=", ")
                if (
                    guidewatch.level
                    >= guidewatch.options_levels["self_basic_stats_info"]
                ):
                    equipment = player.inventory.items[part.inventory_name]
                    if equipment != COLORS["reset"] + " None":
                        print(
                            f"att_pwr: {part.att_pwr + equipment.att_pwr}, def_pwr: {part.def_pwr + equipment.def_pwr}",
                            end=", ",
                        )
                        if part.att_buffs != [] or part.def_buffs != []:
                            print(
                                f"buffs: {list(set(part.att_buffs + part.def_buffs))}",
                                end=", ",
                            )
                        else:
                            print(f"buffs: []", end=", ")
                        if (
                            list(part.att_debuffs.keys()) != []
                            or list(part.def_debuffs.keys()) != []
                        ):
                            print(
                                f"debuffs: {list(set(list(part.att_debuffs.keys()) + list(part.def_debuffs.keys())))}",
                                end=";",
                            )
                        else:
                            print(f"debuffs: []", end=";")

                    else:
                        print(
                            f"att_pwr: {part.att_pwr}, def_pwr: {part.def_pwr}",
                            end=", ",
                        )
                        if part.att_buffs != [] or part.def_buffs != []:
                            print(
                                f"buffs: {list(set(list(part.att_buffs + part.def_buffs)))}",
                                end=", ",
                            )
                        else:
                            print(f"buffs: []", end=", ")
                        if (
                            list(part.att_debuffs.keys()) != []
                            or list(part.def_debuffs.keys()) != []
                        ):
                            print(
                                f"debuffs: {list(set(list(part.att_debuffs.keys()) + list(part.def_debuffs.keys())))}",
                                end=";",
                            )
                        else:
                            print(f"debuffs: []", end=";")
                print()
            # show monster
            monster.show_description(
                player.inventory.guidewatch,
                print_text_description=show_monster_description,
            )
            show_monster_description = False
            # show inventory
            if show_inventory:
                player.inventory.show_inventory()

            options = []
            hands_in_options = False

            base_options = [
                COLORS["cyan"] + "Show/hide inventory" + COLORS["reset"],
                COLORS["cyan"] + "Show/hide att other than w/hands" + COLORS["reset"],
                "Set guidewatch_lvl to 0",
                "Set guidewatch_lvl to 100",
                "Fill inventory",
                "Empty inventory",
            ]

            options.extend(base_options)

            body_part_options = {}
            for part in player.body_parts:
                if part.current_health > 0:
                    body_part_options[part.name] = part

            for option in body_part_options.keys():
                if option not in ["left arm", "right arm", "torso"]:
                    if show_non_hands:
                        options.append(f"Attack with your {option}")
                else:
                    if not hands_in_options and (
                        "left arm" in body_part_options.keys()
                        or "right arm" in body_part_options.keys()
                    ):
                        weapon = player.inventory.items["hands"]
                        if weapon == COLORS["reset"] + " None":
                            options.append("Attack with your bare hands")
                        else:
                            options.append(
                                f"Attack with {hide_color_if_low_lvl(weapon, guidewatch)}"
                            )
                        hands_in_options = True

            answer = Menu("", options).answer

            if answer == COLORS["cyan"] + "Show/hide inventory" + COLORS["reset"]:
                show_inventory ^= True
                turn -= 1

            elif (
                answer
                == COLORS["cyan"] + "Show/hide att other than w/hands" + COLORS["reset"]
            ):
                show_non_hands ^= True
                turn -= 1

            elif answer == "Set guidewatch_lvl to 0":
                guidewatch.level = 0
                turn -= 1

            # elif answer == "Set guidewatch_lvl to 3":
            #     guidewatch.level = 3
            #     turn -= 1

            elif answer == "Set guidewatch_lvl to 100":
                guidewatch.level = 100
                turn -= 1

            elif answer == "Fill inventory":
                player.inventory.fill()
                turn -= 1

            elif answer == "Empty inventory":
                player.inventory.empty()
                turn -= 1

            elif (
                answer == "Attack with your bare hands"
                or answer
                == f"Attack with {hide_color_if_low_lvl(player.inventory.items['hands'], player.inventory.guidewatch)}"
            ):
                arms = [
                    x
                    for x in player.body_parts
                    if x.name in ["left arm", "right arm"]
                    if x.current_health > 0
                ]
                att_pwr = sum(i.att_pwr for i in arms)
                attacking_part = arms[0]
                # if the player has a weapon
                weapon = player.inventory.items["hands"]
                if (
                    answer
                    == f"Attack with {hide_color_if_low_lvl(weapon, player.inventory.guidewatch)}"
                ):
                    att_pwr += weapon.att_pwr
                    attacking_part = weapon
                    att_buffs = weapon.att_buffs

                options = []
                enemy_body_parts = {x.name: x for x in monster.body_parts}
                new_enemy_body_parts = {}
                for part_name, part in enemy_body_parts.items():
                    if part.current_health <= 0:
                        continue
                    option = f"Target {part_name}"
                    guidewatch = player.inventory.guidewatch
                    if (
                        guidewatch.level
                        >= guidewatch.options_levels["show_chance_to_hit"]
                    ):
                        chance_to_hit = min(
                            0.5
                            + part.max_health
                            / sum([x.max_health for x in monster.body_parts]),
                            1,
                        )
                        option += f" (chance: {int(chance_to_hit * 100)}%)"
                    options.append(option)
                    new_enemy_body_parts[option] = enemy_body_parts[part_name]
                enemy_body_parts = new_enemy_body_parts

                options.append("Back")
                answer = Menu("", options).answer

                if answer == "Back":
                    turn -= 1
                else:
                    target_part = enemy_body_parts[answer]
                    def_pwr = target_part.def_pwr + monster.bonus_def
                    attack_phase = Attack(
                        monster, player, target_part, attacking_part, att_pwr, def_pwr
                    )
                    attack_phase.attack()

            # attack with non-hands
            else:
                # option = f"Attack with your {option}"
                attacking_part = answer.split("Attack with your ")[1]
                body_part = [x for x in player.body_parts if x.name == attacking_part][
                    0
                ]
                if attacking_part in ("left leg", "right leg"):
                    weapon = player.inventory.items["pants"]
                else:
                    weapon = player.inventory.items[attacking_part]
                att_pwr = body_part.att_pwr
                if weapon != COLORS["reset"] + " None":
                    att_pwr += weapon.att_pwr
                    attacking_part = weapon
                else:
                    attacking_part = [
                        x for x in player.body_parts if x.name == attacking_part
                    ][0]

                options = []
                enemy_body_parts = {x.name: x for x in monster.body_parts}
                for part_name, part in enemy_body_parts.items():
                    if part.current_health <= 0:
                        continue
                    option = f"Target {part_name}"
                    guidewatch = player.inventory.guidewatch
                    if (
                        guidewatch.level
                        >= guidewatch.options_levels["show_chance_to_hit"]
                    ):
                        chance_to_hit = min(
                            0.5
                            + part.max_health
                            / sum([x.max_health for x in monster.body_parts]),
                            1,
                        )
                        option += f" (chance: {int(chance_to_hit * 100)}%)"
                    options.append(option)
                    enemy_body_parts[option] = enemy_body_parts.pop(part_name)
                options.append("Back")
                answer = Menu("", options).answer

                if answer == "Back":
                    turn -= 1
                else:
                    target_part = enemy_body_parts[answer]
                    def_pwr = target_part.def_pwr + monster.bonus_def
                    attack_phase = Attack(
                        monster,
                        player,
                        target_part,
                        attacking_part,
                        att_pwr,
                        def_pwr,
                        attacking_part.att_buffs,
                        target_part.def_buffs,
                    )

                    attack_phase.attack()

            # defense debuffs, they proc after all other damage
            for part in monster.body_parts:
                if "burn_weak" in part.def_debuffs:
                    print(
                        f"{hide_color_if_low_lvl(monster.name, guidewatch)} is slighty protected from burns!"
                    )
                    part.current_health -= int(part.current_health / 25)
                if "burn" in part.def_debuffs:
                    print(
                        f"{hide_color_if_low_lvl(monster.name, guidewatch)} is burnt!"
                    )
                    part.current_health -= int(part.current_health / 12.5)
                if "poison_weak" in part.def_debuffs:
                    print(
                        f"{hide_color_if_low_lvl(monster.name, guidewatch)} is slighty protected from poison!"
                    )
                    part.current_health -= 15
                if "poison" in part.def_debuffs:
                    print(
                        f"{hide_color_if_low_lvl(monster.name, guidewatch)} is poisoned!"
                    )
                    part.current_health -= 30

            for part in player.body_parts:
                if "burn_weak" in part.def_debuffs:
                    print(
                        f"{player.name}'s {part.name} is burnt, but slighty protected from burns!"
                    )
                    part.current_health -= int(part.current_health / 25)
                if "burn" in part.def_debuffs:
                    print(f"{player.name}'s {part.name} is burnt!")
                    part.current_health -= int(part.current_health / 12.5)
                if "poison_weak" in part.def_debuffs:
                    print(
                        f"{player.name}'s {part.name} is poisoned, but slighty protected from poison!"
                    )
                    part.current_health -= 15
                if "poison" in part.def_debuffs:
                    print(f"{player.name}'s {part.name} is poisoned!")
                    part.current_health -= 30
            # minus length
            for part in player.body_parts + monster.body_parts:
                for debuff, length in part.att_debuffs.items():
                    if length > 0:
                        part.att_debuffs[debuff] -= 1
                for debuff, length in part.def_debuffs.items():
                    if length > 0:
                        part.att_debuffs[debuff] -= 1

            player_head = [x for x in player.body_parts if x.name == "head"][0]
            player_torso = [x for x in player.body_parts if x.name == "torso"][0]
            monster_head = [x for x in monster.body_parts if x.name == "head"][0]
            monster_torso = [x for x in monster.body_parts if x.name == "torso"][0]
            if all([part.current_health <= 0 for part in monster.body_parts]) or (
                player_head.current_health <= 0
                or player_torso.current_health <= 0
                or monster_head.current_health <= 0
                or monster_torso.current_health <= 0
            ):
                print("You won!")
                quit()
            turn += 1


if __name__ == "__main__":
    battle_playground()
