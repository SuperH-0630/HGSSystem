import random


def random_color():
    color_lst = ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F']
    color = ""
    for i in range(6):
        color += random.choice(color_lst)
    return "#" + color
