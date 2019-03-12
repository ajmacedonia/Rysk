import socket
import selectors

import utilities

# app magic
magic = 0x1234567890abcdef


class Network:
    def __init__(self):
        self.selector = None
        self.listener = None

    def update(self, board):
        """Checks sockets for read/write events."""
        if self.selector is not None:
            events = self.selector.select(timeout=0)
            for key, mask in events:
                sock = key.fileobj
                player = key.data
                if player is None:
                    # accept a new connection
                    self._accept(board)
                    if len(board.players) == utilities.MAX_PLAYERS:
                        self.selector.unregister(self.listener)
                else:
                    # process an existing connection
                    if mask & selectors.EVENT_READ:
                        data = sock.recv(1024)
                        if data:
                            player.recv_data(data)
                            print(f"Received {len(data)} bytes from {sock.getpeername()}")
                    if mask & selectors.EVENT_WRITE:
                        if not player.sendq:
                            continue
                        sent = self.send(sock, player.sendq)
                        player.sendq = player.sendq[sent:]

    def _accept(self, board):
        """Accepts a new incoming connection."""
        s, addr = self.listener.accept()
        s.setblocking(False)
        print(f"{addr} has connected")
        board.add_player(None, False, sock=s)
        self.selector.register(s, selectors.EVENT_READ | selectors.EVENT_WRITE,
                               data=board.players[-1])

        return s

    def connect(self, ip, port, board):
        """Connects to a given IP:PORT. Returns a new socket."""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, port))
        s.setblocking(False)
        board.add_player(None, True, sock=s)
        self.selector = selectors.DefaultSelector()
        self.selector.register(s, selectors.EVENT_READ | selectors.EVENT_WRITE,
                               data=board.players[-1])
        print(f"Connected to {s.getpeername()}")
        return s

    def listen(self, ip, port):
        """Listens for new connections on a given IP:PORT."""
        if self.listener is not None:
            return

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((ip, port))
        s.setblocking(False)
        s.listen()
        self.selector = selectors.DefaultSelector()
        self.selector.register(s, selectors.EVENT_READ)
        self.listener = s
        print(f"Listening on {ip}:{port}")

    def send(self, s, data):
        """Sends all data on a given socket."""
        bytes_sent = s.send(data)
        print(f"Sent {bytes_sent} bytes to {s.getpeername()}")
        return bytes_sent

    def shutdown(self):
        if self.listener is not None:
            self.listener.close()
