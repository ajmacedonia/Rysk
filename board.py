import socket
import random
from collections import namedtuple

import pygame

import utilities
from input import is_left_clicked, get_mouse_pos
from player import Player

TERRITORY = {
    # North America
    (255, 255, 0, 255): "Greenland_highlight.png",
    (255, 255, 1, 255): "NWTer_highlight.png",
    (255, 255, 2, 255): "Alaska_highlight.png",
    (255, 255, 3, 255): "Alberta_highlight.png",
    (255, 255, 4, 255): "Ontario_highlight.png",
    (255, 255, 5, 255): "EasternCan_highlight.png",
    (255, 255, 6, 255): "WestUS_highlight.png",
    (255, 255, 7, 255): "EastUS_highlight.png",
    (255, 255, 8, 255): "CentralAmerica_highlight.png",
    # South America
    (255, 127, 0, 255): "Argentina_highlight.png",
    (255, 127, 1, 255): "Brazil_highlight.png",
    (255, 127, 2, 255): "Peru_highlight.png",
    (255, 127, 3, 255): "Venezuela_highlight.png",
    # Africa
    (127, 127, 127, 255): "NorthAfrica_highlight.png",
    (128, 128, 128, 255): "Egypt_highlight.png",
    (129, 129, 129, 255): "EastAfrica_highlight.png",
    (130, 130, 130, 255): "CentralAfrica_highlight.png",
    (131, 131, 131, 255): "SouthAfrica_highlight.png",
    (132, 132, 132, 255): "Madagascar_highlight.png",
    # Europe
    (0, 0, 255, 255): "Iceland_highlight.png",
    (1, 0, 255, 255): "GreatBritain_highlight.png",
    (2, 0, 255, 255): "Scandanavia_highlight.png",
    (3, 0, 255, 255): "Russia_highlight.png",
    (4, 0, 255, 255): "NorthernEurope_highlight.png",
    (5, 0, 255, 255): "WesternEurope_highlight.png",
    (6, 0, 255, 255): "SouthernEurope_highlight.png",
    # Asia
    (0, 255, 0, 255): "Kamchatka_highlight.png",
    (1, 255, 0, 255): "Yakutsk_highlight.png",
    (2, 255, 0, 255): "Siberia_highlight.png",
    (3, 255, 0, 255): "Ural_highlight.png",
    (4, 255, 0, 255): "Irkutsk_highlight.png",
    (5, 255, 0, 255): "Mongolia_highlight.png",
    (6, 255, 0, 255): "Japan_highlight.png",
    (7, 255, 0, 255): "Afghanistan_highlight.png",
    (8, 255, 0, 255): "China_highlight.png",
    (9, 255, 0, 255): "MiddleEast_highlight.png",
    (10, 255, 0, 255): "India_highlight.png",
    (11, 255, 0, 255): "SoutheastAsia_highlight.png",
    # Australia
    (255, 0, 255, 255): "Indonesia_highlight.png",
    (255, 1, 255, 255): "NewGuinea_highlight.png",
    (255, 2, 255, 255): "WesternAustralia_highlight.png",
    (255, 3, 255, 255): "EasternAustralia_highlight.png"
}

Object = namedtuple('Object', ['surf', 'pos'])

# RYSK frame types
RYSK_FRAME_INIT_GAME = 0
RYSK_FRAME_ADD_PLAYER = 1
RYSK_FRAME_TERRITORY_CLICK = 2


class Board:
    PLAYER_COLORS = ["black", "blue", "magenta", "green"]

    def __init__(self, window):
        self.window = window
        self.is_host = False
        self.local_player = None
        self.players = []
        self.objects = []

        self.bg = pygame.transform.scale(utilities.load_image('continents_v2.png'),
                                         self.window)
        self.fg = None

    def add_player(self, player_id, local, sock=None, index=None):
        p = Player(player_id or random.randint(1, 255),
                   index or len(self.players))
        p.local = local
        p.sock = sock
        p.reload()
        if self.is_host and not p.local:
            self.send_init_game(p)
        if self.local_player is None and local is True:
            self.local_player = p
        self.players.append(p)

    def send_init_game(self, player):
        frame = bytearray(3)
        frame[0] = RYSK_FRAME_INIT_GAME
        frame[1] = player.id
        frame[2] = len(self.players)
        player.send_data(frame)
        print(f"Sent INIT_GAME ({len(frame)} bytes): player_id {player.id}, index {frame[-1]}")

    def parse_init_game(self, player):
        frame_len = 3
        player.id = player.recvq[1]
        player.index = player.recvq[2]
        player.recvq = player.recvq[frame_len:]
        print(f"Received INIT_GAME ({frame_len} bytes): player_id {player.id}, index {player.index}")
        player.reload()

    def send_territory_click(self, player, territory_id):
        frame = bytearray(5)
        frame[0] = RYSK_FRAME_TERRITORY_CLICK
        frame[1] = territory_id[0]
        frame[2] = territory_id[1]
        frame[3] = territory_id[2]
        frame[4] = territory_id[3]
        player.send_data(frame)
        print(f"Sent TERRITORY_CLICK ({len(frame)} bytes): territory_id {territory_id}")

    def parse_territory_click(self, player):
        frame_len = 5
        r = player.recvq[1]
        g = player.recvq[2]
        b = player.recvq[3]
        a = player.recvq[4]
        color = (r, g, b, a)
        territory = utilities.load_image(TERRITORY.get(color))
        if territory:
            player.focus = pygame.transform.scale(territory,
                                                  self.window)
        player.recvq = player.recvq[frame_len:]
        print(f"Received TERRITORY_CLICK ({frame_len} bytes): "
              f"territory_id {color}")

    def send_add_player(self, player, new_player):
        frame = bytearray(3)
        frame[0] = RYSK_FRAME_ADD_PLAYER
        frame[1] = new_player.id
        frame[2] = new_player.index
        player.send_data(frame)
        print(f"Sent ADD_PLAYER ({len(frame)} bytes): player id {frame[1]}, "
              f"index {frame[2]}")

    def parse_add_player(self, player):
        frame_len = 3
        player_id, index = player.recvq[1:3]
        self.add_player(id, False, index=index)
        print(f"Received ADD_PLAYER ({frame_len} bytes): player id {player_id}, "
              f"index {index}")

    def update(self):
        if is_left_clicked():
            pos = get_mouse_pos()
            color = tuple(self.bg.get_at(pos))

            # highlight a territory when clicked
            if TERRITORY.get(color):
                print(f"pos: {pos}, color: {color}, state: {TERRITORY.get(color)}")
                country = utilities.load_image(TERRITORY.get(color))
                if country:
                    self.fg = pygame.transform.scale(country, self.window)
                    if self.is_host:
                        # send to all players
                        for p in self.players:
                            self.send_territory_click(p, color)
                    else:
                        # send to server
                        self.send_territory_click(self.local_player, color)

        for player in self.players:
            if player.recvq:
                frame_type = player.recvq[0]
                if frame_type == RYSK_FRAME_INIT_GAME:
                    self.parse_init_game(player)
                elif frame_type == RYSK_FRAME_ADD_PLAYER:
                    self.parse_add_player(player)
                elif frame_type == RYSK_FRAME_TERRITORY_CLICK:
                    self.parse_territory_click(player)

    def draw(self, window):
        # draw background
        if self.bg:
            window.blit(self.bg, (0, 0))

        # draw foreground
        if self.fg:
            window.blit(self.fg, (0, 0))

        # draw various objects (buttons, etc.)
        for obj in self.objects:
            window.blit(obj.surf, obj.pos)

        # draw player stuff
        for player in self.players:
            if player.focus is not None:
                window.blit(player.focus, (0, 0))
            if player.sprite is not None:
                window.blit(player.sprite, player.pos)
