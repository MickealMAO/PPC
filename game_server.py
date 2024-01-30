import socket
import threading
import concurrent.futures
import select
import errno
import Hannabis as h
import json

class GameServer:
    def __init__(self, host, port, num_players):
        self.host = host
        self.port = port
        self.num_players = num_players
        self.game_logic = h.GameLogic(num_players)
        self.lock = threading.Lock()
        self.player_ids = {}  # 将套接字映射到玩家ID
        self.next_player_id = 1  # 下一个玩家的ID
        self.players_connected = 0  # 当前连接的玩家数量
        self.all_players_connected = threading.Condition(self.lock)  # 用于通知所有玩家都已连接

    def start(self):
        print("Starting server...")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setblocking(False)
            server_socket.bind((self.host, self.port))
            server_socket.listen(self.num_players)

            with concurrent.futures.ThreadPoolExecutor(max_workers=self.num_players) as executor:
                while True:
                    readable, _, _ = select.select([server_socket] + list(self.player_ids.values()), [], [])
                    for s in readable:
                        if s is server_socket:
                            player_socket, address = server_socket.accept()
                            player_socket.setblocking(False)
                            self.player_ids[self.next_player_id] = player_socket
                            executor.submit(self.handle_player, player_socket, self.next_player_id)
                            with self.lock:
                                self.players_connected += 1
                                if self.players_connected == self.num_players:
                                    self.all_players_connected.notify_all()
                            self.next_player_id += 1
                        else:
                            player_id = [id for id, socket in self.player_ids.items() if socket == s][0]
                            executor.submit(self.handle_player, s, player_id)

                # 等待所有玩家连接
                with self.lock:
                    while self.players_connected < self.num_players:
                        self.all_players_connected.wait()

                # 所有玩家都已连接，可以开始游戏
                self.start_game()

    def start_game(self):
        # start the game
        self.broadcast("Starting the game...")
        self.broadcast(f"Hello! There are {self.num_players} players in the game.")

        # Assign and notify player IDs
        for player_id in range(1, self.num_players + 1):
            self.send_message_to_player(player_id, f"Your player ID is {player_id}.")

        # Start the rounds
        while not self.game_logic.is_game_over():
            self.broadcast(f"\n--- Round {self.game_logic.round} ---")
            for player_id in range(1, self.num_players + 1):
                self.broadcast(f"\nPlayer {player_id}'s turn.")
                self.broadcast(f"Information tokens: {self.game_logic.shared_tokens['info_tokens']}, Fuse tokens: {self.game_logic.shared_tokens['fuse_tokens']}")

                # Send each player their view of other players' hands
                for view_id in range(1, self.num_players + 1):
                    hands_info = self.game_logic.show_other_players_hands(view_id)
                    self.send_message_to_player(view_id, "Other players' hands:\n" + hands_info)

                # 等待并处理玩家响应
                # ...

                if self.game_logic.is_game_over():
                    break
            self.game_logic.round += 1
        self.broadcast("Game concluded.")


    def handle_player(self, player_socket, player_id):
        try:
            while not self.game_logic.is_game_over():
                data = player_socket.recv(1024).decode()
                if not data:
                    break
                print(f"Received from player {player_id}: {data}")

                # TODO: 处理数据，执行游戏逻辑

        except Exception as e:
            print(f"Error in handling player socket {player_id}: {e}")
        finally:
            player_socket.close()
            with self.lock:
                self.player_ids.pop(player_id)


    def broadcast(self, message):
        with self.lock:
            for player_socket in self.player_ids.values():
                try:
                    player_socket.sendall(message.encode())
                except Exception as e:
                    print(f"Error broadcasting to player {player_socket}: {e}")
    
    def send_message_to_player(self, player_id, message):
        try:
            self.player_ids[player_id].sendall(message.encode())
        except Exception as e:
            print(f"Error sending message to player {self.player_ids[player_id]}: {e}")


    # def format_game_state(self):
    #     state = {
    #         "round": self.game_logic.round,
    #         "info_tokens": self.game_logic.shared_tokens['info_tokens'],
    #         "fuse_tokens": self.game_logic.shared_tokens['fuse_tokens'],
    #         "hands": {player_id: str(hand) for player_id, hand in self.game_logic.shared_hands.items()},
    #         "played_cards": str(self.game_logic.played_cards)
    #     }
    #     return json.dumps(state)


# Example usage
if __name__ == "__main__":
    num_players = h.get_number_of_players()
    server = GameServer("localhost", 2050, num_players)
    server.start()
