import random

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

class GameLogic:
    def __init__(self, number_of_players):
        self.number_of_players = number_of_players
        self.deck = create_deck(number_of_players)
        self.shared_tokens = {'info_tokens': number_of_players + 3, 'fuse_tokens': 3}
        self.shared_hands = {player_id: [self.deck.pop() for _ in range(5)] for player_id in range(1, number_of_players + 1)}
        self.played_cards = []
        self.round = 1

    def show_other_players_hands(self, player_id):
        hands_display = "\n".join(f"Player {id}: {', '.join(map(str, hand))}" for id, hand in self.shared_hands.items() if id != player_id)
        return hands_display

    def play_card(self, player_id, card_letter):
        card_index = ord(card_letter.lower()) - ord('a')
        hand = self.shared_hands[player_id]
        card = hand.pop(card_index)
        print(f"Player {player_id} played {card}.")
        if self.is_play_valid(card):
            self.played_cards.append(card)
            if card.number == 5:
                self.shared_tokens['info_tokens'] += 1
                print("One information token restored.")
        else:
            self.shared_tokens['fuse_tokens'] -= 1
            print("One fuse token consumed.")
        if self.deck:
            hand.append(self.deck.pop())

    def is_play_valid(self, card):
        for played_card in reversed(self.played_cards):
            if played_card.color == card.color:
                return played_card.number == card.number - 1
        return card.number == 1

    def is_game_over(self):
        num_fives = sum(1 for card in self.played_cards if card.number == 5)
        if num_fives == self.number_of_players:
            print("Game Won - All 5s have been played successfully.")
            return True
        if self.shared_tokens['fuse_tokens'] <= 0:
            print("Game Over - All fuse tokens used up.")
            return True
        return False

    def start_game(self):
        print("Starting the game...")
        while not self.is_game_over():
            print(f"\n--- Round {self.round} ---")
            for player_id in range(1, self.number_of_players + 1):
                print(f"\nPlayer {player_id}'s turn.")
                print(f"Information tokens: {self.shared_tokens['info_tokens']}, Fuse tokens: {self.shared_tokens['fuse_tokens']}")
                print("Other players' hands:\n" + self.show_other_players_hands(player_id))
                action = input("Choose action (give_info or play_card): ")
                if action == "play_card":
                    card_letter = input("Which card to play (a-e): ")
                    self.play_card(player_id, card_letter)
                elif action == "give_info":
                    # Implement information giving logic here
                    pass
                if self.is_game_over():
                    break
            self.round += 1
        print("Game concluded.")

# Example usage
if __name__ == "__main__":
    num_players = int(input("Enter the number of players: "))
    game = GameLogic(num_players)
    game.start_game()
