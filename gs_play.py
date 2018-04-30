import pygame

from gsm import Gamestate

TERRITORY = {
    (226, 217, 40, 255): "Alaska",
    (214, 171, 128, 255): "Brazil",
    (255, 252, 0, 255): "greenland.png"
}


class GSPlay(Gamestate):

    def __init__(self):
        self.name = "GS_Play"

        self.core = None
        self.background = None
        self.country = None
        
    def initialize(self, core):
        self.core = core
        
        self.background = core.load_image('continents.png')
        self.background = pygame.transform.scale(self.background,
                                                 (core.display_width, core.display_height))
        
        return True
        
    def update(self):
        if self.core.is_left_clicked():
            pos = self.core.get_mouse_pos()
            color = tuple(self.background.get_at(pos))
            print("pos: {0}, color: {1}, state: {2}".format(
                pos, color, TERRITORY.get(color)))
            self.country = self.core.load_image(TERRITORY.get(color))
        
    def draw(self, display):
        display.blit(self.background, (0, 0))
        if self.country:
            display.blit(self.country, (100, 0))