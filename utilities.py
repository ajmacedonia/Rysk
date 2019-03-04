import os
import random

import pygame


# FS
BASE_DIR = os.path.split(os.path.abspath(__file__))[0]
IMAGES_DIR = os.path.join(BASE_DIR, "images")

# colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (100, 100, 100)
LIGHT_GREY = (128, 128, 128)
RED = (200, 0, 0)
LIGHT_RED = (255, 0 ,0)
GREEN = (75, 200, 75)
LIGHT_GREEN = (0, 255, 0)
BLUE = (0, 0, 200)
LIGHT_BLUE = (0, 0, 255)
YELLOW = (200, 200, 0)
LIGHT_YELLOW = (255, 255, 0)

# keys
K_escape = '\x1b'


# =================
# Helper Functions
# =================
def load_image(name):
    """Loads a pygame image and returns it."""
    image = None
    try:
        fullname = os.path.join(IMAGES_DIR, name)
        image = pygame.image.load(fullname)
    except:
        print(f"Failed to load {name}")
    return image


def roll_dice(red, white):
    """
    Roll some number of red and white dice.
    :param red: Number of red dice to roll.
    :param white: Number of white dice to roll.
    :return: A pair of lists of the results [red], [white].
    """
    reds = [random.randint(1, 6) for _ in range(red)]
    whites = [random.randint(1, 6) for _ in range(white)]
    return reds, whites
