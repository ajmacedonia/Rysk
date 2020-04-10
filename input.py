import pygame

KEY_LEFT = pygame.K_LEFT
KEY_RIGHT = pygame.K_RIGHT
KEY_UP = pygame.K_UP
KEY_DOWN = pygame.K_DOWN
KEY_ESCAPE = pygame.K_ESCAPE
SPECIAL_CHARS = (KEY_LEFT, KEY_RIGHT, KEY_UP, KEY_DOWN, KEY_ESCAPE)
keypress = {}

MOUSE_BUFFER = 4
mouse_buttons = [None] * MOUSE_BUFFER
mouse_buttons_prev = [None] * MOUSE_BUFFER
LEFT_CLICK = 1
RIGHT_CLICK = 3


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
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button < MOUSE_BUFFER:
            mouse_buttons[event.button] = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button < MOUSE_BUFFER:
            mouse_buttons[event.button] = False
        elif event.type == pygame.QUIT:
            keypress[pygame.K_ESCAPE] = True


def is_key_pressed(key):
    """Returns True if key is currently being pressed."""
    return keypress.get(key, False)


def is_left_clicked():
    """"Returns True if left mouse button is down."""
    return mouse_buttons_prev[LEFT_CLICK] and not mouse_buttons[LEFT_CLICK]


def is_right_clicked():
    """"Returns True if right mouse button is down."""
    return mouse_buttons_prev[RIGHT_CLICK] and not mouse_buttons[RIGHT_CLICK]


def get_mouse_pos():
    return pygame.mouse.get_pos()
