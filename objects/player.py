import json
import os
import random
from objects.card import Card

class Player:
    def __init__(self, name):
        """Initialize a player with name and empty decks"""
        self.name = name
        self.hand = []       # Cards currently in hand
        self.draw_pile = []  # Cards to be drawn
        self.discard_pile = [] # Cards that have been played/discarded
        self.turn_power = 0    # Power generated this turn from played cards
    
    def play_card(self, card_index):
        """Play a card from hand to discard pile and add its power/WP"""
        if card_index < 0 or card_index >= len(self.hand):
            print(f"Invalid card index: {card_index}")
            return False
        
        if not self.hand:
            print("No cards in hand to play")
            return False
        
        # Remove card from hand and add to discard pile
        played_card = self.hand.pop(card_index)
        self.discard_pile.append(played_card)
        
        # Add card's power to turn total
        self.turn_power += played_card.getPower()
        
        print(f"{self.name} played {played_card.getName()} (Power: {played_card.getPower()}, WP: {played_card.getWP()})")
        print(f"Turn power: {self.turn_power}")
        return True
    
    def finish_turn(self):
        """Finish turn when no more cards in hand - show final power for purchasing"""
        if self.hand:
            print(f"Still have {len(self.hand)} cards in hand. Play all cards first.")
            return False
        
        print(f"\n=== Turn Complete ===")
        print(f"{self.name} generated {self.turn_power} power this turn")
        print(f"Use this power to buy cards from the market!")
        return True
    
    def buy_card(self, market, card_index):
        """Buy a card from market if player has enough power"""
        if self.turn_power <= 0:
            print("No power available to buy cards!")
            return False
        
        # Attempt to buy card from market
        purchased_card, cost = market.buy_card(card_index, self.turn_power)
        
        if purchased_card is None:
            return False
        
        # Deduct cost from turn power
        self.turn_power -= cost
        
        # Add purchased card to discard pile
        self.discard_pile.append(purchased_card)
        
        print(f"Added {purchased_card.getName()} to discard pile")
        print(f"Remaining power this turn: {self.turn_power}")
        return True
    
    def draw_card(self):
        """Draw a card from draw pile to hand"""
        if not self.draw_pile:
            # If draw pile is empty, shuffle discard pile into draw pile
            if self.discard_pile:
                self.draw_pile = self.discard_pile[:]
                random.shuffle(self.draw_pile)  # Randomize the order
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
        self.turn_power = 0
        print(f"{self.name}'s turn ended")
    
    def calculate_total_wp(self):
        """Calculate total WP from all cards in player's deck (hand + draw + discard)"""
        total_wp = 0
        all_cards = self.hand + self.draw_pile + self.discard_pile
        for card in all_cards:
            total_wp += card.getWP()
        return total_wp
    
    def load_cards_from_json(self, json_file_path):
        """Load cards from JSON file and add to draw pile"""
        try:
            with open(json_file_path, 'r') as file:
                json_data = json.load(file)
                
            # Handle both JSON structures: direct array or wrapped in "cards" key
            if "cards" in json_data:
                cards_data = json_data["cards"]
            else:
                cards_data = json_data
                
            total_cards_loaded = 0
            for card_data in cards_data:
                # Create a card instance
                card_template = Card(
                    card_data['card_index'],
                    card_data['name'],
                    card_data['power'],
                    card_data['cost'],
                    card_data['WP'],
                    card_data.get('count', 1),  # Default to 1 if count not specified
                    card_data.get('ability', card_data.get('Ability', ''))  # Handle both 'ability' and 'Ability'
                )
                
                # Add multiple copies based on count
                count = card_data.get('count', 1)
                for _ in range(count):
                    # Create a new card instance for each copy
                    card_copy = Card(
                        card_data['card_index'],
                        card_data['name'],
                        card_data['power'],
                        card_data['cost'],
                        card_data['WP'],
                        card_data.get('count', 1),
                        card_data.get('card_type', ''),
                        card_data.get('isLegendary', False),
                        card_data.get('isStart', False),
                        card_data.get('ability', card_data.get('Ability', ''))
                    )
                    self.draw_pile.append(card_copy)
                    total_cards_loaded += 1
            
            print(f"Loaded {total_cards_loaded} total cards from {len(cards_data)} card types from {json_file_path}")
            
            # Shuffle the initial draw pile for randomized first draw
            random.shuffle(self.draw_pile)
            print("Initial draw pile shuffled for randomized starting hands")
            
        except FileNotFoundError:
            print(f"Cards file {json_file_path} not found")
        except json.JSONDecodeError:
            print(f"Invalid JSON format in {json_file_path}")
        except KeyError as e:
            print(f"Missing required field in card data: {e}")
    
    def load_starting_cards_from_json(self, json_file_path):
        """Load only starting cards (isStart: true) from JSON file and add to draw pile"""
        try:
            with open(json_file_path, 'r') as file:
                json_data = json.load(file)
                
            # Handle both JSON structures: direct array or wrapped in "cards" key
            if "cards" in json_data:
                cards_data = json_data["cards"]
            else:
                cards_data = json_data
                
            total_cards_loaded = 0
            for card_data in cards_data:
                # Only load cards marked as starting cards
                if not card_data.get('isStart', False):
                    continue
                    
                # Add multiple copies based on count
                count = card_data.get('count', 1)
                for _ in range(count):
                    # Create a new card instance for each copy
                    card_copy = Card(
                        card_data['card_index'],
                        card_data['name'],
                        card_data['power'],
                        card_data['cost'],
                        card_data['WP'],
                        card_data.get('count', 1),
                        card_data.get('card_type', ''),
                        card_data.get('isLegendary', False),
                        card_data.get('isStart', False),
                        card_data.get('ability', card_data.get('Ability', ''))
                    )
                    self.draw_pile.append(card_copy)
                    total_cards_loaded += 1
            
            print(f"Loaded {total_cards_loaded} starting cards from {json_file_path}")
            
            # Shuffle the initial draw pile for randomized first draw
            random.shuffle(self.draw_pile)
            print("Initial draw pile shuffled for randomized starting hands")
            
        except FileNotFoundError:
            print(f"Cards file {json_file_path} not found")
        except json.JSONDecodeError:
            print(f"Invalid JSON format in {json_file_path}")
        except KeyError as e:
            print(f"Missing required field in card data: {e}")
    
    def show_hand(self):
        """Display all cards in hand with indices"""
        if not self.hand:
            print("Hand is empty")
            return
        
        print(f"\n=== {self.name}'s Hand ===")
        for i, card in enumerate(self.hand):
            print(f"{i}: {card.getName()} (Power: {card.getPower()}, WP: {card.getWP()}, Cost: {card.getCost()})")
            print(f"   Ability: {card.getAbility()}")
    
    def get_status(self):
        """Get current player status"""
        return {
            'name': self.name,
            'hand_size': len(self.hand),
            'draw_pile_size': len(self.draw_pile),
            'discard_pile_size': len(self.discard_pile),
            'total_wp': self.calculate_total_wp(),
            'turn_power': self.turn_power
        }
    
    def __str__(self):
        """String representation of player"""
        status = self.get_status()
        return (f"Player: {status['name']} | "
                f"Hand: {status['hand_size']} | "
                f"Draw: {status['draw_pile_size']} | "
                f"Discard: {status['discard_pile_size']} | "
                f"Total WP: {status['total_wp']} | "
                f"Turn Power: {status['turn_power']}")


# Example usage and testing
if __name__ == "__main__":
    print("Player class loaded successfully!")
    print("Run 'python client.py' to play the game interactively.")
