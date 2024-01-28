class Card:
    def __init__(self, color, number):
        self.color = color
        self.number = number

    def __repr__(self):
        return f"{self.color}{self.number}"

def create_deck(number_of_players):
    colors = ['Red', 'Blue', 'Green', 'Yellow', 'White'][:number_of_players]
    deck = [Card(color, number) for color in colors for number in [1, 1, 1, 2, 2, 3, 3, 4, 4, 5]]
    random.shuffle(deck)
    return deck

class GameServer(Process):
    def __init__(self, shared_tokens, shared_hands, played_cards):
        super().__init__()
        self.shared_tokens = shared_tokens
        self.shared_hands = shared_hands
        self.played_cards = played_cards
        self.server_socket = IPC.create_server_socket('localhost', 8000)
        self.player_connections = []
        self.lock = Lock()

class GameServer(Process):
    def __init__(self, shared_tokens, shared_hands, played_cards):
        super().__init__()
        self.shared_tokens = shared_tokens
        self.shared_hands = shared_hands
        self.played_cards = played_cards
        self.server_socket = IPC.create_server_socket('localhost', 8000)
        self.player_connections = []

    def run(self):
        # 创建并启动玩家进程
        self.player_processes = [pl.Player(player_id, self.shared_tokens, self.shared_hands, self.played_cards) for player_id in range(len(self.shared_hands))]
        for player_process in self.player_processes:
            player_process.start()
            client_socket, _ = IPC.accept_client_connection(self.server_socket)
            self.player_connections.append(client_socket)

        # 为每个玩家创建一个线程来处理其动作
        player_threads = []
        for client_socket in self.player_connections:
            player_thread = Thread(target=self.handle_player_connection, args=(client_socket,))
            player_threads.append(player_thread)
            player_thread.start()

        # 等待所有线程完成
        for player_thread in player_threads:
            player_thread.join()

        # 游戏结束，关闭所有连接
        for client_socket in self.player_connections:
            client_socket.close()
        for player_process in self.player_processes:
            player_process.join()

    def handle_player_connection(self, client_socket):
        while not self.is_game_over():
            data = IPC.receive_data(client_socket)
            if data:
                # TODO: 根据接收到的数据处理玩家动作
                # 例如: self.handle_player_action(data)

                # TODO: 更新游戏状态
                # 例如: self.update_game_state()
                with self.lock:
                    pass

                # 将更新后的游戏状态发送给所有玩家
                # TODO: 格式化游戏状态数据
                # 例如: game_state_data = self.format_game_state()
                for client_socket in self.player_connections:
                    IPC.send_data(client_socket, b'Update or Response')


    def is_game_over(self):
        # number of fives played
        num_fives = sum(1 for card in self.played_cards if card.number == 5)
        # win condition
        if num_fives == len(self.shared_hands):
            print("Game Won - All 5s have been played successfully.")
            return True
        # lose condition
        if self.shared_tokens['fuse_tokens'] <= 0:
            print("Game Over - All fuse tokens used up.")
            return True
        return False