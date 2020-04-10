import logging
import random
import pygame
from itertools import count

import utilities
import frames
from input import is_left_clicked, get_mouse_pos
from player import Player

BUFFER_SIZE = 4000 # 4KB
SERVER_ID = 0

# Server commands
COMMAND_EXIT = '/exit'
COMMAND_SHUTDOWN = '/killserver'
COMMAND_START = '/start'

# Game states
STATE_LOBBY = 0
STATE_INITIAL_ARMY_PLACEMENT = 1

STATE_STR = {
    STATE_LOBBY: "STATE_LOBBY",
    STATE_INITIAL_ARMY_PLACEMENT: "STATE_INITIAL_ARMY_PLACEMENT"
}
# GS has a waiting_for_players list, other flags (f_need_rolls) tells us what
# we're waiting for, frame processing checks the flags, removes players from
# waiting list. In state update, if waiting for players list is empty, process
# results and progress. Oh shit this how I could wait for each player in order
# during territory claims. =O

# Both Server and Client wait for players. Ex: Server waits for dice rolls from
# all players, relays the rolls to each player, each Client is waiting for the
# other players. Maybe even themselves depending on abstraction desired

# Fix remove_player logic to remove AFTER list processing
# Load background
# Load territory objects: ids and surface objects


class Territory:

    def __init__(self, name: str, color: tuple, filename: str):
        self.color = color
        self.filename = filename
        self.name = name
        self.image = utilities.load_image(filename)
        if self.image:
            self.image = pygame.transform.scale(self.image, utilities.WINDOW)

        self.pid = None
        self.armies = 0

    def conquer(self, player_id: int, n_armies: int) -> None:
        self.pid = player_id
        self.armies = n_armies

    def add_armies(self, n_armies: int) -> None:
        self.armies += n_armies


class GameState:
    gen_id = count()

    def __init__(self):
        # Display
        self.bg = pygame.transform.scale(utilities.load_image('continents_v2.png'),
                                         utilities.WINDOW)
        # Debug flags

        # Auto start game when the expected number of players have joined
        self.n_auto_start = 2
        # Auto roll dice
        self.f_auto_roll = True
        # Auto place armies during IAP
        self.f_auto_place = True

        self.f_host = False
        self.local_player = None
        self.players = []
        self.waiting_list = []
        self.last_player = None

        self.f_exiting = False
        self.state = STATE_LOBBY

        # State flags
        self.f_need_rolls = False
        self.f_need_territories = False
        self.f_need_armies = False

        # Territories
        self.territories = {
            # North America
            next(GameState.gen_id): Territory("Greenland", (255, 255, 0, 255), "Greenland_highlight.png"),
            next(GameState.gen_id): Territory("Northwest Territory", (255, 255, 1, 255), "NWTer_highlight.png"),
            next(GameState.gen_id): Territory("Alaska", (255, 255, 2, 255), "Alaska_highlight.png"),
            next(GameState.gen_id): Territory("Alberta", (255, 255, 3, 255), "Alberta_highlight.png"),
            next(GameState.gen_id): Territory("Ontario", (255, 255, 4, 255), "Ontario_highlight.png"),
            next(GameState.gen_id): Territory("Eastern Canada", (255, 255, 5, 255), "EasternCan_highlight.png"),
            next(GameState.gen_id): Territory("Western US", (255, 255, 6, 255), "WestUS_highlight.png"),
            next(GameState.gen_id): Territory("Eastern US", (255, 255, 7, 255), "EastUS_highlight.png"),
            next(GameState.gen_id): Territory("Central America", (255, 255, 8, 255), "CentralAmerica_highlight.png"),
            # South America
            next(GameState.gen_id): Territory("Argentina", (255, 127, 0, 255), "Argentina_highlight.png"),
            next(GameState.gen_id): Territory("Brazil", (255, 127, 1, 255), "Brazil_highlight.png"),
            next(GameState.gen_id): Territory("Peru", (255, 127, 2, 255), "Peru_highlight.png"),
            next(GameState.gen_id): Territory("Venezuela", (255, 127, 3, 255), "Venezuela_highlight.png"),
            # Africa
            next(GameState.gen_id): Territory("North Africa", (127, 127, 127, 255), "NorthAfrica_highlight.png"),
            next(GameState.gen_id): Territory("Egypt", (128, 128, 128, 255), "Egypt_highlight.png"),
            next(GameState.gen_id): Territory("East Africa", (129, 129, 129, 255), "EastAfrica_highlight.png"),
            next(GameState.gen_id): Territory("Central Africa", (130, 130, 130, 255), "CentralAfrica_highlight.png"),
            next(GameState.gen_id): Territory("South Africa", (131, 131, 131, 255), "SouthAfrica_highlight.png"),
            next(GameState.gen_id): Territory("Madagascar", (132, 132, 132, 255), "Madagascar_highlight.png"),
            # Europe
            next(GameState.gen_id): Territory("Iceland", (0, 0, 255, 255), "Iceland_highlight.png"),
            next(GameState.gen_id): Territory("Great Britain", (1, 0, 255, 255), "GreatBritain_highlight.png"),
            next(GameState.gen_id): Territory("Scandanavia", (2, 0, 255, 255), "Scandanavia_highlight.png"),
            next(GameState.gen_id): Territory("Russia", (3, 0, 255, 255), "Russia_highlight.png"),
            next(GameState.gen_id): Territory("Northern Europe", (4, 0, 255, 255), "NorthernEurope_highlight.png"),
            next(GameState.gen_id): Territory("Western Europe", (5, 0, 255, 255), "WesternEurope_highlight.png"),
            next(GameState.gen_id): Territory("Southern Europe", (6, 0, 255, 255), "SouthernEurope_highlight.png"),
            # Asia
            next(GameState.gen_id): Territory("Kamchatka", (0, 255, 0, 255), "Kamchatka_highlight.png"),
            next(GameState.gen_id): Territory("Yakutsk", (1, 255, 0, 255), "Yakutsk_highlight.png"),
            next(GameState.gen_id): Territory("Siberia", (2, 255, 0, 255), "Siberia_highlight.png"),
            next(GameState.gen_id): Territory("Ural", (3, 255, 0, 255), "Ural_highlight.png"),
            next(GameState.gen_id): Territory("Irkutsk", (4, 255, 0, 255), "Irkutsk_highlight.png"),
            next(GameState.gen_id): Territory("Mongolia", (5, 255, 0, 255), "Mongolia_highlight.png"),
            next(GameState.gen_id): Territory("Japan", (6, 255, 0, 255), "Japan_highlight.png"),
            next(GameState.gen_id): Territory("Afghanistan", (7, 255, 0, 255), "Afghanistan_highlight.png"),
            next(GameState.gen_id): Territory("China", (8, 255, 0, 255), "China_highlight.png"),
            next(GameState.gen_id): Territory("Middle East", (9, 255, 0, 255), "MiddleEast_highlight.png"),
            next(GameState.gen_id): Territory("India", (10, 255, 0, 255), "India_highlight.png"),
            next(GameState.gen_id): Territory("Southeast Asia", (11, 255, 0, 255), "SoutheastAsia_highlight.png"),
            # Australia
            next(GameState.gen_id): Territory("Indonesia", (255, 0, 255, 255), "Indonesia_highlight.png"),
            next(GameState.gen_id): Territory("New Guinea", (255, 1, 255, 255), "NewGuinea_highlight.png"),
            next(GameState.gen_id): Territory("Western Australia", (255, 2, 255, 255), "WesternAustralia_highlight.png"),
            next(GameState.gen_id): Territory("Eastern Australia", (255, 3, 255, 255), "EasternAustralia_highlight.png"),
        }

    @property
    def f_waiting(self):
        return len(self.waiting_list) > 0

    @f_waiting.setter
    def f_waiting(self, val):
        pass

    def draw(self, window) -> None:
        # draw background
        if self.bg:
            window.blit(self.bg, (0, 0))

    # Change the current game state
    def set_state(self, new_state: int) -> None:
        if self.state == new_state:
            return

        logging.info(f"Changing state: {STATE_STR[self.state]} --> {STATE_STR[new_state]} ")

        if new_state == STATE_INITIAL_ARMY_PLACEMENT:
            if self.f_host:
                state_frame = frames.build_frame_set_state(self, new_state)
                self.send_all(state_frame)
                self.add_waiting(self.players)
            else:
                self.add_waiting(self.players)
                # XXX Ultimately this will be a fun looking message displayed
                print("Roll an attack die for first! (press r)")
                self.f_need_rolls = True

                if self.f_auto_roll:
                    frame = frames.build_frame_roll(self, self.local_player.ID, 1, 0)
                    self.local_player.socket.socket.sendall(frame)

            self.players.sort(key=lambda x: x.ID)
            for p in self.players:
                p.free_armies = {2: 40, 3: 35, 4: 30, 5: 25, 6: 20}[len(self.players)]

        self.state = new_state

    def add_player(self, p) -> None:
        if p not in self.players:
            self.players.append(p)
            logging.info(f"Player {p.name} added")
        else:
            logging.warning(f"Player ID {p.ID} already known")

    def remove_player(self, p) -> None:
        try:
            self.players.remove(p)
            logging.info(f"Player {p.name} has left")
        except ValueError:
            logging.debug(f"Player already removed: {p}")

    def get_player(self, player_id) -> Player:
        for p in self.players:
            if p.ID == player_id:
                return p
        return None

    def get_next_player(self, player_id: int) -> Player:
        for i in range(len(self.players)):
            if i == (len(self.players) - 1):
                return self.players[0]
            if self.players[i].ID == player_id:
                return self.players[i + 1]

    def get_territory(self, tid: int) -> Territory:
        return self.territories[tid]

    def get_sockets(self) -> list:
        return [p.socket for p in self.players]

    # Send data to all players, except those in 'exceptions'
    def send_all(self, data, exceptions=None):
        for p in self.players:
            if not exceptions or p not in exceptions:
                p.socket.socket.sendall(data)

    # Have the host wait for players
    def add_waiting(self, players: list) -> None:
        self.waiting_list.extend(players)

    # Remove a player from the waiting list
    def remove_waiting(self, p: Player) -> None:
        self.waiting_list.remove(p)
        self.last_player = p

    # Return True if host is waiting for this player
    def waiting_for(self, p: Player) -> bool:
        return p in self.waiting_list


# Print a message from the Server
def print_server(msg: str) -> None:
    print(utilities.ANSI_RED + msg + utilities.ANSI_RESET)


# Processes network input from a given player
def process_input(gs, p):
    s = p.socket
    try:
        data = s.socket.recv(BUFFER_SIZE)
        if not data:
            logging.debug(f"{s.socket.getpeername()} has disconnected")
            s.closed = True

        while data:
            if data[0] == frames.FRAME_CHAT:
                player_id, msg = frames.process_frame_chat(gs, data)
                if player_id == SERVER_ID:
                    print_server(msg)
                else:
                    sender = gs.get_player(player_id)
                    if sender:
                        name = sender.name
                    else:
                        name = None
                    if gs.f_host:
                        logging.debug(f"{name} {s.socket.getpeername()}: {msg}")
                        if msg == COMMAND_EXIT:
                            s.closed = True
                        elif msg == COMMAND_SHUTDOWN:
                            gs.f_exiting = True
                        elif msg == COMMAND_START:
                            gs.set_state(STATE_INITIAL_ARMY_PLACEMENT)
                        else:
                            for s2 in [x for x in gs.get_sockets() if x != s]:
                                chat_frame = frames.build_frame_chat(gs, player_id, msg)
                                s2.socket.sendall(chat_frame)
                                logging.debug(f"Sent {s2.socket.getpeername()} "
                                              f"frame {chat_frame}")
                    else:
                        print(f"{name}: {msg}")
                data = data[frames.FRAME_CHAT_LEN + len(msg):]
            elif data[0] == frames.FRAME_ROLL:
                frames.process_frame_roll(gs, data)
                data = data[frames.FRAME_ROLL_LEN:]
            elif data[0] == frames.FRAME_ROLL_RESULT:
                var_len = frames.process_frame_roll_result(gs, data)
                data = data[frames.FRAME_ROLL_RESULT_LEN + var_len:]
            elif data[0] == frames.FRAME_ADD_PLAYER:
                if gs.f_host:
                    logging.error(f"Server sent ADD_PLAYER frame: {data}")
                    break

                new_player = frames.process_frame_add_player(gs, data)
                gs.add_player(new_player)
                data = data[frames.FRAME_ADD_PLAYER_LEN + len(new_player.name):]
            elif data[0] == frames.FRAME_SET_ID:
                if gs.f_host:
                    logging.error(f"Client sent SET_ID frame: {data}")

                frames.process_frame_set_id(gs, data)
                data = data[frames.FRAME_SET_ID_LEN:]
            elif data[0] == frames.FRAME_SET_NAME:
                if not gs.f_host:
                    logging.error(f"Server sent SET_NAME frame: {data}")
                    break

                # Assign new player an ID
                while p.ID is None or p.ID in [p2.ID for p2 in gs.players if p2 != p]:
                    p.ID = random.randint(1, 255)
                # Set name
                frames.process_frame_set_name(gs, data, p)

                # Inform player of their ID
                id_frame = frames.build_frame_set_id(gs, p.ID)
                s.socket.sendall(id_frame)

                # Inform player of current players and current players of new player
                new_player_frame = frames.build_frame_add_player(gs, p.ID, p.name)
                for p2 in gs.players:
                    if p2 != p:
                        player_frame = frames.build_frame_add_player(gs, p2.ID, p2.name)
                        s.socket.sendall(player_frame)
                        p2.socket.socket.sendall(new_player_frame)

                data = data[frames.FRAME_SET_NAME_LEN + len(p.name):]
            elif data[0] == frames.FRAME_SET_STATE:
                frames.process_frame_set_state(gs, data)
                data = data[frames.FRAME_SET_STATE_LEN:]
            elif data[0] == frames.FRAME_SELECT_TERRITORY:
                frames.process_frame_select_territory(gs, data)
                data = data[frames.FRAME_SELECT_TERRITORY_LEN:]
            else:
                logging.error(f"Unknown frame type {data[0]}, data {data}")
                break
    except BlockingIOError:
        pass
    except ConnectionResetError:
        logging.debug(f"{s.socket.getpeername()} has disconnected")
        s.closed = True
    except ConnectionAbortedError:
        logging.debug(f"{s.socket.getpeername()} has disconnected")
        s.closed = True

    if s.closed and gs.f_host:
        gs.remove_player(p)


# Update state INITIAL_ARMY_PLACEMENT
def run_state_iap(gs: GameState) -> None:
    # Determine turn order
    if gs.f_need_rolls and not gs.f_waiting:
        gs.f_need_rolls = False
        highest_roll = [0, None]
        for p in gs.players:
            assert p.f_new_roll
            if p.attack_roll[0] > highest_roll[0]:
                highest_roll[0] = p.attack_roll[0]
                highest_roll[1] = p
            p.f_new_roll = False
        print(f"{highest_roll[1].name} goes first!")
        # Set turn order
        gs.players.remove(highest_roll[1])
        gs.players.insert(0, highest_roll[1])
        gs.f_need_territories = True
        gs.add_waiting([gs.players[0]])

    # Territory placement
    if gs.f_need_territories and not gs.f_waiting:
        gs.f_need_territories = False
        gs.f_need_armies = True
        gs.add_waiting([gs.get_next_player(gs.last_player.ID)])
        print("All territories claimed! Awaiting troop placement.")

    # Army placement
    if gs.f_need_armies and not gs.f_waiting:
        gs.f_need_armies = False
        print("All armies placed! Setup complete.")


# Update game state
def update(gs: GameState) -> None:
    # Go back to lobby if all players leave
    if gs.state != STATE_LOBBY and len(gs.players) == 0:
        gs.set_state(STATE_LOBBY)

    # Auto IAP
    if not gs.f_host and gs.f_auto_place and gs.waiting_for(gs.local_player):
        if gs.f_need_territories:
            for ID, t in gs.territories.items():
                if t.pid is None:
                    frame = frames.build_frame_select_territory(gs, gs.local_player.ID, ID)
                    gs.local_player.socket.socket.sendall(frame)
        elif gs.f_need_armies:
            # Picking a random territory from the set
            it = iter(gs.local_player.territories)
            tid = next(it)
            for i in range(random.randint(0, len(gs.local_player.territories) - 1)):
                tid = next(it)
            frame = frames.build_frame_select_territory(gs, gs.local_player.ID, tid)
            gs.local_player.socket.socket.sendall(frame)

    if is_left_clicked():
        pos = get_mouse_pos()
        color = tuple(gs.bg.get_at(pos))
        # XXX find territory by color function
        for tid, t in gs.territories.items():
            if t.color == color:
                logging.debug(f"Local player clicked on {t.name}")
                if not gs.f_host:
                    frame = frames.build_frame_select_territory(gs,
                                                                gs.local_player.ID,
                                                                tid)
                    gs.local_player.socket.socket.sendall(frame)

    if gs.state == STATE_LOBBY:
        return
    elif gs.state == STATE_INITIAL_ARMY_PLACEMENT:
        run_state_iap(gs)
