import pygame
from utilities import load_image

CARD_POS_DOWN = 0
CARD_POS_UP = 1
CARD_POS_FLIPPED = 2


class Player:
    def __init__(self, color: str, pos: tuple):
        self.color = color
        self.surface = load_image("playercard_{0}.png".format(color))
        self.pos = pos
        self.curr_pos = 1

        x, y = self.pos[0], self.pos[1] + self.surface.get_height()
        self.positions = [(x, y), self.pos]

    def _next_pos(self):
        x, y = self.pos[0], self.pos[1] + self.surface.get_height() - 5
        positions = [(x, y), self.pos]
        i = 0
        while True:
            yield positions[i]
            i = (i + 1) % len(positions)

    def _slide_card(self):
        self.curr_pos = (self.curr_pos + 1) % len(self.positions)
        self.pos = self.positions[self.curr_pos]

    def clicked(self):
        self._slide_card()
