import socket
import queue
import os
import signal
import random
from threading import Thread, Lock
from multiprocessing import Process, Manager

import IPC
import player as pl
import Hannabis as H
import game_server as gs

# Starting the game server
if __name__ == "__main__":
    number_of_players = 3
    deck = gs.create_deck(number_of_players)

    # Create shared memory objects (tokens and cards)
    with Manager() as manager:
        shared_tokens = manager.dict({'info_tokens': number_of_players + 3, 'fuse_tokens': 3})
        shared_hands = manager.dict()
        played_cards = manager.list()

        # Initialize hands for each player
        for player in range(number_of_players):
            shared_hands[player] = [deck.pop() for _ in range(5)]

    # Create the game server process
    game_server = gs.GameServer(shared_tokens, shared_hands, played_cards)
    game_server.start()
    game_server.join()
