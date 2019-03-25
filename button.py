import pygame.freetype

import utilities
from input import is_left_clicked, get_mouse_pos


class Button:
    def __init__(self, text=None, pos=None):
        self.font = pygame.freetype.SysFont('comicsansms', 30)
        self.text = text
        self.text_surface, self.text_rect = self.font.render(self.text,
                                                             bgcolor=utilities.GREY)
        if pos:
            self.text_rect.topleft = pos

    def clicked(self):
        if is_left_clicked():
            pos = get_mouse_pos()
            if (self.text_rect.x <= pos[0] <= self.text_rect.x + self.text_rect.width and
                    self.text_rect.y <= pos[1] <= self.text_rect.y + self.text_rect.height):
                return True
        return False

    def draw(self, window):
        window.blit(self.text_surface, self.text_rect)

    @property
    def x(self):
        return self.text_rect.x

    @x.setter
    def x(self, x):
        self.text_rect.x = x

    @property
    def y(self):
        return self.text_rect.y

    @y.setter
    def y(self, y):
        self.text_rect.y = y

    @property
    def width(self):
        return self.text_rect.width

    @property
    def height(self):
        return self.text_rect.height
