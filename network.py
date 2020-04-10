import socket


# app magic
MAGIC = sum(map(ord, 'RYSK'))
HEADER_LEN = 2


class Socket:
    def __init__(self, sock=None):
        self.socket = sock
        self.recvq = []
        self.closed = False

    def __str__(self):
        if self.closed:
            return "Disconnected"
        else:
            return f"Connected to {self.socket.getpeername()}"

    def __eq__(self, other):
        return self.socket == other.socket

    def recv_bytes(self, data):
        self.recvq.append(data)

    def has_bytes(self):
        return len(self.recvq) != 0

    def get_bytes(self):
        data = self.recvq.pop(0)
        return data


class Network:
    def __init__(self):
        self.listener = None
        self.sockets = []

    def get_header(self, payload_len):
        header = bytearray(MAGIC.to_bytes(2, 'big'))
        header += payload_len.to_bytes(2, 'big')
        return header

    def validate_hdr(self, hdr):
        magic = int.from_bytes(hdr, 'big', signed=False)
        return magic == MAGIC

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

    def accept(self, board):
        """Accepts a new incoming connection."""
        s, addr = self.listener.accept()
        if s is not None:
            s.setblocking(False)
            print(f"{addr} has connected")
            board.add_player(None, False, sock=s)

        return s

    def connect(self, ip, port, board):
        """Connects to a given IP:PORT. Returns a new socket."""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, port))
        s.setblocking(False)
        board.add_player(None, True, sock=s)
        print(f"Connected to {s.getpeername()}")
        return s

    def listen(self, ip, port):
        """Listens for new connections on a given IP:PORT."""
        if self.listener is not None:
            return

        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener.bind((ip, port))
        self.listener.setblocking(False)
        self.listener.listen()
        print(f"Listening on {ip}:{port}")

    def shutdown(self):
        if self.listener is not None:
            self.listener.close()
            self.listener = None

    def update(self, board):
        """Checks sockets for read/write events."""
        if self.listener is not None:
            self.accept()

        for s in self.sockets:
            s.recv_data()

        for s in self.sockets:
            s.send_data()