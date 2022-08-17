import numpy as np


def get_damage(base_damage):
    return base_damage * (1 + 3)
    # + np.random.normal(
    #    float(base_damage), scale=float(base_damage) / 2
    # )


def get_defense(base_defense):
    return base_defense * (1 + 2)


print(get_defense(5))
