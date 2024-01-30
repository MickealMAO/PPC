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
        # Check if the card index is valid
        if card_index < 0 or card_index >= len(hand):
            print("Invalid card selection. Please choose a valid card.")
            return
        card = hand.pop(card_index)
        self.played_cards.append(card)
        # Check if the played card is valid
        if self.is_play_valid(card):
            print(f"Player {player_id} played {card} successfully.")
            if card.number == 5:
                self.shared_tokens['info_tokens'] += 1  
        else:
            print(f"Player {player_id} played {card}, but it was not valid.")
            self.shared_tokens['fuse_tokens'] -= 1  
        # Draw a new card from the deck to replace the played card
        if self.deck:
            new_card = self.deck.pop()
            hand.insert(card_index, new_card)

    def is_play_valid(self, card):
        """Checks if the played card is valid according to game rules."""
        if card.number == 1:
            return not any(c.color == card.color and c.number == 1 for c in self.played_cards)
        if card.number > 1:
            last_card_played = self.played_cards[-1]
            return card.number == last_card_played.number + 1
        return False  

    def is_game_over(self):
        num_fives = sum(1 for card in self.played_cards if card.number == 5)
        if num_fives == self.number_of_players:
            print("Game Won - All 5s have been played successfully.")
            return True
        if self.shared_tokens['fuse_tokens'] <= 0:
            print("Game Over - All fuse tokens used up.")
            return True
        return False

    def get_player_action(self):
        """Gets and validates the player's action."""
        valid_actions = {"1", "2", "play_card", "give_info"}
        action = input("Choose action (1: play_card, 2: give_info): ")
        while action not in valid_actions:
            print("Invalid action. Please enter '1' for play_card or '2' for give_info.")
            action = input("Choose action (1: play_card, 2: give_info): ")
        return action
    

    def give_information(self, current_player_id):
        if self.shared_tokens['info_tokens'] <= 0:
            print("No information tokens available.")
            return

        while True:
            target_player_id = self.get_target_player_id(current_player_id)
            info = self.get_information_type()
            informed_cards = self.get_informed_cards(target_player_id, info)

            if informed_cards:
                self.shared_tokens['info_tokens'] -= 1
                card_positions = ', '.join(informed_cards).lower()
                print(f"Player {target_player_id}, your cards {card_positions} are {info}.")
                print(f"Information tokens left: {self.shared_tokens['info_tokens']}")
                break
            else:
                print("Invalid information. Please try again.")

    def get_target_player_id(self, current_player_id):
        """Gets a valid target player ID for giving information."""
        valid_ids = [str(id) for id in range(1, self.number_of_players + 1) if id != current_player_id]
        prompt = f"Enter the target player ID to give information to (options: {', '.join(valid_ids)}): "

        while True:
            target_id = input(prompt)
            if target_id in valid_ids:
                return int(target_id)
            else:
                print("Invalid player ID. Please choose from the given options.")

    def get_informed_cards(self, player_id, info):
        """Returns the positions of the cards that match the given information."""
        hand = self.shared_hands[player_id]
        matching_positions = []

        for i, card in enumerate(hand):
            if (info.isdigit() and card.number == int(info)) or (card.color == info):
                matching_positions.append(chr(97 + i))

        return matching_positions

    def get_valid_colors(self):
        """Returns a list of valid colors used in the game."""
        return ['Red', 'Blue', 'Green', 'Yellow', 'White'][:self.number_of_players]

    def get_information_type(self):
        valid_colors = self.get_valid_colors()
        while True:
            info = input("Enter the information to give (color or number): ")
            if info.isdigit() and 1 <= int(info) <= 5:
                return info
            elif info.capitalize() in valid_colors:
                return info.capitalize()
            else:
                print("Invalid information type. Please enter a valid color or number.")

    def start_game(self):
        print("Starting the game...")
        while not self.is_game_over():
            print(f"\n--- Round {self.round} ---")
            for player_id in range(1, self.number_of_players + 1):
                print(f"\nPlayer {player_id}'s turn.")
                print(f"Information tokens: {self.shared_tokens['info_tokens']}, Fuse tokens: {self.shared_tokens['fuse_tokens']}")
                print("Other players' hands:\n" + self.show_other_players_hands(player_id)) 

                action = self.get_player_action()
                if action == "play_card" or action == "1":
                    card_letter = input("Which card to play (a-e): ")
                    self.play_card(player_id, card_letter)
                elif action == "give_info" or action == "2":
                    self.give_information(player_id)

                if self.is_game_over():
                    break
            self.round += 1
        print("Game concluded.")

def get_number_of_players(min_players=2, max_players=5):
    """Gets the number of players, ensuring it's within the valid range."""
    while True:
        try:
            num_players = int(input(f"Enter the number of players ({min_players}-{max_players}): "))
            if min_players <= num_players <= max_players:
                return num_players
            else:
                print(f"Invalid number of players. Please enter a number between {min_players} and {max_players}.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

# Example usage
if __name__ == "__main__":
    num_players = get_number_of_players()
    game = GameLogic(num_players)
    game.start_game()
