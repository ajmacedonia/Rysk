import pygame
import socket
import selectors

from gsm import Gamestate
from player import Player

TERRITORY = {
    # North America
    (255, 255, 0, 255): "greenland_highlight.png",
    (255, 255, 1, 255): "nwter_highlight.png",
    (255, 255, 2, 255): "alaska_highlight.png",
    (255, 255, 3, 255): "alberta_highlight.png",
    (255, 255, 4, 255): "ontario_highlight.png",
    (255, 255, 5, 255): "easterncan_highlight.png",
    (255, 255, 6, 255): "westus_highlight.png",
    (255, 255, 7, 255): "eastus_highlight.png",
    (255, 255, 8, 255): "centralamerica_highlight.png",
    # South America
    (255, 127, 0, 255): "Argentina",
    (255, 127, 1, 255): "Brazil",
    (255, 127, 2, 255): "Peru",
    (255, 127, 3, 255): "Venezuela",
    # Africa
    (127, 127, 127, 255): "North Africa",
    (128, 128, 128, 255): "Egypt",
    (129, 129, 129, 255): "East Africa",
    (130, 130, 130, 255): "Central Africa",
    (131, 131, 131, 255): "South Africa",
    (132, 132, 132, 255): "Madagascar",
    # Europe
    (0, 0, 255, 255): "Iceland",
    (1, 0, 255, 255): "Great Britain",
    (2, 0, 255, 255): "Scandanavia",
    (3, 0, 255, 255): "Russia",
    (4, 0, 255, 255): "Northern Europe",
    (5, 0, 255, 255): "Western Europe",
    (6, 0, 255, 255): "Southern Europe",
    # Asia
    (0, 255, 0, 255): "Kamchatka",
    (1, 255, 0, 255): "Yakutsk",
    (2, 255, 0, 255): "Siberia",
    (3, 255, 0, 255): "Ural",
    (4, 255, 0, 255): "Irkutsk",
    (5, 255, 0, 255): "Mongolia",
    (6, 255, 0, 255): "Japan",
    (7, 255, 0, 255): "Afghanistan",
    (8, 255, 0, 255): "China",
    (9, 255, 0, 255): "Middle East",
    (10, 255, 0, 255): "India",
    (11, 255, 0, 255): "Southeast Asia",
    # Australia
    (255, 0, 255, 255): "Indonesia",
    (255, 1, 255, 255): "New Guinea",
    (255, 2, 255, 255): "Western Australia",
    (255, 3, 255, 255): "Eastern Australia"
}
MAX_PLAYERS = 4

HOST = 'localhost'
PORT = 9669
sel = selectors.DefaultSelector()

class GSPlay(Gamestate):

    def __init__(self):
        self.name = "GS_Play"
        self.current_state = None

        self.core = None
        self.background = None
        self.country = None

        self.players = []

        self.is_host = False
        self.listener_sock = None
        
    def initialize(self, core):
        self.core = core
        
        self.background = core.load_image('continents_v2.png')
        self.background = pygame.transform.scale(self.background,
                                                 (core.display_width,
                                                  core.display_height))

        self.current_state = self.initial_army_placement
        return True

    def _player_clicked(self, player: object, mouse_pos: tuple):
        player_rect = pygame.Rect(player.pos,
                                  (player.surface.get_width(),
                                   player.surface.get_height()))
        return player_rect.collidepoint(*mouse_pos)

    def start_host(self):
        self.is_host = True

        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.bind((HOST, PORT))
        listener.setblocking(False)
        listener.listen()
        sel.register(listener, selectors.EVENT_READ, data=None)

        while True:
            events = sel.select()

            for key, mask in events:
                if key.data is None:
                    accept(key.fileobj)
                else:
                    process(key.fileobj, mask, key.data)

    def update(self):
        if self.core.is_left_clicked():
            pos = self.core.get_mouse_pos()
            color = tuple(self.background.get_at(pos))

            # highlight a territory when clicked
            if TERRITORY.get(color):
                print("pos: {0}, color: {1}, state: {2}".format(
                    pos, color, TERRITORY.get(color)))
                self.country = self.core.load_image(TERRITORY.get(color))
                if self.country:
                    self.country = pygame.transform.scale(self.country,
                                                          (self.core.display_width,
                                                           self.core.display_height))

            # slide player card when clicked
            for player in self.players:
                if self._player_clicked(player, pos):
                    player.clicked()

        if self.core.is_key_pressed('s'):
            self.start_host()

        self.current_state()

    def initial_army_placement(self):
        num_players = 2  # int(input("Number of players: "))

        for i in range(num_players):
            self.add_player()

        # listener socket event or dedicated polling thread
        # add_player: player contains network logic

        self.current_state = self.game_loop

    def add_player(self):
        colors = ["black", "blue", "magenta", "green"]
        scale_x = self.core.display_width // MAX_PLAYERS
        scale_y = self.core.display_height // 2

        num_player = len(self.players)
        x, y = scale_x * num_player, scale_y
        player = Player(colors[num_player], (x, y))
        scale = (scale_x, scale_y)
        player.surface = pygame.transform.scale(player.surface, scale)
        self.players.append(player)

    def game_loop(self):
        pass

    def draw(self, display):
        display.blit(self.background, (0, 0))

        for i in range(len(self.players)):
            display.blit(self.players[i].surface, self.players[i].pos)

        if self.country:
            display.blit(self.country, (100, 0))