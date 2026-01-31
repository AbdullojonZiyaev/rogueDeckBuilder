import json
import random
from objects.card import Card

class Market:
    def __init__(self):
        """Initialize market with empty card pools"""
        self.market_draw_pile = []  # Cards available to be put in market
        self.available_cards = []   # 5 cards currently available for purchase
        self.purchased_indices = [] # Track which slots were purchased this turn
        
    def load_market_cards_from_json(self, json_file_path):
        """Load market cards from JSON file"""
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
                # Add multiple copies based on count
                count = card_data.get('count', 1)
                for _ in range(count):
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
                    self.market_draw_pile.append(card_copy)
                    total_cards_loaded += 1
            
            # Shuffle market draw pile
            random.shuffle(self.market_draw_pile)
            print(f"Loaded {total_cards_loaded} total cards from {len(cards_data)} card types into market")
            
            # Fill initial available cards (5 cards)
            self.refill_market()
            
        except FileNotFoundError:
            print(f"Market cards file {json_file_path} not found")
        except json.JSONDecodeError:
            print(f"Invalid JSON format in {json_file_path}")
        except KeyError as e:
            print(f"Missing required field in market card data: {e}")
    
    def load_market_cards_from_main_json(self, json_file_path):
        """Load only market cards (isStart: false) from main JSON file"""
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
                # Only load cards NOT marked as starting cards
                if card_data.get('isStart', False):
                    continue
                    
                # Add multiple copies based on count
                count = card_data.get('count', 1)
                for _ in range(count):
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
                    self.market_draw_pile.append(card_copy)
                    total_cards_loaded += 1
            
            # Shuffle market draw pile
            random.shuffle(self.market_draw_pile)
            print(f"Loaded {total_cards_loaded} market cards from {json_file_path}")
            
            # Fill initial available cards (5 cards)
            self.refill_market()
            
        except FileNotFoundError:
            print(f"Cards file {json_file_path} not found")
        except json.JSONDecodeError:
            print(f"Invalid JSON format in {json_file_path}")
        except KeyError as e:
            print(f"Missing required field in card data: {e}")
    
    def refill_market(self):
        """Fill available cards to 5 cards from market draw pile"""
        while len(self.available_cards) < 5 and self.market_draw_pile:
            new_card = self.market_draw_pile.pop(0)
            self.available_cards.append(new_card)
        
        if len(self.available_cards) < 5:
            print(f"Warning: Only {len(self.available_cards)} cards available in market (market draw pile exhausted)")
    
    def show_available_cards(self):
        """Display all available cards for purchase"""
        if not self.available_cards:
            print("No cards available in market!")
            return
            
        print(f"\n=== MARKET - Available Cards ===")
        for i, card in enumerate(self.available_cards):
            print(f"{i}: {card.getName()} - Cost: {card.getCost()} | Power: {card.getPower()} | WP: {card.getWP()}")
            print(f"   Ability: {card.getAbility()}")
        print(f"Market draw pile remaining: {len(self.market_draw_pile)} cards")
        print("="*35)
    
    def buy_card(self, card_index, player_power):
        """Buy a card from market if player has enough power"""
        if card_index < 0 or card_index >= len(self.available_cards):
            print("Invalid card index!")
            return None, 0
        
        card = self.available_cards[card_index]
        cost = card.getCost()
        
        if player_power < cost:
            print(f"Not enough power! Need {cost}, have {player_power}")
            return None, 0
        
        # Remove card from available cards and mark slot for replacement
        purchased_card = self.available_cards.pop(card_index)
        self.purchased_indices.append(card_index)
        
        print(f"Purchased {purchased_card.getName()} for {cost} power!")
        return purchased_card, cost
    
    def replace_purchased_cards(self):
        """Replace purchased card slots with new cards from market draw pile"""
        cards_replaced = 0
        
        # Sort indices in reverse order to maintain correct positions when inserting
        for index in sorted(self.purchased_indices, reverse=True):
            if self.market_draw_pile and index <= len(self.available_cards):
                new_card = self.market_draw_pile.pop(0)
                self.available_cards.insert(index, new_card)
                cards_replaced += 1
        
        # If we couldn't replace all cards, just refill from the end
        while len(self.available_cards) < 5 and self.market_draw_pile:
            new_card = self.market_draw_pile.pop(0)
            self.available_cards.append(new_card)
            cards_replaced += 1
        
        # Clear purchased indices for next turn
        self.purchased_indices.clear()
        
        if cards_replaced > 0:
            print(f"Market restocked with {cards_replaced} new cards")
        
        return cards_replaced
    
    def is_market_exhausted(self):
        """Check if market draw pile is empty (game end condition)"""
        return len(self.market_draw_pile) == 0
    
    def get_market_status(self):
        """Get current market status"""
        return {
            'available_cards_count': len(self.available_cards),
            'market_draw_pile_count': len(self.market_draw_pile),
            'purchased_this_turn': len(self.purchased_indices),
            'is_exhausted': self.is_market_exhausted()
        }
    
    def __str__(self):
        """String representation of market"""
        status = self.get_market_status()
        return (f"Market: {status['available_cards_count']} available | "
                f"Draw pile: {status['market_draw_pile_count']} | "
                f"Purchased: {status['purchased_this_turn']}")


# Example usage and testing
if __name__ == "__main__":
    print("Market class loaded successfully!")
    print("Market will be integrated with the main client.")
