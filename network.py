import socket
import selectors

# app magic
magic = 0x1234567890abcdef


class Buffer:
    def __init__(self):
        self.sendq = bytearray()
        self.recvq = bytearray()


class Network:
    def __init__(self):
        self.sockets = []
        self.selector = None
        self.listener = None

    def update(self):
        """Checks sockets for read/write events."""
        if self.selector is None:
            return

        events = self.selector.select(timeout=0)
        for key, mask in events:
            sock = key.fileobj
            data = key.data
            if data is None:
                # accept a new connection
                self._accept()
            else:
                # process an existing connection
                if mask == selectors.EVENT_READ:
                    d = sock.recv(1024)
                    bytes_read = len(d)
                    if bytes_read:
                        data.recvq += d
                        print(f"Received {bytes_read} bytes from {sock.getpeername()}")
                        print(data.recvq.decode('utf-8'))

                elif mask == selectors.EVENT_WRITE:
                    if not data.sendq:
                        continue
                    self.send(sock, data.sendq)
                    data.sendq = b''
                    self.sel.unregister(sock)

    def _accept(self):
        """Accepts a new incoming connection."""
        s, addr = self.listener.accept()
        s.setblocking(False)
        self.selector.register(s, selectors.EVENT_READ, data=Buffer())
        print(f"{addr} has connected")

    def connect(self, ip, port):
        """Connects to a given IP:PORT. Returns a new socket."""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, port))
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

    def shutdown(self):
        for s in self.sockets:
            s.close()
        if self.listener is not None:
            self.listener.close()


def send_dice_roll(player, results):
    buf = bytearray([player.player_id, len(results)] + results)
    return buf


def process_dice_roll(data):
    player_id = data[0]
    num_dice = data[1]
    print(f"player {player_id} rolled {num_dice} dice: ", end='')
    for i in range(num_dice):
        print(data[2+i], end=' ')


def send_state_change(state):
    pass


def send_territory_update():
    pass

# Message types
# DICE_ROLL
# - player
#  - num dice
#  - results
#  ...
# ...
#
# STATE_CHANGE
# - state
#  - State-specific data
#
# TERRITORY_UPDATE
# - territory
# - owner
# - add/remove num troops
#
#
#
#
