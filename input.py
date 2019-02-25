import pygame

KEY_LEFT = pygame.K_LEFT
KEY_RIGHT = pygame.K_RIGHT
KEY_UP = pygame.K_UP
KEY_DOWN = pygame.K_DOWN
KEY_ESCAPE = pygame.K_ESCAPE
SPECIAL_CHARS = (KEY_LEFT, KEY_RIGHT, KEY_UP, KEY_DOWN, KEY_ESCAPE)
keypress = {}
mouse_state = None


def update_input():
    global keypress
    global mouse_state

    # clear key presses
    for key in keypress.keys():
        keypress[key] = False

    #  record key presses
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            keypress[event.key] = True
        elif event.type == pygame.KEYUP:
            keypress[event.key] = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_state = (*event.pos, event.button)
        elif event.type == pygame.MOUSEBUTTONUP:
            mouse_state = (*event.pos, False)
        elif event.type == pygame.QUIT:
            keypress[pygame.K_ESCAPE] = True


def is_key_pressed(key):
    """Returns True if key is currently being pressed."""
    if key not in SPECIAL_CHARS:
        key = ord(key.lower())
    return keypress.get(key, False)


def is_left_clicked():
    """"Returns True if left mouse button is down."""
    return pygame.mouse.get_pressed()[0]


def get_mouse_pos():
    return pygame.mouse.get_pos()
