# Frames types
import random
import logging

import game
import player

FRAME_CHAT = 0
FRAME_ROLL = 1
FRAME_ROLL_RESULT = 2
FRAME_ADD_PLAYER = 3
FRAME_SET_ID = 4
FRAME_SET_NAME = 5
FRAME_SET_STATE = 6
FRAME_SELECT_TERRITORY = 7

FRAME_CHAT_LEN = 4  # + len(msg)
FRAME_ROLL_LEN = 4
FRAME_ROLL_RESULT_LEN = 4 # + number of dice rolls
FRAME_ADD_PLAYER_LEN = 4  # + len(name)
FRAME_SET_ID_LEN = 2
FRAME_SET_NAME_LEN = 3  # + len(name)
FRAME_SET_STATE_LEN = 2
FRAME_SELECT_TERRITORY_LEN = 3


# Frame type(1), player ID(1), msg_len(2), msg(...)
def build_frame_chat(gs, sender_id, msg) -> bytes:
    frame = FRAME_CHAT.to_bytes(1, byteorder='big') +\
        sender_id.to_bytes(1, byteorder='big') +\
        len(msg).to_bytes(2, byteorder='big') + msg.encode('utf-8')
    return frame


def process_frame_chat(gs, frame) -> tuple:
    sender_id = frame[1]
    msg_len = int.from_bytes(frame[2:4], byteorder='big')
    msg = frame[4:4+msg_len].decode('utf-8')
    logging.debug(f"Received CHAT frame: ID {sender_id}, msg_len {msg_len}, "
                  f"msg {msg}")
    return sender_id, msg


# Frame type(1), player ID(1), num_attack(1), num_defense(1)
def build_frame_roll(gs, player_id, num_attack, num_defense) -> bytes:
    frame = FRAME_ROLL.to_bytes(1, byteorder='big') +\
        player_id.to_bytes(1, byteorder='big')
    frame += min(num_attack, 6).to_bytes(1, byteorder='big') +\
        min(num_defense, 6).to_bytes(1, byteorder='big')
    return frame


def process_frame_roll(gs, frame) -> None:
    player_id = frame[1]
    num_attack = frame[2]
    num_defense = frame[3]
    attack = [random.randint(1, 6) for _ in range(num_attack)]
    defense = [random.randint(1, 6) for _ in range(num_defense)]
    logging.debug(f"Received FRAME_ROLL: ID {player_id}, num_attack {num_attack}, "
                  f"num_defense {num_defense}")
    p = gs.get_player(player_id)
    p.set_roll(attack, defense)
    print(f"{p.name} rolled {p.print_last_roll()}")

    # Remove player from waiting list
    if gs.f_need_rolls and gs.waiting_for(p):
        gs.remove_waiting(p)

    # Inform other players
    if gs.f_host:
        frame = build_frame_roll_result(gs, player_id, attack, defense)
        gs.send_all(frame)


# Frame type(1), player ID(1), len(attack)(1), attack(...)
# len(defense)(1), defense(...)
def build_frame_roll_result(gs, player_id, attack, defense) -> bytes:
    frame = FRAME_ROLL_RESULT.to_bytes(1, byteorder='big') +\
            player_id.to_bytes(1, byteorder='big') +\
            len(attack).to_bytes(1, byteorder='big')
    for roll in attack:
        frame += roll.to_bytes(1, byteorder='big')
    frame += len(defense).to_bytes(1, byteorder='big')
    for roll in defense:
        frame += roll.to_bytes(1, byteorder='big')
    return frame


# Returns the additional frame length from dice rolls
def process_frame_roll_result(gs, frame) -> int:
    index = 1
    player_id = frame[index]
    index += 1
    num_attack = frame[index]
    index += 1
    attack = list(frame[index:index + num_attack])
    index += num_attack
    num_defense = frame[index]
    index += 1
    defense = list(frame[index:index + num_defense])
    logging.debug(f"Received FRAME_ROLL_RESULT: ID {player_id}, num_attack "
                  f"{num_attack} {attack}, num_defense {num_defense} {defense}")

    p = gs.get_player(player_id)
    p.set_roll(attack, defense)
    print(f"{p.name} rolled {p.print_last_roll()}")

    if gs.f_need_rolls and gs.waiting_for(p):
        gs.remove_waiting(p)

    return num_attack + num_defense


# Frame type(1), player ID(1), name_len(2), name(...)
def build_frame_add_player(gs, player_id, name) -> bytes:
    frame = FRAME_ADD_PLAYER.to_bytes(1, byteorder='big') +\
            player_id.to_bytes(1, byteorder='big') +\
            len(name).to_bytes(2, byteorder='big') + name.encode('utf-8')
    return frame


def process_frame_add_player(gs, frame) -> player.Player2:
    ID = frame[1]
    name_len = int.from_bytes(frame[2:4], byteorder='big')
    name = frame[4:4 + name_len].decode('utf-8')
    logging.debug(f"Received ADD_PLAYER: ID {ID}, name_len {name_len}, name {name}")
    return player.Player(player_id=ID, name=name)


# Frame type(1), player ID(1)
def build_frame_set_id(gs, player_id) -> bytes:
    frame = FRAME_SET_ID.to_bytes(1, byteorder='big') +\
            player_id.to_bytes(1, byteorder='big')
    return frame


def process_frame_set_id(gs, frame) -> None:
    ID = frame[1]
    # XXX validation
    logging.debug(f"Received SET_ID: ID {ID}, frame {frame}")
    logging.debug(f"Player ID changed from {gs.local_player.ID} to {ID}")
    gs.local_player.ID = ID


# Frame type(1), name_len(2), name(...)
def build_frame_set_name(gs, name) -> bytes:
    frame = FRAME_SET_NAME.to_bytes(1, byteorder='big') +\
            len(name).to_bytes(2, byteorder='big') + name.encode('utf-8')
    return frame


def process_frame_set_name(gs, frame, p) -> None:
    name_len = int.from_bytes(frame[1:3], byteorder='big')
    name = frame[3:3 + name_len].decode('utf-8')
    # XXX Validation
    logging.debug(f"Received SET_NAME: name len {name_len}, name {name}")
    logging.debug(f"Player ID {p.ID}: name changed from {p.name} to {name}")
    p.name = name


# Frame type(1), state(1)
def build_frame_set_state(gs, state) -> bytes:
    frame = FRAME_SET_STATE.to_bytes(1, byteorder='big') +\
        state.to_bytes(1, byteorder='big')
    return frame


def process_frame_set_state(gs, frame) -> None:
    state = frame[1]
    logging.debug(f"Received SET_STATE: state {state}")
    gs.set_state(state)


# Frame type(1), player id(1), territory id(1)
def build_frame_select_territory(gs, pid: int, tid: int) -> bytes:
    frame = FRAME_SELECT_TERRITORY.to_bytes(1, byteorder='big') +\
        pid.to_bytes(1, byteorder='big') + tid.to_bytes(1, byteorder='big')
    return frame


def process_frame_select_territory(gs, frame: bytes) -> None:
    pid = frame[1]
    tid = frame[2]
    p = gs.get_player(pid)
    t = gs.get_territory(tid)
    logging.debug(f"Received SELECT_TERRITORY: player id {pid}, territory id {tid}")
    print(f"{p.name} selected {t.name}")

    if gs.f_need_territories and gs.waiting_for(p):
        if t.pid is None:
            t.conquer(pid, 1)
            p.add_territory(tid)
            gs.remove_waiting(p)
            if sum([len(p.territories) for p in gs.players]) != len(gs.territories):
                gs.add_waiting([gs.get_next_player(pid)])
        elif p is gs.local_player:
            print(f"{t.name} is occupied by {gs.get_player(t.pid).name}. Choose another territory.")
    elif gs.f_need_armies and gs.waiting_for(p):
        if t.pid is None or t.pid != pid:
            print(f"{t.name} is occupied by {gs.get_player(t.pid).name}. Choose another territory.")
        else:
            t.add_armies(1)
            p.n_free_armies -= 1
            gs.remove_waiting(p)
            next_player = gs.get_next_player(pid)
            if next_player.n_free_armies > 0:
                gs.add_waiting(next_player)

    if gs.f_host:
        gs.send_all(frame[:FRAME_SELECT_TERRITORY_LEN])
