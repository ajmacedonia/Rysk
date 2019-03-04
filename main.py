# built-ins
import os
import random
import socket
import selectors

# external modules
import pygame

# custom modules
import utilities
from input import update_input, is_key_pressed, is_left_clicked, get_mouse_pos
from network import Network
from player import Player

# filesystem info
BASE_DIR = os.path.split(os.path.abspath(__file__))[0]
IMAGES_DIR = os.path.join(BASE_DIR, 'images')

# misc
WINDOW = (1280, 960)
SERVER_PORT = 9923
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
MAX_PLAYERS = 4


def load_image(name):
    """Loads a pygame image and returns it."""
    image = None
    try:
        path = os.path.join(IMAGES_DIR, name)
        image = pygame.image.load(path)
    except:
        print(f"Failed to load {name}")
    return image


def roll_dice(red, white):
    """
    Roll some number of red and white dice.
    :param red: Number of red dice to roll.
    :param white: Number of white dice to roll.
    :return: A pair of lists of the results [red], [white].
    """
    reds = [random.randint(1, 6) for _ in range(red)]
    whites = [random.randint(1, 6) for _ in range(white)]
    return reds, whites


STATE_INITIAL_ARMY_PLACEMENT = 0

# initial infantry count based on number of players
infantry_count = {
    2: 40,  # XXX see page 11
    3: 35,
    4: 30,
    5: 25,
    6: 20
}


# RYSK frame types
RYSK_FRAME_TERRITORY_CLICK = 0


class Board:
    PLAYER_COLORS = ["black", "blue", "magenta", "green"]

    def __init__(self):
        self.players = []
        self.country = None

    def add_player(self, sock):
        x = WINDOW[0] // MAX_PLAYERS
        y = WINDOW[1] // 2
        num_players = len(self.players)
        p = Player(self.PLAYER_COLORS[num_players], (x * num_players, y))
        p.surface = pygame.transform.scale(p.surface, (x, y))
        p.sock = sock
        self.players.append(p)

    def send_territory_click(self, territory_id):
        if not self.players:
            return
        frame = bytearray(5)
        frame[0] = RYSK_FRAME_TERRITORY_CLICK
        frame[1] = territory_id[0]
        frame[2] = territory_id[1]
        frame[3] = territory_id[2]
        frame[4] = territory_id[3]
        self.players[0].sendq += frame

    def update(self):
        for player in self.players:
            if player.recvq:
                frame_type = player.recvq[0]
                frame_len = 1
                if frame_type == RYSK_FRAME_TERRITORY_CLICK:
                    frame_len += 4
                    r = player.recvq[1]
                    g = player.recvq[2]
                    b = player.recvq[3]
                    a = player.recvq[4]
                    color = (r, g ,b, a)
                    print(f"Frame 0: {color}")
                    self.country = load_image(TERRITORY.get(color))
                    if self.country:
                        self.country = pygame.transform.scale(self.country, WINDOW)
                    player.recvq = player.recvq[frame_len:]

    def draw(self, window):
        for player in self.players:
            if player.surface is not None:
                window.blit(player.surface, player.pos)

        if self.country:
            window.blit(self.country, (0, 0))


def run():
    # init window stuff
    pygame.init()
    pygame.display.set_caption('RYSK')
    window = pygame.display.set_mode(WINDOW)

    # init game stuff
    background = pygame.transform.scale(load_image('continents_v2.png'),
                                        WINDOW)
    board = Board()
    country = None

    # init network stuff
    net = Network()

    while True:
        # updates (input, network, game loop)
        update_input()
        net.update(board)
        board.update()

        # player wants to quit
        if is_key_pressed(pygame.K_ESCAPE):
            print("Thanks for playing!")
            break

        if is_left_clicked():
            pos = get_mouse_pos()
            color = tuple(background.get_at(pos))

            # highlight a territory when clicked
            if TERRITORY.get(color):
                print(f"pos: {pos}, color: {color}, state: {TERRITORY.get(color)}")
                country = load_image(TERRITORY.get(color))
                if country:
                    country = pygame.transform.scale(country, WINDOW)
                    board.send_territory_click(color)

            # slide player card when clicked
            for player in board.players:
                player_rect = pygame.Rect(player.pos,
                                          (player.surface.get_width(),
                                           player.surface.get_height()))
                if player_rect.collidepoint(*pos):
                    player.clicked()

        # player wants to host a game
        if is_key_pressed('h'):
            net.listen('localhost', 9923)

        # player wants to join a game
        if is_key_pressed('j'):
            sock = net.connect(input('Server IP: '), SERVER_PORT)
            board.add_player(sock)

        # player wants to chat
        if is_key_pressed('c'):
            msg = input('Say: ').encode('utf-8')
            net.send(sock, msg)

        # render
        window.fill(utilities.WHITE)
        window.blit(background, (0, 0))
        board.draw(window)
        if country:
            window.blit(country, (0, 0))
        pygame.display.update()

    net.shutdown()
    pygame.quit()


if __name__ == "__main__":
    run()
