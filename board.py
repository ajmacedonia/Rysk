import random
from collections import namedtuple

import pygame

import utilities
from input import is_left_clicked, get_mouse_pos, is_key_pressed
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
RYSK_FRAME_START_GAME = 1
RYSK_FRAME_ADD_PLAYER = 2
RYSK_FRAME_TERRITORY_CLICK = 3
RYSK_FRAME_DICE_ROLL = 4

# RYSK game states
INITIAL_ARMY_PLACEMENT = 0


class Board:
    def __init__(self, window):
        self.window = window
        self.f_host = False
        self.local_player = None
        self.players = []
        self.objects = []

        self.bg = pygame.transform.scale(utilities.load_image('continents_v2.png'),
                                         self.window)
        self.fg = None
        self.state = None
        self.stage = 1

    def state_initial_army_placement(self):
        if self.stage == 1:
            d = input("Everyone rolls 1 die to determine turn order. Red or white (r/w)?: ")
            if d == 'r':
                reds, whites = utilities.roll_dice(1, 0)
            else:
                reds, whites = utilities.roll_dice(0, 1)
            self.local_player.reds, self.local_player.whites = reds, whites
            self.local_player.f_rolled = True

            if self.f_host:
                frame = self.send_dice_roll(None, self.local_player.id,
                                            reds, whites, send=False)
                self.send_to_all_players(frame, [self.local_player])
            else:
                self.send_dice_roll(self.local_player, self.local_player.id,
                                    reds, whites)
            self.stage = 2

        if self.stage == 2:
            for p in self.players:
                if not p.f_rolled:
                    return
            self.stage = 3

        if self.stage == 3:
            print("Reached stage 3")
            pass

    def get_player_by_id(self, player_id):
        for p in self.players:
            if p.id == player_id:
                return p
        return None

    def add_player(self, player_id, local, sock=None, index=None):
        new_player = Player(player_id or random.randint(1, 255))
        new_player.index = index if index is not None else len(self.players)
        new_player.f_local = local
        new_player.sock = sock
        new_player.reload()
        # when a new client joins the lobby
        if self.f_host and not new_player.f_local:
            # introduce everyone
            self.send_init_game(new_player)
            for p in self.players:
                self.send_add_player(new_player, p)
                if p is not self.local_player:
                    self.send_add_player(p, new_player)
        if self.local_player is None and local is True:
            self.local_player = new_player
        self.players.append(new_player)

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

    def send_start_game(self, player):
        frame = bytearray(1)
        frame[0] = RYSK_FRAME_START_GAME
        player.send_data(frame)
        print(f"Sent START_GAME ({len(frame)} bytes)")

    def parse_start_game(self, player):
        frame_len = 1
        player.recvq = player.recvq[frame_len:]
        print(f"Received START_GAME")
        self.state = INITIAL_ARMY_PLACEMENT

    def send_territory_click(self, player, territory_id, send=True):
        frame = bytearray(1)
        frame[0] = RYSK_FRAME_TERRITORY_CLICK
        frame.append(player.id)
        frame.extend(territory_id)
        if send:
            player.send_data(frame)
            print(f"Sent TERRITORY_CLICK ({len(frame)} bytes): player_id "
                  f"{player.id}, territory_id {territory_id}")
        return frame

    def parse_territory_click(self, player):
        frame_len = 6
        frame = player.recvq[:frame_len]
        p = self.get_player_by_id(frame[1])
        r, g, b, a = frame[2:frame_len]
        color = (r, g, b, a)
        territory = utilities.load_image(TERRITORY.get(color))
        if territory:
            p.set_focus(territory, self.window)
        player.recvq = player.recvq[frame_len:]
        print(f"Received TERRITORY_CLICK ({frame_len} bytes): player_id "
              f"{player.id}, territory_id {color}")
        return frame

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
        frame = player.recvq[:frame_len]
        player_id, index = frame[1:3]
        self.add_player(player_id, False, index=index)
        player.recvq = player.recvq[frame_len:]
        print(f"Received ADD_PLAYER ({frame_len} bytes): player id {player_id}, "
              f"index {index}")
        return frame

    def send_dice_roll(self, player, player_id, reds, whites, send=True):
        frame = bytearray(1)
        frame[0] = RYSK_FRAME_DICE_ROLL
        frame.append(player_id)
        frame.append(len(reds))
        for roll in reds:
            frame.append(roll)
        frame.append(len(whites))
        for roll in whites:
            frame.append(roll)
        if send:
            player.send_data(frame)
            print(f"Sent DICE_ROLL ({len(frame)} bytes): player_id {player_id}, "
                  f"reds {reds}, whites {whites}")
        return frame

    def parse_dice_roll(self, player):
        frame_len = 3
        player_id = player.recvq[1]
        p = self.get_player_by_id(player_id)
        num_reds = player.recvq[2]
        p.reds = list(player.recvq[frame_len:frame_len+num_reds])
        frame_len += num_reds
        num_whites = player.recvq[frame_len]
        frame_len += 1
        p.whites = list(player.recvq[frame_len:frame_len+num_whites])
        frame_len += num_whites
        print(f"Received DICE_ROLL ({frame_len} bytes): player_id {player_id}, "
              f"reds {p.reds}, whites {p.whites}")
        p.f_rolled = True
        frame = player.recvq[:frame_len]
        player.recvq = player.recvq[frame_len:]
        return frame

    def send_to_all_players(self, data, exceptions=None):
        """Send some data to all players."""
        for p in self.players:
            if exceptions is not None and p not in exceptions:
                p.send_data(data)

    def update(self):
        # check for left clicks on anything
        if is_left_clicked():
            pos = get_mouse_pos()
            color = tuple(self.bg.get_at(pos))

            # highlight a territory when clicked
            if TERRITORY.get(color):
                print(f"pos: {pos}, color: {color}, state: {TERRITORY.get(color)}")
                territory = utilities.load_image(TERRITORY.get(color))
                if territory:
                    self.local_player.set_focus(territory, self.window)
                    if self.f_host:
                        # send to all players
                        frame = self.send_territory_click(self.local_player,
                                                          color, send=False)
                        self.send_to_all_players(frame,
                                                 exceptions=[self.local_player])
                    else:
                        # send to server
                        self.send_territory_click(self.local_player, color)

        # receive from all players
        for player in self.players:
            while player.recvq:
                frame_type = player.recvq[0]
                if frame_type == RYSK_FRAME_INIT_GAME:
                    self.parse_init_game(player)
                elif frame_type == RYSK_FRAME_START_GAME:
                    self.parse_start_game(player)
                elif frame_type == RYSK_FRAME_ADD_PLAYER:
                    self.parse_add_player(player)
                elif frame_type == RYSK_FRAME_TERRITORY_CLICK:
                    frame = self.parse_territory_click(player)
                    self.send_to_all_players(frame, exceptions=[player])
                elif frame_type == RYSK_FRAME_DICE_ROLL:
                    self.parse_dice_roll(player)

        # run game state specific logic
        if self.state is None:
            if self.f_host and is_key_pressed('s'):
                self.state = INITIAL_ARMY_PLACEMENT
                f = bytearray(1)
                f[0] = RYSK_FRAME_START_GAME
                self.send_to_all_players(f, exceptions=[self.local_player])
        elif self.state == INITIAL_ARMY_PLACEMENT:
            self.state_initial_army_placement()

    def draw(self, window):
        # draw background
        if self.bg:
            window.blit(self.bg, (0, 0))

        # draw various objects (buttons, etc.)
        for obj in self.objects:
            window.blit(obj.surf, obj.pos)

        # draw player stuff
        for player in self.players:
            if player.focus is not None:
                window.blit(player.focus, (0, 0))
            if player.sprite is not None:
                window.blit(player.sprite, player.pos)

    def quit(self):
        for p in self.players:
            if p.sock is not None:
                p.sock.close()