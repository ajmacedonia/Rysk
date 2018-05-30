import pygame

from gsm import Gamestate
from player import Player

TERRITORY = {
    (226, 217, 40, 255): "Alaska",
    (214, 171, 128, 255): "Brazil",
    (255, 252, 0, 255): "greenland.png"
}
MAX_PLAYERS = 4


class GSPlay(Gamestate):

    def __init__(self):
        self.name = "GS_Play"
        self.current_state = None

        self.core = None
        self.background = None
        self.country = None

        self.players = []
        
    def initialize(self, core):
        self.core = core
        
        self.background = core.load_image('continents.png')
        self.background = pygame.transform.scale(self.background,
                                                 (core.display_width, core.display_height))

        self.current_state = self.initial_army_placement
        return True

    def _player_clicked(self, player: object, mouse_pos: tuple):
        player_rect = pygame.Rect(player.pos,
                                  (player.surface.get_width(),
                                   player.surface.get_height()))
        return player_rect.collidepoint(*mouse_pos)

    def update(self):
        if self.core.is_left_clicked():
            pos = self.core.get_mouse_pos()
            color = tuple(self.background.get_at(pos))

            # zoom in on a continent when clicked
            print("pos: {0}, color: {1}, state: {2}".format(
                pos, color, TERRITORY.get(color)))
            self.country = self.core.load_image(TERRITORY.get(color))

            # slide player card when clicked
            for player in self.players:
                if self._player_clicked(player, pos):
                    player.clicked()

        self.current_state()

    def initial_army_placement(self):
        num_players = 2#int(input("Number of players: "))
        colors = ["black", "blue", "magenta", "green"]

        # load players and scale them appropriately
        scale_x = self.core.display_width // MAX_PLAYERS
        scale_y = self.core.display_height // 2
        for i in range(num_players):
            x, y = scale_x * i, scale_y

            player = Player(colors[i], (x, y))
            player.surface = pygame.transform.scale(player.surface,
                                                    (scale_x, scale_y+20))
            self.players.append(player)

        self.current_state = self.game_loop

    def game_loop(self):
        pass

    def draw(self, display):
        display.blit(self.background, (0, 0))

        for player in self.players:
            print("player 1:", player.pos)
            display.blit(player.surface, player.pos)

        if self.country:
            display.blit(self.country, (100, 0))