import inquirer
import itertools
import sys
import pickle
import ctypes
import time

kernel32 = ctypes.windll.kernel32
kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)


class Menu:
    def __init__(self, title_text, options, param_to_save=None):
        if isinstance(options, dict):
            questions = [
                inquirer.List(
                    title_text,
                    message=title_text,
                    choices=options.keys(),
                ),
            ]
            self.answer = options[inquirer.prompt(questions)[title_text]]
            if callable(self.answer):
                self.answer = self.answer()
        else:
            questions = [
                inquirer.List(
                    title_text,
                    message=title_text,
                    choices=options,
                ),
            ]
            self.answer = inquirer.prompt(questions)[title_text]
