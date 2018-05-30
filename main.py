import pygame
import utilities

from core import Core
from gsm import GamestateManager
from gs_play import GSPlay
from gs_main import GSMain

if __name__ == "__main__":
    clock = pygame.time.Clock()
    FPS = 15

    core = Core(1280, 960)
    core.set_caption("RYSK")

    gsm = GamestateManager()
    gsm.register_state("GSPlay", GSPlay())
    gsm.register_state("GSMain", GSMain())
    gsm.set_next_state("GSPlay")

    while core.run:

        success = gsm.initialize_state(core)
        # other systems

        if not success:
            break

        while core.run and not gsm.shutdown:
            # update input
            core.update_input()

            # update game play
            gsm.update_state()

            # render
            core.display.fill(utilities.WHITE)
            gsm.draw_state(core.display)
            pygame.display.update()

            clock.tick(FPS)

    pygame.quit()
