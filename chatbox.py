import pygame
import pygame.freetype

import utilities
from input import is_left_clicked, get_mouse_pos


class ChatBox:
    def __init__(self):
        self.focused = False
        self.history = ""
        self.current_input = ""
        self.font = pygame.freetype.SysFont('courier', 20)
        self.surface = utilities.load_image('chatbox.png')
        if self.surface:
            scale = (utilities.WINDOW[0] // 4, utilities.WINDOW[1] // 4)
            self.surface = pygame.transform.scale(self.surface, scale)
            self.surface.set_alpha(128)
        self.pos = (utilities.WINDOW[0] - self.surface.get_width(), 0)

    def get_input(self, key):
        if key == pygame.K_BACKSPACE:
            self.current_input = self.current_input[:-1]
        else:
            self.current_input += chr(key)

    def update(self):
        if is_left_clicked():
            pos = get_mouse_pos()
            if (self.pos[0] <= pos[0] <= self.pos[0] + self.surface.get_width() and
                self.pos[1] <= pos[1] <= self.pos[1] + self.surface.get_height()):
                self.focused = True
            else:
                self.focused = False

    def draw(self, window):
        if self.surface is not None:
            window.blit(self.surface, self.pos)
        if self.current_input:
            ts, tr = self.font.render(self.current_input)
            tr.x, tr.y = self.pos[0] + 20, self.pos[1] + 20
            window.blit(ts, tr)
