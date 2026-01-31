import os
import sys
from objects.player import Player
from objects.card import Card

class GameClient:
    def __init__(self):
        self.player = None
        self.game_running = True
    
    def start_game(self):
        """Start the game and initialize player"""
        print("=== Welcome to Rogue Deck Builder! ===")
        player_name = input("Enter your player name: ").strip()
        if not player_name:
            player_name = "Player"
        
        self.player = Player(player_name)
        
        # Load cards from JSON
        cards_json_path = "cards.json"
        if os.path.exists(cards_json_path):
            self.player.load_cards_from_json(cards_json_path)
            print(f"\nLoaded cards for {self.player.name}!")
        else:
            print("Cards file not found! Creating some basic cards...")
            # Create basic cards if JSON not found
            basic_cards = [
                Card(1, "Fire Bolt", 3, 2, 1, "Deal 3 damage"),
                Card(2, "Lightning Strike", 5, 4, 2, "Deal 5 damage"),
                Card(3, "Healing Potion", 1, 1, 1, "Restore 3 health"),
                Card(4, "Magic Shield", 2, 2, 1, "Block 4 damage"),
                Card(5, "Power Crystal", 4, 3, 3, "Generate extra power")
            ]
            self.player.draw_pile = basic_cards
        
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
                self.show_all_cards()
            elif choice == "4":
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
        print("3. Show All Available Cards")
        print("4. Quit Game")
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
        
        # Play cards phase
        while self.player.hand:
            self.show_turn_menu()
            choice = input("\nWhat would you like to do? ").strip()
            
            if choice == "1":
                self.play_card_interactive()
            elif choice == "2":
                self.player.show_hand()
            elif choice == "3":
                self.show_player_status()
            elif choice == "4":
                if self.finish_turn_check():
                    break
            elif choice == "5":
                print("Ending turn without finishing...")
                break
            else:
                print("Invalid choice!")
        
        # If no cards left, automatically finish turn
        if not self.player.hand:
            print("\\nAll cards played! Finishing turn...")
            self.player.finish_turn()
            self.show_player_status()
            input("Press Enter to continue...")
    
    def show_turn_menu(self):
        """Show turn menu options"""
        print("\\n" + "-"*30)
        print("TURN OPTIONS")
        print("-"*30)
        print("1. Play a Card")
        print("2. Show Hand")
        print("3. Show Status")
        print("4. Finish Turn (only if hand empty)")
        print("5. End Turn")
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
        """Check if turn can be finished"""
        if self.player.hand:
            print(f"You still have {len(self.player.hand)} cards in hand!")
            print("You must play all cards before finishing the turn.")
            return False
        else:
            self.player.finish_turn()
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
