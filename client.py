import sys
import argparse
import socket
import logging
import pygame

import utilities
import frames
import game
from network import Socket
from input import is_key_pressed, update_input
from player import Player


logging.basicConfig(format='[%(levelname)s]%(asctime)s - '
                           '%(funcName)s:%(lineno)d - '
                           '%(message)s',
                    level=logging.DEBUG)


def run_client(args):
    logging.info("Starting client...")
    pygame.init()
    pygame.display.set_caption('Client')
    window = pygame.display.set_mode(utilities.WINDOW)
    window.fill(utilities.CYAN)

    # Create local player
    name = args.name or input("Player Name (max 16 characters): ")
    if len(name) > utilities.PLAYER_NAME_LEN_MAX:
        name = name[:utilities.PLAYER_NAME_LEN_MAX]
    local_player = Player(name=name)
    gs = game.GameState()
    gs.add_player(local_player)
    gs.local_player = local_player

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    logging.info(f"Connecting to {utilities.ADDR}")
    s.connect(utilities.ADDR)
    s.setblocking(False)
    local_player.socket = Socket(sock=s)
    logging.info(f"Connected to localhost")

    # Inform Server
    frame = frames.build_frame_set_name(gs, local_player.name)
    s.sendall(frame)

    while not gs.f_exiting:
        update_input()
        game.process_input(gs, local_player)

        # Auto start game
        if gs.n_auto_start != 0 and gs.n_auto_start == len(gs.players):
            gs.n_auto_start = 0
            frame = frames.build_frame_chat(gs, local_player.ID, game.COMMAND_START)
            s.sendall(frame)

        if is_key_pressed(pygame.K_q):
            print(gs.players)

        # Send chat message
        if is_key_pressed(pygame.K_t):
            msg = input(": ")
            if msg == game.COMMAND_EXIT or msg == game.COMMAND_SHUTDOWN:
                logging.debug(f"Received command {msg}")
                gs.f_exiting = True
            else:
                frame = frames.build_frame_chat(gs, local_player.ID, msg)
                s.sendall(frame)

        # Send dice roll
        if is_key_pressed(pygame.K_r):
            num_attack = int(input("Roll how many attack dice (max 6): "))
            num_defense = int(input("Roll how many defense dice (max 6): "))
            frame = frames.build_frame_roll(gs, local_player.ID, num_attack,
                                            num_defense)
            s.sendall(frame)

        game.update(gs)
        gs.draw(window)
        pygame.display.update()

        # Graceful close
        if is_key_pressed(pygame.K_ESCAPE):
            gs.f_exiting = True

        # Server down
        if local_player.socket.closed:
            logging.info(f"Lost connection to Server")
            gs.f_exiting = True

    logging.info("Exiting")

    # Cleanup
    s.shutdown(socket.SHUT_RDWR)
    s.close()


if __name__ == "__main__":
    ap = argparse.ArgumentParser(prog="RYSK Client", description="The World Conquest Game")
    ap.add_argument('-n', '--name', required=False, help="Set player name")
    run_client(ap.parse_args())
    sys.exit(0)
