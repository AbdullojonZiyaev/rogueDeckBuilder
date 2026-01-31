import os
import sys
from objects.player import Player
from objects.card import Card
from objects.market import Market

class GameClient:
    def __init__(self):
        self.player = None
        self.market = None
        self.game_running = True
    
    def start_game(self):
        """Start the game and initialize player"""
        print("=== Welcome to Rogue Deck Builder! ===")
        player_name = input("Enter your player name: ").strip()
        if not player_name:
            player_name = "Player"
        
        self.player = Player(player_name)
        self.market = Market()
        
        # Load player starting cards from JSON
        cards_json_path = "cards.json"
        if os.path.exists(cards_json_path):
            self.player.load_starting_cards_from_json(cards_json_path)
            print(f"Loaded starting cards for {self.player.name}!")
        else:
            print("Player cards file not found! Creating some basic cards...")
            # Create basic cards if JSON not found
            basic_cards = [
                Card(1, "Fire Bolt", 3, 2, 1, 1, "Spell", False, True, "Deal 3 damage"),
                Card(2, "Lightning Strike", 5, 4, 2, 1, "Spell", False, True, "Deal 5 damage"),
                Card(3, "Healing Potion", 1, 1, 1, 1, "Item", False, True, "Restore 3 health"),
                Card(4, "Magic Shield", 2, 2, 1, 1, "Item", False, True, "Block 4 damage"),
                Card(5, "Power Crystal", 4, 3, 3, 1, "Treasure", False, True, "Generate extra power")
            ]
            self.player.draw_pile = basic_cards
        
        # Load market cards from the same JSON file
        if os.path.exists(cards_json_path):
            self.market.load_market_cards_from_main_json(cards_json_path)
            print("Market initialized from main cards file!")
        else:
            print("No cards file found! Market will be empty.")
        
        self.main_game_loop()
    
    def main_game_loop(self):
        """Main game loop"""
        while self.game_running:
            self.show_main_menu()
            choice = input("\nEnter your choice: ").strip()
            
            if choice == "1":
                self.new_turn()
            elif choice == "2":
                self.show_player_status()
            elif choice == "3":
                self.show_market()
            elif choice == "4":
                self.show_all_cards()
            elif choice == "5":
                self.game_running = False
                print("Thanks for playing!")
            else:
                print("Invalid choice! Please try again.")
    
    def show_main_menu(self):
        """Display main menu"""
        print("\n" + "="*40)
        print("MAIN MENU")
        print("="*40)
        print("1. Start New Turn")
        print("2. Show Player Status")
        print("3. Show Market")
        print("4. Show All Available Cards")
        print("5. Quit Game")
        print("="*40)
    
    def new_turn(self):
        """Start a new turn"""
        print(f"\n=== {self.player.name}'s Turn ===")
        
        # Draw hand
        hand_size = 5
        try:
            hand_size = int(input(f"How many cards to draw? (default 5): ") or "5")
        except ValueError:
            hand_size = 5
        
        self.player.draw_hand(hand_size)
        self.show_player_status()
        
        # Play cards phase and market purchasing
        game_phase_active = True
        while game_phase_active:
            self.show_turn_menu()
            choice = input("\nWhat would you like to do? ").strip()
            
            if choice == "1":
                self.play_card_interactive()
            elif choice == "2":
                self.player.show_hand()
            elif choice == "3":
                self.show_player_status()
            elif choice == "4":
                self.show_market()
            elif choice == "5":
                self.buy_from_market()
            elif choice == "6":
                if self.finish_turn_check():
                    game_phase_active = False
            elif choice == "7":
                print("Ending turn without finishing...")
                game_phase_active = False
            else:
                print("Invalid choice!")
    
    def show_turn_menu(self):
        """Show turn menu options"""
        print("\\n" + "-"*30)
        print("TURN OPTIONS")
        print("-"*30)
        print("1. Play a Card")
        print("2. Show Hand")
        print("3. Show Status")
        print("4. Show Market")
        print("5. Buy from Market")
        print("6. Finish Turn (only if hand empty)")
        print("7. End Turn")
        print("-"*30)
    
    def play_card_interactive(self):
        """Interactive card playing"""
        if not self.player.hand:
            print("No cards in hand!")
            return
        
        print("\\n=== Your Hand ===")
        self.player.show_hand()
        
        try:
            card_index = int(input("\\nEnter card index to play: "))
            if 0 <= card_index < len(self.player.hand):
                card_name = self.player.hand[card_index].getName()
                success = self.player.play_card(card_index)
                if success:
                    print(f"Successfully played {card_name}!")
                else:
                    print("Failed to play card!")
            else:
                print("Invalid card index!")
        except ValueError:
            print("Please enter a valid number!")
        except KeyboardInterrupt:
            print("\\nCancelled card play.")
    
    def finish_turn_check(self):
        """Finish the turn when player chooses to"""
        # Warn if cards still in hand
        if self.player.hand:
            print(f"\\nWarning: You still have {len(self.player.hand)} cards in hand!")
            confirm = input("Are you sure you want to finish the turn? (y/n): ").strip().lower()
            if confirm not in ['y', 'yes']:
                print("Turn continues...")
                return False
        
        self.player.finish_turn()
        
        # Replace purchased cards in market
        self.market.replace_purchased_cards()
        
        # End turn to reset power and other turn-specific states
        self.player.end_turn()
        
        # Check if game should end (market exhausted)
        if self.market.is_market_exhausted():
            self.end_game()
            return True
        
        self.show_player_status()
        print("Turn finished!")
        input("Press Enter to continue...")
        return True
    
    def show_player_status(self):
        """Display detailed player status"""
        print("\\n" + "="*50)
        print("PLAYER STATUS")
        print("="*50)
        print(self.player)
        status = self.player.get_status()
        print(f"Turn Power Generated: {status['turn_power']}")
        print(f"Total WP (from all cards): {status['total_wp']}")
        print("="*50)
    
    def show_all_cards(self):
        """Show all cards in all piles"""
        print("\\n=== ALL CARDS ===")
        
        print(f"\\n--- Draw Pile ({len(self.player.draw_pile)} cards) ---")
        if self.player.draw_pile:
            for i, card in enumerate(self.player.draw_pile):
                print(f"{i}: {card.getName()} (Power: {card.getPower()}, WP: {card.getWP()})")
        else:
            print("Empty")
        
        print(f"\\n--- Hand ({len(self.player.hand)} cards) ---")
        if self.player.hand:
            self.player.show_hand()
        else:
            print("Empty")
        
        print(f"\\n--- Discard Pile ({len(self.player.discard_pile)} cards) ---")
        if self.player.discard_pile:
            for i, card in enumerate(self.player.discard_pile):
                print(f"{i}: {card.getName()} (Power: {card.getPower()}, WP: {card.getWP()})")
        else:
            print("Empty")
        
        input("\\nPress Enter to continue...")
    
    def show_market(self):
        """Display market status and available cards"""
        print("\\n" + "="*50)
        print("MARKET STATUS")
        print("="*50)
        print(self.market)
        self.market.show_available_cards()
        
        if self.market.is_market_exhausted():
            print("\\n*** MARKET EXHAUSTED - GAME WILL END SOON ***")
    
    def buy_from_market(self):
        """Interactive market purchasing"""
        if self.player.turn_power <= 0:
            print("You have no power to buy cards!")
            return
        
        print(f"\\nYou have {self.player.turn_power} power to spend")
        self.market.show_available_cards()
        
        if not self.market.available_cards:
            print("No cards available for purchase!")
            return
        
        try:
            card_index = int(input("\\nEnter card index to buy (or -1 to cancel): "))
            if card_index == -1:
                print("Purchase cancelled")
                return
            
            if 0 <= card_index < len(self.market.available_cards):
                card_name = self.market.available_cards[card_index].getName()
                success = self.player.buy_card(self.market, card_index)
                if success:
                    print(f"Successfully purchased {card_name}!")
                else:
                    print("Failed to purchase card!")
            else:
                print("Invalid card index!")
        except ValueError:
            print("Please enter a valid number!")
        except KeyboardInterrupt:
            print("\\nPurchase cancelled.")
    
    def end_game(self):
        """End the game and show final scores"""
        print("\\n" + "="*60)
        print("GAME OVER - MARKET EXHAUSTED!")
        print("="*60)
        
        final_wp = self.player.calculate_total_wp()
        print(f"\\n{self.player.name}'s Final Score:")
        print(f"Total Win Points: {final_wp}")
        
        # Show final deck composition
        print(f"\\nFinal Deck Composition:")
        all_cards = self.player.hand + self.player.draw_pile + self.player.discard_pile
        print(f"Total cards in deck: {len(all_cards)}")
        
        # Count unique cards
        card_counts = {}
        for card in all_cards:
            card_name = card.getName()
            card_counts[card_name] = card_counts.get(card_name, 0) + 1
        
        print("\\nCards in your deck:")
        for card_name, count in sorted(card_counts.items()):
            print(f"  {card_name}: {count} copies")
        
        print(f"\\nCongratulations on your deck-building journey!")
        self.game_running = False
        input("\\nPress Enter to exit...")


def main():
    """Main function"""
    try:
        client = GameClient()
        client.start_game()
    except KeyboardInterrupt:
        print("\\n\\nGame interrupted. Goodbye!")
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Please check your setup and try again.")


if __name__ == "__main__":
    main()
