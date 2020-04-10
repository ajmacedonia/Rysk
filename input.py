import pygame

KEY_LEFT = pygame.K_LEFT
KEY_RIGHT = pygame.K_RIGHT
KEY_UP = pygame.K_UP
KEY_DOWN = pygame.K_DOWN
KEY_ESCAPE = pygame.K_ESCAPE
SPECIAL_CHARS = (KEY_LEFT, KEY_RIGHT, KEY_UP, KEY_DOWN, KEY_ESCAPE)
keypress = {}
mouse_buttons = [None] * 4
mouse_buttons_prev = [None] * 4


def update_input():
    global keypress
    global mouse_buttons
    global mouse_buttons_prev

    # clear key presses
    for key in keypress.keys():
        keypress[key] = False

    mouse_buttons_prev[:] = mouse_buttons[:]

    #  record key presses
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            keypress[event.key] = True
        elif event.type == pygame.KEYUP:
            keypress[event.key] = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_buttons[event.button] = True
        elif event.type == pygame.MOUSEBUTTONUP:
            mouse_buttons[event.button] = False
        elif event.type == pygame.QUIT:
            keypress[pygame.K_ESCAPE] = True


def is_key_pressed(key):
    """Returns True if key is currently being pressed."""
    return keypress.get(key, False)


def is_left_clicked():
    """"Returns True if left mouse button is down."""
    return mouse_buttons_prev[1] and not mouse_buttons[1]


def is_right_clicked():
    """"Returns True if right mouse button is down."""
    return mouse_buttons_prev[3] and not mouse_buttons[3]


def get_mouse_pos():
    return pygame.mouse.get_pos()
