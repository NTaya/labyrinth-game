from numpy import random, ceil, floor, append
import typing
from items import Item
from menu import Menu


def craft(item1: Item, item2: Item):
    rand = random.random()
    if rand <= 0.5:
        use_ceil = False
        type_of = item1.type_of
    else:
        use_ceil = True
        type_of = item2.type_of

    attribute_num = (item1.attribute_num + item2.attribute_num) / 2
    if int(attribute_num) != attribute_num:  # if we got a decimal
        if use_ceil:
            attribute_num = int(ceil(attribute_num))
        else:
            attribute_num = int(floor(attribute_num))

    old_attributes = append(item1.attributes, item2.attributes)
    old_attributes = list(set(old_attributes))
    new_attributes = random.choice(old_attributes, int(attribute_num), replace=False)

    return Item(type_of=type_of, attribute_num=attribute_num, attributes=new_attributes)


result = ""
item1 = Item()
item2 = Item()


def regenerate_item1():
    global item1
    item1 = Item()
    crafting_playground()


def regenerate_item2():
    global item2
    item2 = Item()
    crafting_playground()


def craft_():
    global result
    result = craft(item1, item2)
    crafting_playground()


def set_crafted_as_item1():
    global item1
    global result
    item1 = result
    crafting_playground()


def set_crafted_as_item2():
    global item2
    global result
    item2 = result
    crafting_playground()


options = {
    "Craft!  ": craft_,
    "Regenerate Item 1  ": regenerate_item1,
    "Regenerate Item 2  ": regenerate_item2,
    "Set Crafted as Item 1  ": set_crafted_as_item1,
    "Set Crafted as Item 2  ": set_crafted_as_item2,
}


def crafting_playground():
    print(f"Item 1: {item1};\nItem 2: {item2};\nResult: {result}")
    text = ""
    Menu(text, options)
