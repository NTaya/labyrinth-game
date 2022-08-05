import inquirer
import itertools
import sys
import pickle
import ctypes
import time

kernel32 = ctypes.windll.kernel32
kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)


class Menu:
    def __init__(self, title_text, options):
        questions = [
            inquirer.List(
                title_text,
                message=title_text,
                choices=options.keys(),
            ),
        ]

        options[inquirer.prompt(questions)[title_text]]()
