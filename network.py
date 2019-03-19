import socket
import selectors

import utilities

# app magic
MAGIC = sum(map(ord, 'RYSK'))
HEADER_LEN = 2


class Network:
    def __init__(self):
        self.selector = None
        self.listener = None

    def get_header(self, payload_len):
        header = bytearray(MAGIC.to_bytes(2, 'big'))
        header += payload_len.to_bytes(2, 'big')
        return header

    def validate_hdr(self, hdr):
        magic = int.from_bytes(hdr, 'big', signed=False)
        return magic == MAGIC

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
                        data, f_ready = self.recv(sock)
                        if data:
                            player.recv_data(data, f_ready)
                            print(f"Received {len(data)} bytes from {sock.getpeername()}, "
                                  f"f_ready_to_read {f_ready}")
                    if mask & selectors.EVENT_WRITE:
                        if not player.sendq:
                            continue
                        header = self.get_header(len(player.sendq))
                        sent = self.send(sock, header+player.sendq)
                        player.sendq = player.sendq[sent:]

    def send(self, s, data):
        """Sends all data on a given socket."""
        bytes_sent = 0
        while bytes_sent < len(data):
            bytes_sent += s.send(data)
        print(f"Sent {bytes_sent} bytes to {s.getpeername()}")
        return bytes_sent

    def recv(self, s):
        data = bytearray()
        try:
            while len(data) < HEADER_LEN:
                data += s.recv(1024)
        except BlockingIOError:
            return data, False

        if not self.validate_hdr(data[:HEADER_LEN]):
            print("Bad header", data[:HEADER_LEN])
            return None, False

        payload_len = int.from_bytes(data[HEADER_LEN:HEADER_LEN+2], 'big',
                                     signed=False)
        data = data[HEADER_LEN+2:]
        while len(data) < payload_len:
            try:
                data += s.recv(1024)
            except BlockingIOError:
                pass
        return data, True

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

    def shutdown(self):
        if self.listener is not None:
            self.listener.close()
