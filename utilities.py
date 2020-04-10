import os
import random

import pygame

# Game stuff
MAX_PLAYERS = 4
PLAYER_NAME_LEN_MAX = 16

# Misc
WINDOW = (1280, 960)
ADDR = ("localhost", 8080)

# Filesystem
BASE_DIR = os.path.split(os.path.abspath(__file__))[0]
IMAGES_DIR = os.path.join(BASE_DIR, "images")

# Colors
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
CYAN = (0, 255, 255)
YELLOW = (200, 200, 0)
LIGHT_YELLOW = (255, 255, 0)

# ANSI escape codes
ANSI_BLACK = '\u001b[30m'
ANSI_RED = '\u001b[31m'
ANSI_GREEN = '\u001b[32m'
ANSI_YELLOW = '\u001b[33m'
ANSI_BLUE = '\u001b[34m'
ANSI_MAGENTA = '\u001b[35m'
ANSI_CYAN = '\u001b[36m'
ANSI_WHITE = '\u001b[37m'
ANSI_RESET = '\u001b[0m'


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
