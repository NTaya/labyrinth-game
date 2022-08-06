import keyboard
import itertools
import sys
import pickle

from inventory import inventory_playground
from crafting import crafting_playground
from maps import map_playground
from menu import Menu


def start_new_session():
    print("Starting new session...")


def continue_session():
    print("Continuing session...")


def send_help():
    print("Sending help...")


def info_inventory_playground():
    print("Ok, before we start, a few quick notes.")
    print("Normally, you can equip items but not carry them.")
    print("You don't have the pockets deep enough to shove a sword or whatever here.")
    print("But you can equip a sword to have it in your hands.")
    print("To carry items, you need a backpack.")
    print("Counterintuitively, you can have up to four (4) backpacks.")
    print("Labyrinth allows you to carry plenty of weight.")
    print("Currently, you can't move items between backpacks,")
    print("but you can equip-unequip items to mimic that.")
    print("It will move to the first free backpack.")
    print()
    inventory_playground()


def exit_session():
    sys.exit()


options = {
    # "New game  ": start_new_session,
    # "Continue  ": continue_session,
    # "Help  ": send_help,
    "Inventory Playground  ": info_inventory_playground,
    "Crafting Playground  ": crafting_playground,
    "Map Playground ": map_playground,
    "Exit  ": exit_session,
}

title_text = "Select item: down button, then press space or enter."

main_menu = Menu(title_text, options)

# raise SystemExit(0)
