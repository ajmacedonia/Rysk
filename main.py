# external modules
import pygame

# custom modules
import utilities
from input import update_input, is_key_pressed, is_left_clicked, get_mouse_pos
from network import Network
from board import Board
from button import Button

# misc
WINDOW = (1280, 960)
SERVER_PORT = 9923

STATE_INITIAL_ARMY_PLACEMENT = 0

# initial infantry count based on number of players
infantry_count = {
    2: 40,  # XXX see page 11
    3: 35,
    4: 30,
    5: 25,
    6: 20
}


def run():
    # init window stuff
    pygame.init()
    pygame.display.set_caption('RYSK')
    window = pygame.display.set_mode(WINDOW)

    # init game stuff
    board = Board(WINDOW)
    button_host = Button("(H)ost Game")
    button_join = Button("(J)oin Game")
    button_join.x += button_host.width + 10

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
            # slide player card when clicked
            pos = get_mouse_pos()
            for player in board.players:
                player_rect = pygame.Rect(player.pos,
                                          (player.surface.get_width(),
                                           player.surface.get_height()))
                if player_rect.collidepoint(*pos):
                    player.clicked()

        # player wants to host a game
        if is_key_pressed('h') or button_host.clicked():
            net.listen('localhost', 9923)

        # player wants to join a game
        if is_key_pressed('j') or button_join.clicked():
            sock = net.connect(input('Server IP: '), SERVER_PORT)
            board.add_player(sock)

        # player wants to chat
        if is_key_pressed('c'):
            msg = input('Say: ').encode('utf-8')
            net.send(sock, msg)

        # render
        window.fill(utilities.WHITE)
        board.draw(window)
        button_host.draw(window)
        button_join.draw(window)
        pygame.display.update()

    net.shutdown()
    pygame.quit()


if __name__ == "__main__":
    run()
