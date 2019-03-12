import pygame
import utilities

CARD_POS_DOWN = 0
CARD_POS_UP = 1
CARD_POS_FLIPPED = 2

PLAYER_SPRITE = ["playercard_black.png", "playercard_blue.png",
                 "playercard_magenta.png", "playercard_green.png"]


class Player:
    def __init__(self, player_id=None):
        # player ID assigned by Server
        self.id = player_id
        # player card, color, etc.
        self.index = None
        # player representation (player cards currently)
        self.sprite = None
        self.pos = None
        # currently highlighted territory
        self.focus = None

        # most recent dice rolls
        self.reds = []
        self.whites = []
        self.f_rolled = None

        # this is going to be refactored
        self.card_positions = self._gen_card_positions()

        # local player instance
        self.f_local = None
        # network socket
        self.sock = None
        # send and receive queues
        self.sendq = bytearray()
        self.recvq = bytearray()

    def reload(self):
        """Re-initialize certain attributes."""
        width = utilities.WINDOW[0] // utilities.MAX_PLAYERS
        height = utilities.WINDOW[1] // 2
        self.pos = (width * self.index, height)
        sprite = utilities.load_image(PLAYER_SPRITE[self.index])
        self.sprite = pygame.transform.scale(sprite, (width, height))

    def send_data(self, data):
        self.sendq += data

    def recv_data(self, data):
        self.recvq += data

    def update(self):
        pass

    def draw(self, window):
        pass

    def _gen_card_positions(self):
        x, y = self.pos[0], self.pos[1] + self.sprite.get_height() - 160
        positions = [(x, y), self.pos]
        i = 0
        while True:
            yield positions[i]
            i = (i + 1) % len(positions)

    def _slide_card(self):
        self.pos = next(self.card_positions)

    def clicked(self):
        self._slide_card()
