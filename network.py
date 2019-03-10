import socket
import selectors

import utilities

# app magic
magic = 0x1234567890abcdef


class Network:
    def __init__(self):
        self.sockets = []
        self.selector = None
        self.listener = None

    def update(self, board):
        """Checks sockets for read/write events."""
        # board is either host or not
        # if host - run select loop on all player sockets
        #   - attempt recv on all players (do not change selector state)
        #   - attempt send if player has data to send (do not change state)
        # if not host - attempt recv on local player, attempt send
        # if not board.is_host and board.local_player is not None:
        #     # clients maintain a single connection
        #     p = board.local_player
        #     # receive as much as we can
        #     data = p.sock.recv(1024)
        #     if data:
        #         p.recv_data(data)
        #         print(f"Received {len(data)} bytes from {p.sock.getpeername()}")
        #     # send as much as we can
        #     if p.sendq:
        #         sent = self.send(p.sock, p.sendq)
        #         p.sendq = p.sendq[sent:]
        # elif board.is_host:
        if self.selector is not None:
            # hosts maintain connections with all players
            # for p in board.players:
            #     if p.sock is None:
            #         continue
            #     data = p.sock.recv(1024)
            #     if data:
            #         p.recv_data(data)
            #         print(f"Received {len(data)} bytes from {p.sock.getpeername()}")
            #     if p.sendq:
            #         sent = self.send(p.sock, p.sendq)
            #         p.sendq = p.sendq[sent:]

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
                        # self.sel.unregister(sock)

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
        self.sockets.append(s)
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
        for s in self.sockets:
            s.close()
        if self.listener is not None:
            self.listener.close()
