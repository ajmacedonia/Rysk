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
from player import Player

# filesystem info
BASE_DIR = os.path.split(os.path.abspath(__file__))[0]
IMAGES_DIR = os.path.join(BASE_DIR, 'images')

# misc
WINDOW = (1280, 960)
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


class Buffer:
    def __init__(self):
        self.data_in = b''
        self.data_out = b''


def run_initial_army_placement():
    pass
    # rolls = player.roll_dice(1, 0)

    # for p in players:
    #    rolls = p.get_roll()

    # rolls = sorted([(p.get_rolls())[0][0] for p in players])
    # d
    # send result to server, server sends to everyone else
    # sort results
    # loop through players


def add_player(players):
    colors = ["black", "blue", "magenta", "green"]
    scale_x = WINDOW[0] // MAX_PLAYERS
    scale_y = WINDOW[1] // 2

    num_player = len(players)
    x, y = scale_x * num_player, scale_y
    player = Player(colors[num_player], (x, y))
    scale = (scale_x, scale_y)
    player.surface = pygame.transform.scale(player.surface, scale)
    players.append(player)


def run():
    # init window stuff
    pygame.init()
    pygame.display.set_caption('RYSK')
    window = pygame.display.set_mode(WINDOW)

    # init game stuff
    background = pygame.transform.scale(load_image('continents_v2.png'),
                                        WINDOW)
    country = None
    players = []

    # init network stuff
    port = 9923
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sel = selectors.DefaultSelector()

    while True:
        # updates (input, network, game loop)
        update_input()

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

            # slide player card when clicked
            for player in players:
                player_rect = pygame.Rect(player.pos,
                                          (player.surface.get_width(),
                                           player.surface.get_height()))
                if player_rect.collidepoint(*pos):
                    player.clicked()

        # player wants to host a game
        if is_key_pressed('h'):
            add_player(players)

            print("Listening on port {port}")
            sock.bind(('localhost', port))
            sock.setblocking(False)
            sock.listen()
            sel.register(sock, selectors.EVENT_READ, data=None)

            while True:
                if is_key_pressed('s'):
                    break

                events = sel.select()
                for key, mask in events:
                    csock = key.fileobj
                    if key.data is None:
                        # add new connection
                        conn, addr = csock.accept()
                        print(f"New connection from {addr}")
                        sel.register(conn, selectors.EVENT_READ, data=Buffer())
                        add_player(players)
                    else:
                        # process existing connection
                        if mask == selectors.EVENT_READ:
                            data = csock.recv(1024)
                            print(f"{str(csock.laddr)}: {data.decode('utf-8')}")
                            key.data.data_in += data
                            sel.unregister(csock)
                            if data:
                                sel.register(csock, selectors.EVENT_WRITE, data=key.data)
                            else:
                                csock.close()
                        elif mask == selectors.EVENT_WRITE:
                            sent = csock.send(key.data.data_in)
                            print(f"Sent to {str(csock.laddr)}: {key.data.data_in[:sent].decode('utf-8')}")
                            key.data.data_in = key.data.data_in[sent:]
                            if not key.data.data_in:
                                sel.unregister(csock)
                                sel.register(csock, selectors.EVENT_READ, data=key.data)

        # player wants to join a game
        if is_key_pressed('j'):
            server = input('Server IP: ')
            sock.connect_ex((server, port))
            print("Connected to {(server, port)}")

            while True:
                msg = input('Chat: ').encode('utf-8')
                sent = 0
                while sent < len(msg):
                    sent += sock.send(msg)
                if sent:
                    msg = sock.recv(1024)
                    print(msg.decode('utf-8'))
                else:
                    break

        # render
        window.fill(utilities.WHITE)
        window.blit(background, (0, 0))
        for player in players:
            window.blit(player.surface, player.pos)
        if country:
            window.blit(country, (0, 0))
        pygame.display.update()

    pygame.quit()
    # initialize
    # num_players = 3

    # for i in range(num_players):
    #    players.append(Player(infantry_count[num_players]))

    # state = STATE_INITIAL_ARMY_PLACEMENT
    # while True:
    #    if state == STATE_INITIAL_ARMY_PLACEMENT:
    #        run_initial_army_placement()


if __name__ == "__main__":
    run()
