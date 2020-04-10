import pygame
import utilities
import logging

CARD_POS_DOWN = 0
CARD_POS_UP = 1
CARD_POS_FLIPPED = 2


class Player:
    def __init__(self, player_id=None, name=""):
        self.ID = player_id
        self.name = name
        self.socket = None

        # True if the latest roll hasn't been processed
        self.f_new_roll = False
        # The latest attack roll
        self.attack_roll = []
        # The latest defense roll
        self.defense_roll = []
        # The number of armies available for placement
        self.n_free_armies = 0
        # The IDs of owned territories
        self.territories = set()

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"Player ID {self.ID}, name {self.name}, socket {self.socket}\n" \
               f"Territories: {self.territories}\n" \
               f"Last attack roll: {self.attack_roll}\n" \
               f"Last defense roll: {self.defense_roll}"

    def __eq__(self, other):
        return self.ID == other.ID

    def set_roll(self, attack: list, defense: list) -> None:
        self.attack_roll = attack
        self.defense_roll = defense
        self.f_new_roll = True

    def print_last_roll(self) -> str:
        return f"attack: {self.attack_roll}, defense: {self.defense_roll}"

    def add_territory(self, t) -> None:
        self.territories.add(t)
        logging.debug(f"{self.name} added territory ID {t}")

    def remove_territory(self, t) -> None:
        try:
            self.territories.remove(t)
        except KeyError:
            logging.exception(f"{self.name} tried to remove unowned {t.name}")


class Player2:
    def __init__(self, player_id=None):
        # player name
        self.name = ""
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
        # font for name display
        self.font = pygame.freetype.SysFont('comicsansms', 30)

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
        if self.sprite is not None:
            window.blit(self.sprite, self.pos)

        if self.focus is not None:
            window.blit(self.focus, (0, 0))

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
