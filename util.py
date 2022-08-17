# -- GENERAL --


COLORS = {
    "black": "\u001b[30m",
    "red": "\u001b[31m",
    "green": "\u001b[32m",
    "yellow": "\u001b[33m",
    "blue": "\u001b[34m",
    "magenta": "\u001b[35m",
    "cyan": "\u001b[36m",
    "white": "\u001b[37m",
    "reset": "\u001b[0m",
}


def func_wrapper(func, val):
    return lambda: func(val)


def check_if_subset(a, b):
    return not (set(a) - set(b))


def flatten(S):
    if S == [] or S == ():
        return S
    if isinstance(S[0], list) or isinstance(S[0], tuple):
        return flatten(S[0]) + flatten(S[1:])
    return S[:1] + flatten(S[1:])


# -- GAMEPLAY --


def game_over():
    print("Game Over")
    # TODO: delete save file, exit to main menu
    quit()


# -- ITEM --


def hide_color_if_low_lvl(item_name, guidewatch):
    return (
        COLORS["reset"] + " " + str(item_name)[5:]
        if guidewatch.level < guidewatch.options_levels["use_color"]
        else str(item_name)
    )
