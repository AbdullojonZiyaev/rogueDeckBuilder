import socket
import json
import threading
import sys

class MultiplayerClient:
    def __init__(self, host='localhost', port=8888):
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
        self.player_index = -1
        self.player_name = ""
        self.game_state = {}
        self.is_my_turn = False
        
    def connect_to_server(self):
        """Connect to the game server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.connected = True
            print(f"Connected to server at {self.host}:{self.port}")
            
            # Start listening for server messages
            listener_thread = threading.Thread(target=self.listen_for_messages)
            listener_thread.daemon = True
            listener_thread.start()
            
            return True
        except Exception as e:
            print(f"Failed to connect to server: {e}")
            return False
    
    def listen_for_messages(self):
        """Listen for messages from the server"""
        while self.connected:
            try:
                data = self.socket.recv(4096).decode('utf-8')
                if not data:
                    break
                
                message = json.loads(data)
                self.handle_server_message(message)
                
            except Exception as e:
                if self.connected:
                    print(f"Error receiving message: {e}")
                break
    
    def handle_server_message(self, message):
        """Handle messages from the server"""
        msg_type = message.get('type')
        
        if msg_type == 'join_success':
            self.player_index = message.get('player_index')
            self.player_name = message.get('player_name')
            print(f"Successfully joined as {self.player_name} (Player {self.player_index + 1})")
        
        elif msg_type == 'game_start':
            first_player = message.get('first_player')
            first_player_name = message.get('first_player_name')
            players = message.get('players', [])
            print(f"\\n=== GAME STARTED! ===")
            print(f"Players: {', '.join(players)}")
            print(f"{first_player_name} goes first!")
        
        elif msg_type == 'game_state':
            self.game_state = message
            self.is_my_turn = message.get('is_your_turn', False)
            self.display_game_state()
        
        elif msg_type == 'card_played':
            player_name = message.get('player_name')
            if message.get('player_index') != self.player_index:
                print(f"{player_name} played a card!")
        
        elif msg_type == 'card_bought':
            player_name = message.get('player_name')
            card_name = message.get('card_name')
            if message.get('player_index') != self.player_index:
                print(f"{player_name} bought {card_name}!")
        
        elif msg_type == 'turn_finished':
            finished_player = message.get('finished_player')
            next_player_name = message.get('next_player_name')
            if finished_player == self.player_index:
                print("Your turn has ended!")
            else:
                print(f"It's now {next_player_name}'s turn!")
        
        elif msg_type == 'cards_drawn':
            player_index = message.get('player_index')
            hand_size = message.get('hand_size')
            if player_index != self.player_index:
                opponent_name = self.game_state.get('opponent', {}).get('name', 'Opponent')
                print(f"{opponent_name} drew cards (hand: {hand_size})")
        
        elif msg_type == 'game_end':
            self.handle_game_end(message)
        
        elif msg_type == 'error':
            print(f"Error: {message.get('message')}")
    
    def display_game_state(self):
        """Display current game state"""
        if not self.game_state:
            return
        
        player_data = self.game_state.get('player', {})
        opponent_data = self.game_state.get('opponent', {})
        market_data = self.game_state.get('market', {})
        
        print(f"\\n{'='*60}")
        print("GAME STATUS")
        print("="*60)
        
        # Current turn indicator
        current_player = self.game_state.get('current_player')
        if self.is_my_turn:
            print(">>> IT'S YOUR TURN! <<<")
        else:
            print(f"Waiting for {opponent_data.get('name', 'opponent')}'s turn...")
        
        # Player status
        print(f"\\nYour Status ({player_data.get('name', 'You')}):")
        print(f"  Hand: {player_data.get('hand_size', 0)} cards")
        print(f"  Draw Pile: {player_data.get('draw_pile_size', 0)} cards")
        print(f"  Discard Pile: {player_data.get('discard_pile_size', 0)} cards")
        print(f"  Turn Power: {player_data.get('turn_power', 0)}")
        print(f"  Total WP: {player_data.get('total_wp', 0)}")
        
        # Opponent status
        print(f"\\nOpponent Status ({opponent_data.get('name', 'Waiting...')}):")
        print(f"  Hand: {opponent_data.get('hand_size', 0)} cards")
        print(f"  Draw Pile: {opponent_data.get('draw_pile_size', 0)} cards")
        print(f"  Discard Pile: {opponent_data.get('discard_pile_size', 0)} cards")
        print(f"  Turn Power: {opponent_data.get('turn_power', 0)}")
        print(f"  Total WP: {opponent_data.get('total_wp', 0)}")
        
        # Market status
        print(f"\\nMarket:")
        print(f"  Available Cards: {len(market_data.get('available_cards', []))}")
        print(f"  Market Draw Pile: {market_data.get('market_draw_pile_size', 0)} cards")
        
        print("="*60)
    
    def show_hand(self):
        """Display player's hand"""
        if not self.game_state:
            print("No game state available")
            return
        
        hand = self.game_state.get('player', {}).get('hand', [])
        if not hand:
            print("Your hand is empty!")
            return
        
        print("\\n=== YOUR HAND ===")
        for i, card in enumerate(hand):
            print(f"{i}: {card['name']} (Power: {card['power']}, WP: {card['wp']}, Cost: {card['cost']})")
            print(f"   Ability: {card['ability']}")
    
    def show_market(self):
        """Display available market cards"""
        if not self.game_state:
            print("No game state available")
            return
        
        market_cards = self.game_state.get('market', {}).get('available_cards', [])
        if not market_cards:
            print("No cards available in market!")
            return
        
        print("\\n=== MARKET ===")
        for i, card in enumerate(market_cards):
            print(f"{i}: {card['name']} - Cost: {card['cost']} | Power: {card['power']} | WP: {card['wp']}")
            print(f"   Ability: {card['ability']}")
        
        market_pile_size = self.game_state.get('market', {}).get('market_draw_pile_size', 0)
        print(f"Market draw pile remaining: {market_pile_size} cards")
    
    def send_to_server(self, message):
        """Send a message to the server"""
        if not self.connected:
            print("Not connected to server!")
            return False
        
        try:
            self.socket.send(json.dumps(message).encode('utf-8'))
            return True
        except Exception as e:
            print(f"Failed to send message: {e}")
            return False
    
    def join_game(self, player_name):
        """Join the game with a player name"""
        message = {
            'type': 'join',
            'name': player_name
        }
        return self.send_to_server(message)
    
    def play_card(self, card_index):
        """Play a card from hand"""
        if not self.is_my_turn:
            print("It's not your turn!")
            return
        
        message = {
            'type': 'play_card',
            'card_index': card_index
        }
        self.send_to_server(message)
    
    def buy_card(self, card_index):
        """Buy a card from market"""
        if not self.is_my_turn:
            print("It's not your turn!")
            return
        
        message = {
            'type': 'buy_card',
            'card_index': card_index
        }
        self.send_to_server(message)
    
    def draw_hand(self, hand_size=5):
        """Draw cards for hand"""
        if not self.is_my_turn:
            print("It's not your turn!")
            return
        
        message = {
            'type': 'draw_hand',
            'hand_size': hand_size
        }
        self.send_to_server(message)
    
    def finish_turn(self):
        """Finish current turn"""
        if not self.is_my_turn:
            print("It's not your turn!")
            return
        
        message = {
            'type': 'finish_turn'
        }
        self.send_to_server(message)
    
    def request_status(self):
        """Request current game status"""
        message = {
            'type': 'get_status'
        }
        self.send_to_server(message)
    
    def handle_game_end(self, message):
        """Handle game end"""
        print("\\n" + "="*60)
        print("GAME OVER!")
        print("="*60)
        
        scores = message.get('scores', [])
        winner = message.get('winner', {})
        
        print("\\nFinal Scores:")
        for score in scores:
            player_name = score.get('player_name')
            final_wp = score.get('final_wp')
            print(f"  {player_name}: {final_wp} WP")
        
        print(f"\\nWinner: {winner.get('player_name')} with {winner.get('final_wp')} WP!")
        print("\\nThank you for playing!")
        
        # Close connection
        self.disconnect()
    
    def disconnect(self):
        """Disconnect from server"""
        self.connected = False
        if self.socket:
            self.socket.close()
    
    def main_game_loop(self):
        """Main client game loop"""
        print("\\n=== Multiplayer Rogue Deck Builder ===")
        print("Commands:")
        print("  h - Show hand")
        print("  m - Show market")
        print("  s - Show status")
        print("  p <index> - Play card at index")
        print("  b <index> - Buy card at index from market")
        print("  d [size] - Draw hand (default 5 cards)")
        print("  f - Finish turn")
        print("  q - Quit")
        print("\\nWaiting for another player to join...")
        
        while self.connected:
            try:
                command = input("\\n> ").strip().lower()
                
                if not command:
                    continue
                
                parts = command.split()
                cmd = parts[0]
                
                if cmd == 'h':
                    self.show_hand()
                
                elif cmd == 'm':
                    self.show_market()
                
                elif cmd == 's':
                    self.request_status()
                
                elif cmd == 'p' and len(parts) > 1:
                    try:
                        card_index = int(parts[1])
                        self.play_card(card_index)
                    except ValueError:
                        print("Invalid card index")
                
                elif cmd == 'b' and len(parts) > 1:
                    try:
                        card_index = int(parts[1])
                        self.buy_card(card_index)
                    except ValueError:
                        print("Invalid card index")
                
                elif cmd == 'd':
                    hand_size = 5
                    if len(parts) > 1:
                        try:
                            hand_size = int(parts[1])
                        except ValueError:
                            hand_size = 5
                    self.draw_hand(hand_size)
                
                elif cmd == 'f':
                    self.finish_turn()
                
                elif cmd == 'q':
                    print("Disconnecting...")
                    break
                
                else:
                    print("Unknown command. Type 'h' for hand, 'm' for market, 's' for status, 'q' to quit.")
                    
            except KeyboardInterrupt:
                print("\\nDisconnecting...")
                break
            except Exception as e:
                print(f"Error: {e}")
        
        self.disconnect()

def main():
    """Main client function"""
    print("=== Multiplayer Connection Setup ===")
    
    # Get connection details
    print("1. Connect to localhost (same computer)")
    print("2. Connect to remote server (enter IP)")
    
    while True:
        choice = input("Choose connection type (1-2): ").strip()
        if choice == '1':
            host = 'localhost'
            port = 8888
            break
        elif choice == '2':
            host = input("Enter server IP address: ").strip()
            if not host:
                print("Invalid IP address!")
                continue
            
            # Ask for port (optional)
            port_input = input("Enter port (default 8888): ").strip()
            if port_input:
                try:
                    port = int(port_input)
                except ValueError:
                    print("Invalid port, using default 8888")
                    port = 8888
            else:
                port = 8888
            break
        else:
            print("Invalid choice! Please select 1 or 2.")
    
    # Get player name
    player_name = input("Enter your player name: ").strip()
    if not player_name:
        player_name = "Anonymous"
    
    print(f"Connecting to {host}:{port} as {player_name}...")
    client = MultiplayerClient(host, port)
    
    if not client.connect_to_server():
        print(f"Failed to connect to server at {host}:{port}")
        print("Make sure:")
        print("1. The server is running")
        print("2. The IP address and port are correct") 
        print("3. No firewall is blocking the connection")
        return
    
    # Join the game immediately after connecting
    if client.join_game(player_name):
        print("Successfully connected! Waiting for game to start...")
        client.main_game_loop()
    else:
        print("Failed to join game")
    
    client.disconnect()

if __name__ == "__main__":
    main()