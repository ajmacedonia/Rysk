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
        self.color = None
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
        # TRUE if a full frame is ready to be read
        self.f_ready_to_read = False

    def reload(self):
        """Re-initialize certain attributes."""
        width = utilities.WINDOW[0] // utilities.MAX_PLAYERS
        height = utilities.WINDOW[1] // 2
        self.pos = (width * self.index, height)
        sprite = utilities.load_image(PLAYER_SPRITE[self.index])
        self.sprite = pygame.transform.scale(sprite, (width, height))
        self.color = self.sprite.get_at((0, 50))

    def set_focus(self, territory, scale):
        t = pygame.transform.scale(territory, scale)
        for y in range(scale[1]):
            for x in range(scale[0]):
                c = t.get_at((x, y))
                if c != pygame.Color(0, 0, 0, 0):
                    t.set_at((x, y), pygame.Color(self.color.r,
                                                  self.color.g,
                                                  self.color.b, c.a))
        self.focus = t

    def send_data(self, data):
        self.sendq += data

    def recv_data(self, data, f_ready):
        self.recvq += data
        self.f_ready_to_read = f_ready

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
