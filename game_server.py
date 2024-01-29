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
        self.player_sockets = []
        self.lock = threading.Lock()
        self.player_ids = {}  # 将套接字映射到玩家ID

    def start(self):
        print("Starting server...")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setblocking(False)
            server_socket.bind((self.host, self.port))
            server_socket.listen(self.num_players)

            with concurrent.futures.ThreadPoolExecutor(max_workers=self.num_players) as executor:
                while not self.game_logic.is_game_over():
                    readable, _, _ = select.select([server_socket] + self.player_sockets, [], [])
                    for s in readable:
                        if s is server_socket:
                            player_socket, address = server_socket.accept()
                            player_socket.setblocking(False)
                            self.player_sockets.append(player_socket)
                            player_id = len(self.player_sockets)
                            self.player_ids[player_socket] = player_id
                            executor.submit(self.handle_player, player_socket, player_id)
                        else:
                            executor.submit(self.handle_player, s, self.player_ids[s])

        # 游戏结束后关闭所有套接字
        for sock in self.player_sockets:
            sock.close()

    def handle_player(self, player_socket, player_id):
        try:
            while not self.game_logic.is_game_over():
                data = player_socket.recv(1024).decode()
                if not data:
                    break

                # 解析接收到的数据
                action_data = json.loads(data)
                action = action_data.get("action")
                message = action_data.get("message")

                # 处理玩家动作
                self.execute_action(action, message, player_id)

                # 更新并广播游戏状态
                self.update_and_broadcast()
        except Exception as e:
            print(f"Error in handling player socket {player_id}: {e}")
        finally:
            player_socket.close()
            with self.lock:
                self.player_sockets.remove(player_socket)
                del self.player_ids[player_socket]

    def execute_action(self, action, message, player_id):
        if action == "play_card":
            self.game_logic.play_card(player_id, message)
        elif action == "give_info":
            # 分析并执行给予信息的动作
            # ...

    def update_and_broadcast(self):
        game_state = self.format_game_state()
        self.broadcast(game_state)

    def format_game_state(self):
        # 格式化游戏状态
        state = {
            "round": self.game_logic.round,
            "info_tokens": self.game_logic.shared_tokens['info_tokens'],
            "fuse_tokens": self.game_logic.shared_tokens['fuse_tokens'],
            "hands": {player_id: str(hand) for player_id, hand in self.game_logic.shared_hands.items()},
            "played_cards": str(self.game_logic.played_cards)
        }
        return json.dumps(state)

    def broadcast(self, message):
        with self.lock:
            for player_socket in self.player_sockets:
                try:
                    player_socket.sendall(message.encode())
                except Exception as e:
                    print(f"Error broadcasting to player {player_socket}: {e}")

# Example usage
if __name__ == "__main__":
    num_players = h.get_number_of_players()
    server = GameServer("localhost", 2050, num_players)
    server.start()
