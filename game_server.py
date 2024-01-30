import socket
import threading
import concurrent.futures
import select
import errno
import Hannabis as h
import json

class GameServer:
    """Game server that handles the game logic and communication with players."""
    def __init__(self, host, port, num_players):
        self.host = host
        self.port = port
        self.num_players = num_players
        self.game_logic = h.GameLogic(num_players)
        self.lock = threading.Lock()
        self.player_ids = {} 
        self.next_player_id = 1
        self.players_connected = 0
        self.all_players_connected = threading.Condition(self.lock) 
        self.player_responses = {} 
        self.response_condition = threading.Condition(self.lock) 

    def start(self):
        """Starts the server and waits for players to connect."""
        print("Starting server...")
        print(f"Waiting for {self.num_players} players to connect...")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setblocking(False)
            server_socket.bind((self.host, self.port))
            server_socket.listen(self.num_players)

            with concurrent.futures.ThreadPoolExecutor(max_workers=self.num_players) as executor:
                while self.players_connected < self.num_players:
                    readable, _, _ = select.select([server_socket] + list(self.player_ids.values()), [], [])
                    for s in readable:
                        if s is server_socket:
                            player_socket, address = server_socket.accept()
                            player_socket.setblocking(False)
                            self.player_ids[self.next_player_id] = player_socket
                            executor.submit(self.handle_player, player_socket, self.next_player_id)
                            with self.lock:
                                self.players_connected += 1
                                print('there are ' + str(self.players_connected) + ' players connected')
                                if self.players_connected == self.num_players:
                                    print('all players connected')
                                    self.all_players_connected.notify_all()
                            self.next_player_id += 1

                with self.lock:
                    while self.players_connected < self.num_players:
                        self.all_players_connected.wait()

                # start the game
                self.start_game()

    def start_game(self):
        """Starts the game and handles the game logic."""
        # start the game
        self.broadcast("Starting the game...")
        self.broadcast(f"Hello! There are {self.num_players} players in the game.")

        # Assign and notify player IDs
        for player_id in range(1, self.num_players + 1):
            self.send_message_to_player(player_id, f"Your player ID is {player_id}.")

        # Start the rounds
        while not self.game_logic.is_game_over():
            self.broadcast(f"\n--- Round {self.game_logic.round} ---\n")
            for player_id in range(1, self.num_players + 1):
                self.broadcast(f"Player {player_id}'s turn.\n")
                self.broadcast(f"Information tokens: {self.game_logic.shared_tokens['info_tokens']}, Fuse tokens: {self.game_logic.shared_tokens['fuse_tokens']}\n")

                # Send each player their view of other players' hands
                for view_id in range(1, self.num_players + 1):
                    hands_info = self.game_logic.show_other_players_hands(view_id)
                    self.send_message_to_player(view_id, f"Other players' hands:\n{hands_info}\n")

                # Ask for player action
                action = self.get_player_action(player_id)
                # Do the action
                if action == "play_card" or action == "1":
                    print('player ' + str(player_id) + ' chose to play card')
                    card = self.which_card_to_play(player_id)
                    self.play_card_action(player_id, card)

                elif action == "give_info" or action == "2":
                    print('player ' + str(player_id) + ' chose to give info')
                    self.give_information_action(player_id)

                if self.game_logic.is_game_over():
                    print('game over')
                    break
            self.game_logic.round += 1
        self.broadcast("Game concluded.")


    def handle_player(self, player_socket, player_id):
        """Handles the player's socket connection."""
        try:
            while not self.game_logic.is_game_over():
                try:
                    data = player_socket.recv(1024)
                    if not data:
                        break

                    message = data.decode()
                    print(f"Received message from player {player_id}: {message}")
                    # Detect if the player is sending a response to a request
                    with self.lock:
                        self.player_responses[player_id] = message
                        self.response_condition.notify_all()

                except socket.error as e:
                    if e.errno in (errno.EWOULDBLOCK, errno.EAGAIN):
                        continue
                    else:
                        raise e
        except Exception as e:
            print(f"Error in handling player socket {player_id}: {e}")
        finally:
            player_socket.close()
            with self.lock:
                del self.player_ids[player_id]

    def get_player_action(self, player_id):
        """ask and check for player action"""
        valid_actions = {"1", "2", "play_card", "give_info"}
        while True:
            with self.lock:
                self.player_responses[player_id] = None
            self.send_message_to_player(player_id, "Choose action (1: play_card, 2: give_info): ")
            self.send_message_to_player(player_id, "(Please type it in terminal.)")

            action = self.wait_for_player_response(player_id)

            if action in valid_actions:
                return action
            else:
                self.send_message_to_player(player_id, "Invalid action. Please enter '1' for play_card or '2' for give_info.")

    def which_card_to_play(self, player_id):
        """ask and check for which card to play"""
        valid_cards = {"a", "b", "c", "d", "e"}
        while True:
            with self.lock:
                self.player_responses[player_id] = None
            self.send_message_to_player(player_id, "Which card to play (a-e): ")
            self.send_message_to_player(player_id, "(Please type it in terminal.)") # tell player to open input

            card = self.wait_for_player_response(player_id)

            if card in valid_cards:
                return card
            else:
                self.send_message_to_player(player_id, "Invalid card. Please enter a valid card (a-e).")

    def play_card_action(self, player_id, card_letter):
        """play and check for card action"""
        card_index = ord(card_letter.lower()) - ord('a')
        hand = self.game_logic.shared_hands[player_id]
        # check if card index is valid
        if card_index < 0 or card_index >= len(hand):
            self.broadcast(f"Player {player_id}: Invalid card selection.")
            return
        card = hand.pop(card_index)
        if self.game_logic.is_play_valid(card):
            self.broadcast(f"Player {player_id} played {card} successfully.")
            if card.number == 5:
                self.game_logic.shared_tokens['info_tokens'] += 1
        else:
            self.broadcast(f"Player {player_id} played {card}, but it was not valid.")
            self.game_logic.shared_tokens['fuse_tokens'] -= 1
        self.game_logic.played_cards.append(card)
        if self.game_logic.deck:
            new_card = self.game_logic.deck.pop()
            hand.insert(card_index, new_card)

    def ask_for_target_player_id(self, current_player_id):
        """ask and check for target player id"""
        valid_ids = [id for id in range(1, self.num_players + 1) if id != current_player_id]
        with self.lock:
            self.player_responses[current_player_id] = None
        while True:
            with self.lock:
                self.player_responses[current_player_id] = None
            self.send_message_to_player(current_player_id, f"Enter the target player ID to give information to (options: {', '.join(map(str, valid_ids))}): ")
            self.send_message_to_player(current_player_id, "(Please type it in terminal.)")
            target_id = self.wait_for_player_response(current_player_id)
            if target_id in map(str, valid_ids):
                return int(target_id)
            else:
                self.send_message_to_player(current_player_id, "Invalid player ID. Please choose from the given options.")

    def ask_for_information_type(self, current_player_id):
        """ask and check for information type"""
        valid_colors = self.game_logic.get_valid_colors()
        with self.lock:
            self.player_responses[current_player_id] = None
        while True:
            with self.lock:
                self.player_responses[current_player_id] = None
            self.send_message_to_player(current_player_id, "Enter the information to give (color or number): ")
            self.send_message_to_player(current_player_id, "(Please type it in terminal.)")
            info = self.wait_for_player_response(current_player_id)
            if info.isdigit() and 1 <= int(info) <= 5:
                return info
            elif info.capitalize() in valid_colors:
                return info.capitalize()
            else:
                self.send_message_to_player(current_player_id, "Invalid information type. Please enter a valid color or number.")

    def give_information_action(self, current_player_id):
        """give and check for information action"""
        if self.game_logic.shared_tokens['info_tokens'] <= 0:
            self.broadcast("No information tokens available.")
            return

        target_player_id = self.ask_for_target_player_id(current_player_id)
        info = self.ask_for_information_type(current_player_id)
        informed_cards = self.game_logic.get_informed_cards(target_player_id, info)
        if informed_cards:
            self.game_logic.shared_tokens['info_tokens'] -= 1
            card_positions = ', '.join(informed_cards).lower()
            self.send_message_to_player(target_player_id, f"Player {target_player_id}, your cards {card_positions} are {info}.")
            self.broadcast(f"Information tokens left: {self.game_logic.shared_tokens['info_tokens']}")
        else:
            self.send_message_to_player(current_player_id, "Invalid information provided. Please try again.")


    def wait_for_player_response(self, player_id):
        """wait and return player response"""
        with self.response_condition:
            while self.player_responses[player_id] is None:
                self.response_condition.wait()
        return self.player_responses[player_id]
    

    def broadcast(self, message):
        """broadcast message to all players"""
        with self.lock:
            for player_socket in self.player_ids.values():
                try:
                    player_socket.sendall(message.encode())
                except Exception as e:
                    print(f"Error broadcasting to player {player_socket}: {e}")
    
    def send_message_to_player(self, player_id, message):
        """send message to a player"""
        try:
            self.player_ids[player_id].sendall(message.encode())
        except Exception as e:
            print(f"Error sending message to player {self.player_ids[player_id]}: {e}")



# Example usage
if __name__ == "__main__":
    num_players = h.get_number_of_players()
    server = GameServer("localhost", 12330, num_players)
    server.start()