class Player:
    def __init__(self, name):
        """Initialize a player with name and empty decks"""
        self.name = name
        self.hand = []       # Cards currently in hand
        self.draw_pile = []  # Cards to be drawn
        self.discard_pile = [] # Cards that have been played/discarded
        self.wp = 0          # Win points
        self.current_power = 0 # Power available for purchasing cards
        self.cards_played_this_turn = False
    
    def play_card(self, card_index):
        """Play a card from hand to discard pile"""
        if card_index < 0 or card_index >= len(self.hand):
            print(f"Invalid card index: {card_index}")
            return False
        
        if not self.hand:
            print("No cards in hand to play")
            return False
        
        # Remove card from hand and add to discard pile
        played_card = self.hand.pop(card_index)
        self.discard_pile.append(played_card)
        
        print(f"{self.name} played a card")
        return True
    
    def buy_card(self, market_card, cost):
        """Buy a card from market if player has enough power"""
        if not self.cards_played_this_turn:
            print("Must play all cards in hand before buying")
            return False
        
        if self.current_power < cost:
            print(f"Not enough power. Need {cost}, have {self.current_power}")
            return False
        
        # Deduct cost from current power
        self.current_power -= cost
        # Add card to discard pile
        self.discard_pile.append(market_card)
        
        print(f"{self.name} bought a card for {cost} power")
        print(f"Remaining power: {self.current_power}")
        return True
    
    def draw_card(self):
        """Draw a card from draw pile to hand"""
        if not self.draw_pile:
            # If draw pile is empty, shuffle discard pile into draw pile
            if self.discard_pile:
                self.draw_pile = self.discard_pile[:]
                self.discard_pile.clear()
                print("Shuffled discard pile into draw pile")
            else:
                print("No cards available to draw")
                return False
        
        # Draw card from draw pile to hand
        drawn_card = self.draw_pile.pop(0)
        self.hand.append(drawn_card)
        print(f"{self.name} drew a card")
        return True
    
    def draw_hand(self, hand_size=5):
        """Draw initial hand of cards"""
        cards_drawn = 0
        while len(self.hand) < hand_size and cards_drawn < hand_size:
            if not self.draw_card():
                break
            cards_drawn += 1
        
        print(f"{self.name} drew {cards_drawn} cards for hand")
    
    def end_turn(self):
        """Reset turn-specific states"""
        self.current_power = 0
        self.cards_played_this_turn = False
        print(f"{self.name}'s turn ended")
    
    def add_win_points(self, points):
        """Add win points to player"""
        self.wp += points
        print(f"{self.name} gained {points} win points (Total: {self.wp})")
    
    def get_status(self):
        """Get current player status"""
        return {
            'name': self.name,
            'hand_size': len(self.hand),
            'draw_pile_size': len(self.draw_pile),
            'discard_pile_size': len(self.discard_pile),
            'win_points': self.wp,
            'current_power': self.current_power,
            'cards_played_this_turn': self.cards_played_this_turn
        }
    
    def __str__(self):
        """String representation of player"""
        status = self.get_status()
        return (f"Player: {status['name']} | "
                f"Hand: {status['hand_size']} | "
                f"Draw: {status['draw_pile_size']} | "
                f"Discard: {status['discard_pile_size']} | "
                f"WP: {status['win_points']} | "
                f"Power: {status['current_power']}")


# Example usage and testing
if __name__ == "__main__":
    # Create a test player
    player = Player("TestPlayer")
    
    # Add some mock cards to draw pile for testing
    mock_cards = ["Card1", "Card2", "Card3", "Card4", "Card5"]
    player.draw_pile = mock_cards[:]
    
    print("=== Player Status ===")
    print(player)
    
    print("\n=== Drawing Hand ===")
    player.draw_hand()
    print(player)
    
    print("\n=== Playing All Cards ===")
    player.play_all_cards()
    print(player)
    
    print("\n=== Buying Card ===")
    mock_market_card = "ExpensiveCard"
    player.buy_card(mock_market_card, 3)
    print(player)
    
    print("\n=== Adding Win Points ===")
    player.add_win_points(10)
    print(player)
    
    print("\n=== End Turn ===")
    player.end_turn()
    print(player)
