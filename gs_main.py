import pygame
import pygame.freetype

import utilities
from gsm import Gamestate


class GSMain(Gamestate):

    def __init__(self):
        self.name = "GSMain"

        self.core = None
        self.background = None
        self.button = None
        self.button_color = None
        self.button_text = None
        self.text_surface = None
        self.text_rect = None
        self.font = None

    def initialize(self, core):
        self.core = core

        # create background
        self.background = core.load_image('haha.png')
        self.background = pygame.transform.scale(self.background,
                                                 (core.display_width, core.display_height))

        # create buttons
        self.button_text = "Host Game"
        self.font = pygame.freetype.SysFont("comicsansms", 50)
        self.text_surface, self.text_rect = self.font.render(self.button_text,
                                                             pygame.Color(*utilities.BLACK),
                                                             pygame.Color(*utilities.LIGHT_RED))
        self.text_rect.center = (core.display_width // 2, core.display_height // 2)

        return True

    def update(self):
        if self.core.is_left_clicked():
            pos = self.core.get_mouse_pos()
            if (self.text_rect.x <= pos[0] <= self.text_rect.x + self.text_rect.width and
                    self.text_rect.y <= pos[1] <= self.text_rect.y + self.text_rect.y + self.text_rect.height):
                self._gsm.set_next_state("GSPlay")
                self._gsm.shutdown = True

    def draw(self, display):
        # draw background
        display.blit(self.background, (0, 0))

        # draw buttons
        display.blit(self.text_surface, self.text_rect)