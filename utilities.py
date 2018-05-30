import os
import pygame

# FS
ROOT_DIR = os.path.split(os.path.abspath(__file__))[0]
IMAGES_DIR = os.path.join(ROOT_DIR, "images")

# colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
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


# ================
# Pygame wrappers
# ================
def load_image(name):
    """Loads a pygame image and returns it."""
    image = None
    try:
        fullname = os.path.join(IMAGES_DIR, name)
        image = pygame.image.load(fullname)
        # image = image.convert()
    except:
        print("Failed to load {0}".format(fullname))
    return image
