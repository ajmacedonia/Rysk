import sys
import socket
import logging

import pygame

import utilities
import game
from network import Socket
from input import is_key_pressed, update_input
from player import Player


logging.basicConfig(format='[%(levelname)s]%(asctime)s - '
                           '%(funcName)s:%(lineno)d - '
                           '%(message)s',
                    level=logging.DEBUG)


# GS obj has state flags that are checked on update to progress
# Use pathlib


def run_server():
    # Game initialization
    gs = game.GameState()
    gs.f_host = True

    # Display initialization
    pygame.init()
    pygame.display.set_caption('Server')
    window = pygame.display.set_mode(utilities.WINDOW)
    window.fill((240, 0, 20))

    # Network initialization
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.bind(utilities.ADDR)
    listener.setblocking(False)
    listener.listen()

    logging.info(f"Listening on {utilities.ADDR}")
    while not gs.f_exiting:
        update_input()

        # Graceful exit
        if is_key_pressed(pygame.K_ESCAPE):
            gs.f_exiting = True

        # Accept new connections
        try:
            s, addr = listener.accept()
            if s is not None:
                logging.info(f"{addr} has connected")
                s.setblocking(False)
                p = Player()
                p.socket = Socket(sock=s)
                gs.add_player(p)
        except BlockingIOError:
            pass

        # Process player input
        for p in gs.players:
            if gs.f_exiting:
                break
            game.process_input(gs, p)

        # Remove disconnected players
        if gs.players:
            gs.players[:] = [p for p in gs.players if not p.socket.closed]
            if not gs.players:
                gs.set_state(game.STATE_LOBBY)

        # Update
        game.update(gs)
        gs.draw(window)
        pygame.display.update()

    # Shutdown all connections
    for s in gs.get_sockets():
        s.socket.shutdown(socket.SHUT_WR)
        s.socket.close()

    logging.info("Exiting")


if __name__ == "__main__":
    run_server()
    sys.exit(0)
