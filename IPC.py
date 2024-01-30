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

                self.start_game()

    def start_game(self):
        # 游戏逻辑的开始
        pass

    # 其他方法不变...




    def update_and_broadcast(self):
        # 每轮开始时广播当前轮数和令牌数量
        round_info = {
            "type": "round_info",
            "round": self.game_logic.round,
            "info_tokens": self.game_logic.shared_tokens['info_tokens'],
            "fuse_tokens": self.game_logic.shared_tokens['fuse_tokens']
        }
        self.broadcast(json.dumps(round_info))

        # 向每个玩家发送其他玩家的手牌信息
        for player_id, player_socket in self.player_ids.items():
            hands_info = self.game_logic.show_other_players_hands(player_id)
            self.send_message_to_player(player_socket, hands_info)

        # 询问当前轮到的玩家进行行动选择
        current_player_id = self.determine_current_player()
        current_player_socket = self.get_socket_by_player_id(current_player_id)
        prompt = {"type": "action_prompt", "message": "Your turn. Choose action (1: play_card, 2: give_info):"}
        self.send_message_to_player(current_player_socket, json.dumps(prompt))

    def broadcast(self, message):
        with self.lock:
            for player_socket in self.player_sockets:
                try:
                    player_socket.sendall(message.encode())
                except Exception as e:
                    print(f"Error broadcasting to player {player_socket}: {e}")

    def send_message_to_player(self, player_socket, message):
        try:
            player_socket.sendall(message.encode())
        except Exception as e:
            print(f"Error sending message to player {player_socket}: {e}")

    def get_socket_by_player_id(self, player_id):
        for socket, id in self.player_ids.items():
            if id == player_id:
                return socket

    def determine_current_player(self):
        # 确定当前轮到哪个玩家
        # 这里需要一种机制来跟踪当前轮到的玩家。这可能是一个简单的轮流机制，也可以更复杂。
        # 例如:
        return (self.game_logic.round - 1) % self.num_players + 1