# built-in modules
import argparse
import configparser
import logging

# external modules
import pygame

# custom modules
import utilities
from input import update_input, is_key_pressed, is_left_clicked, get_mouse_pos
from network import Network
from board import Board
from button import Button
from chatbox import ChatBox

WINDOW = utilities.WINDOW

STATE_INITIAL_ARMY_PLACEMENT = 0

# initial infantry count based on number of players
infantry_count = {
    2: 40,  # XXX see page 11
    3: 35,
    4: 30,
    5: 25,
    6: 20
}


def run(run_client=None, run_server=None):
    # load config
    config = configparser.ConfigParser(allow_no_value=True)
    config.read('rysk.conf')
    print(f"Configuration loaded:")
    for section in config.sections():
        print(f"\t{section}")
        for key in config[section]:
            print(f"\t\t{key} = {config[section][key]}")

    # init window stuff
    pygame.init()
    pygame.display.set_caption('RYSK')
    window = pygame.display.set_mode(WINDOW)

    # init game stuff
    board = Board(WINDOW)
    button_host = Button('(H)ost Game')
    button_join = Button('(J)oin Game')
    button_join.x += button_host.width + 10
    button_chat = Button('(C)hat')
    name = config['DEFAULT']['name']
    if name is None or len(name) > 10:
        while len(name) > 10:
            name = input("Please enter your name (10 chars max): ")

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
                                          (player.sprite.get_width(),
                                           player.sprite.get_height()))
                if player_rect.collidepoint(*pos):
                    player.clicked()

        # player wants to host a game
        if is_key_pressed('h') or button_host.clicked() or run_server:
            run_server = False
            pygame.display.set_caption('RYSK (Host)')
            board.f_host = True
            board.add_player(None, True)
            board.local_player.name = name
            net.listen('localhost', 9923)

        # player wants to join a game
        if is_key_pressed('j') or button_join.clicked() or run_client:
            run_client=False
            pygame.display.set_caption('RYSK (Client)')
            sock = net.connect('localhost', utilities.SERVER_PORT, board)

        # player wants to chat
        if is_key_pressed('c') or button_chat.clicked():
            msg = input('Say: ').encode('utf-8')
            net.send(sock, msg)

        # render
        window.fill(utilities.WHITE)
        board.draw(window)
        button_host.draw(window)
        button_join.draw(window)
        pygame.display.update()

    board.quit()
    net.shutdown()
    pygame.quit()


if __name__ == "__main__":
    logging.debug('This is a debug message')
    logging.info('This is an info message')
    logging.warning('This is a warning message')
    logging.error('This is an error message')
    logging.critical('This is a critical message')
    ap = argparse.ArgumentParser(prog="RYSK", description="The World Conquest Game")
    ap.add_argument('-c', '--client', required=False, action='store_true',
                    help="Run as Client")
    ap.add_argument('-s', '--server', required=False, action='store_true',
                    help="Run as Server")
    args = ap.parse_args()
    run(run_client=args.client, run_server=args.server)
