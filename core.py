import os
import pygame


class Core:
    """Basically just a container for anything most closely classified a "core engine" function."""

    KEY_LEFT = pygame.K_LEFT
    KEY_RIGHT = pygame.K_RIGHT
    KEY_UP = pygame.K_UP
    KEY_DOWN = pygame.K_DOWN
    KEY_ESCAPE = pygame.K_ESCAPE

    SPECIAL_CHARS = (KEY_LEFT, KEY_RIGHT, KEY_UP, KEY_DOWN, KEY_ESCAPE)

    def __init__(self, display_width, display_height):
        # filesystem info
        self.main_dir = os.path.split(os.path.abspath(__file__))[0]
        self.images_dir = os.path.join(self.main_dir, "images")

        # creating a Core initializes pygame
        pygame.init()

        # display info
        self.display_width = display_width
        self.display_height = display_height
        self.display = pygame.display.set_mode((self.display_width, self.display_height))

        self.__caption = None
        self.__icon = None

        self.load_fonts()

        # input handling
        self.__is_pressed = {}
        self.mouse = (0, 0, 0)
        self.run = True

    def set_caption(self, display_name):
        """Sets the title on the window."""
        self.__caption = display_name
        if self.__caption:
            pygame.display.set_caption(self.__caption)

    def set_icon(self, name):
        """Loads 'name' and sets it as the window icon."""
        self.__icon = self.load_image(name)
        if self.__icon:
            pygame.display.set_icon(self.__icon)

    def load_image(self, name):
        """Loads a pygame image and returns it."""
        image = None
        try:
            fullname = os.path.join(self.images_dir, name)
            image = pygame.image.load(fullname)
            # image = image.convert()
        except:
            print("Failed to load {0}".format(name))
        return image

    def load_fonts(self):
        """Loads some pygame fonts into the Core."""
        self.font_small = pygame.font.SysFont("comicsansms", 25)
        self.font_med = pygame.font.SysFont("comicsansms", 50)
        self.font_large = pygame.font.SysFont("comicsansms", 80)

    def message_to_screen(msg, color, y_displace=0, size="small"):
        text_surface, text_rect = create_text_objects(msg, color, size)
        text_rect.center = (display_width / 2), (display_height / 2) + y_displace
        self.display.blit(text_surface, text_rect)

    def is_key_pressed(self, key):
        """Returns True if key is currently being pressed."""
        if key not in self.SPECIAL_CHARS:
            key = ord(key.lower())

        return self.__is_pressed.get(key, False)

    def is_left_clicked(self):
        return self.mouse[2]

    def get_mouse_pos(self):
        return self.mouse[0], self.mouse[1]

    def update_input(self):
        for key in self.__is_pressed.keys():
            self.__is_pressed[key] = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.run = False
            if event.type == pygame.KEYDOWN:
                self.__is_pressed[event.key] = True
            if event.type == pygame.KEYUP:
                self.__is_pressed[event.key] = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                self.mouse = (*event.pos, event.button)
                print(self.mouse)
            if event.type == pygame.MOUSEBUTTONUP:
                self.mouse = (*event.pos, 0)
                print(self.mouse)