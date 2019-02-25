import socket
import pygame

import utilities

from core import Core
from gsm import GamestateManager
from gs_play import GSPlay
from gs_main import GSMain


def run():
    clock = pygame.time.Clock()
    FPS = 15

    core = Core(1280, 960)
    core.set_caption("RYSK")

    gsm = GamestateManager()
    gsm.register_state("GSPlay", GSPlay())
    gsm.register_state("GSMain", GSMain())
    gsm.set_next_state("GSMain")

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





class Buffer():
    def __init__(self):
        self.data_in = b''
        self.data_out = b''


def accept(sock):
    conn, addr = sock.accept()
    print("New connection from {0}".format(addr))
    sel.register(conn, selectors.EVENT_READ, data=Buffer())


def process(sock, mask, buffer):
    if mask == selectors.EVENT_READ:
        data = sock.recv(1024)
        print("Received from {0}: {1}".format(str(sock), data.decode('utf-8')))
        buffer.data_in += data
        sel.unregister(sock)
        if data:
            sel.register(sock, selectors.EVENT_WRITE, data=buffer)
        else:
            sock.close()
    elif mask == selectors.EVENT_WRITE:
        sent = sock.send(buffer.data_in)
        print("Sent to {0}: {1}".format(str(sock), buffer.data_in[:sent].decode('utf-8')))
        buffer.data_in = buffer.data_in[sent:]
        if not buffer.data_in:
            sel.unregister(sock)
            sel.register(sock, selectors.EVENT_READ, data=buffer)


def client():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect_ex((HOST, PORT))
    print("Connected to {0}".format((HOST, PORT)))

    while True:
        msg = input(":").encode('utf-8')
        sent = 0
        while sent < len(msg):
            sent += sock.send(msg)

        if sent:
            msg = sock.recv(1024)
            print(msg.decode('utf-8'))
        else:
            break


if __name__ == "__main__":
    run()
    # if sys.argv[1] == '-s':
    #     server()
    # elif sys.argv[1] == '-c':
    #     client()
