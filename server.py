import socket
import threading
import json
import random
from objects.player import Player
from objects.market import Market

class GameServer:
    def __init__(self, host='localhost', port=8888):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Game state
        self.players = []  # List of Player objects
        self.client_connections = []  # List of client socket connections
        self.player_names = []  # List of player names
        self.market = Market()
        self.current_player_index = 0
        self.game_started = False
        self.game_ended = False
        self.connected = True
        
        # Initialize market
        self.initialize_market()
    
    def initialize_market(self):
        """Initialize the market from cards.json"""
        try:
            self.market.load_market_cards_from_main_json("cards.json")
            print("Market initialized on server")
        except Exception as e:
            print(f"Failed to initialize market: {e}")
    
    def start_server(self):
        """Start the server and listen for connections"""
        try:
            self.socket.bind((self.host, self.port))
            self.socket.listen(2)  # Maximum 2 players
            print(f"Game server started on {self.host}:{self.port}")
            print("Waiting for players to connect...")
            
            while len(self.client_connections) < 2:
                client_socket, address = self.socket.accept()
                print(f"Player connected from {address}")
                
                # Handle client connection in a separate thread
                client_thread = threading.Thread(
                    target=self.handle_client, 
                    args=(client_socket, len(self.client_connections))
                )
                client_thread.daemon = True
                client_thread.start()
                
                self.client_connections.append(client_socket)
                
                print(f"{len(self.client_connections)}/2 players connected")
            
            # Keep server alive while game is running
            print("Game is running! Press Ctrl+C to stop server.")
            try:
                while not self.game_ended and len(self.client_connections) > 0:
                    import time
                    time.sleep(1)  # Check every second
            except KeyboardInterrupt:
                print("\nServer interrupted by user")
            
            print("Game finished or all players disconnected")
                
        except Exception as e:
            print(f"Server error: {e}")
        finally:
            print("Server shutting down...")
            for client in self.client_connections:
                try:
                    client.close()
                except:
                    pass
            self.socket.close()
    
    def handle_client(self, client_socket, player_index):
        """Handle communication with a specific client"""
        print(f"Starting handler for player {player_index}")
        try:
            while not self.game_ended:
                try:
                    client_socket.settimeout(1.0)  # Set timeout for recv
                    data = client_socket.recv(4096).decode('utf-8')
                    if not data:
                        print(f"Player {player_index} disconnected (no data)")
                        break
                    
                    try:
                        message = json.loads(data)
                        self.process_client_message(client_socket, player_index, message)
                    except json.JSONDecodeError:
                        print(f"Invalid JSON from player {player_index}: {data}")
                        
                except socket.timeout:
                    # Timeout is normal, just continue
                    continue
                except ConnectionResetError:
                    print(f"Player {player_index} disconnected (connection reset)")
                    break
                except Exception as e:
                    print(f"Network error with player {player_index}: {e}")
                    break
                    
        except Exception as e:
            print(f"Error handling client {player_index}: {e}")
        finally:
            print(f"Cleaning up connection for player {player_index}")
            if client_socket in self.client_connections:
                self.client_connections.remove(client_socket)
            try:
                client_socket.close()
            except:
                pass
    
    def process_client_message(self, client_socket, player_index, message):
        """Process messages from clients"""
        msg_type = message.get('type')
        
        if msg_type == 'join':
            self.handle_player_join(client_socket, player_index, message.get('name', f'Player{player_index+1}'))
        
        elif msg_type == 'play_card' and self.is_current_player(player_index):
            self.handle_play_card(player_index, message.get('card_index'))
        
        elif msg_type == 'buy_card' and self.is_current_player(player_index):
            self.handle_buy_card(player_index, message.get('card_index'))
        
        elif msg_type == 'finish_turn' and self.is_current_player(player_index):
            self.handle_finish_turn(player_index)
        
        elif msg_type == 'draw_hand' and self.is_current_player(player_index):
            self.handle_draw_hand(player_index, message.get('hand_size', 5))
        
        elif msg_type == 'get_status':
            self.send_game_status(client_socket, player_index)
    
    def handle_player_join(self, client_socket, player_index, player_name):
        """Handle player joining the game"""
        if len(self.players) <= player_index:
            # Create new player
            player = Player(player_name)
            try:
                player.load_starting_cards_from_json("cards.json")
                print(f"Loaded starting cards for {player_name}")
            except Exception as e:
                print(f"Failed to load cards for {player_name}: {e}")
            
            self.players.append(player)
            self.player_names.append(player_name)
            
            # Send confirmation to client
            response = {
                'type': 'join_success',
                'player_index': player_index,
                'player_name': player_name
            }
            self.send_to_client(client_socket, response)
            
            print(f"Player {player_name} joined as player {player_index}")
            print(f"{len(self.players)}/2 players joined")
            
            # Start game when both players have joined
            if len(self.players) == 2:
                print("Both players joined! Starting game...")
                self.start_game()
    
    def start_game(self):
        """Start the game with both players"""
        if len(self.players) == 2:
            # Randomly select first player
            self.current_player_index = random.randint(0, 1)
            self.game_started = True
            
            print(f"Game starting with players: {[p.name for p in self.players]}")
            
            # Notify all players that game started
            game_start_msg = {
                'type': 'game_start',
                'first_player': self.current_player_index,
                'first_player_name': self.players[self.current_player_index].name,
                'players': [player.name for player in self.players]
            }
            self.broadcast_to_all(game_start_msg)
            
            print(f"Game started! {self.players[self.current_player_index].name} goes first")
            
            # Send initial game state
            self.send_game_state_to_all()
        else:
            print(f"Cannot start game - only {len(self.players)} players joined")
    
    def handle_play_card(self, player_index, card_index):
        """Handle player playing a card"""
        player = self.players[player_index]
        
        if 0 <= card_index < len(player.hand):
            success = player.play_card(card_index)
            if success:
                # Broadcast card played to all players
                msg = {
                    'type': 'card_played',
                    'player_index': player_index,
                    'player_name': player.name,
                    'success': True
                }
                self.broadcast_to_all(msg)
                self.send_game_state_to_all()
            else:
                self.send_error(self.client_connections[player_index], "Failed to play card")
        else:
            self.send_error(self.client_connections[player_index], "Invalid card index")
    
    def handle_buy_card(self, player_index, card_index):
        """Handle player buying a card from market"""
        player = self.players[player_index]
        
        if 0 <= card_index < len(self.market.available_cards):
            success = player.buy_card(self.market, card_index)
            if success:
                msg = {
                    'type': 'card_bought',
                    'player_index': player_index,
                    'player_name': player.name,
                    'card_name': self.market.available_cards[card_index].getName() if card_index < len(self.market.available_cards) else "Unknown",
                    'success': True
                }
                self.broadcast_to_all(msg)
                self.send_game_state_to_all()
            else:
                self.send_error(self.client_connections[player_index], "Failed to buy card")
        else:
            self.send_error(self.client_connections[player_index], "Invalid card index")
    
    def handle_finish_turn(self, player_index):
        """Handle player finishing their turn"""
        player = self.players[player_index]
        
        # Finish current player's turn
        player.finish_turn()
        
        # Replace purchased cards in market
        self.market.replace_purchased_cards()
        
        # Reset player's turn power
        player.end_turn()
        
        # Check if game should end
        if self.market.is_market_exhausted():
            self.end_game()
            return
        
        # Switch to next player
        self.current_player_index = (self.current_player_index + 1) % 2
        
        # Broadcast turn change
        msg = {
            'type': 'turn_finished',
            'finished_player': player_index,
            'next_player': self.current_player_index,
            'next_player_name': self.players[self.current_player_index].name
        }
        self.broadcast_to_all(msg)
        self.send_game_state_to_all()
    
    def handle_draw_hand(self, player_index, hand_size):
        """Handle player drawing cards"""
        player = self.players[player_index]
        player.draw_hand(hand_size)
        
        msg = {
            'type': 'cards_drawn',
            'player_index': player_index,
            'hand_size': len(player.hand)
        }
        self.broadcast_to_all(msg)
        self.send_game_state_to_all()
    
    def end_game(self):
        """End the game and send final scores"""
        self.game_ended = True
        
        # Calculate final scores
        scores = []
        for i, player in enumerate(self.players):
            final_wp = player.calculate_total_wp()
            scores.append({
                'player_index': i,
                'player_name': player.name,
                'final_wp': final_wp
            })
        
        # Determine winner
        winner = max(scores, key=lambda x: x['final_wp'])
        
        end_game_msg = {
            'type': 'game_end',
            'scores': scores,
            'winner': winner
        }
        self.broadcast_to_all(end_game_msg)
        print(f"Game ended! Winner: {winner['player_name']} with {winner['final_wp']} WP")
        
        # Give clients time to process the end game message
        threading.Timer(2.0, self.shutdown_server).start()
    
    def send_game_state_to_all(self):
        """Send current game state to all players"""
        for i, client in enumerate(self.client_connections):
            self.send_game_status(client, i)
    
    def send_game_status(self, client_socket, player_index):
        """Send game status to a specific client"""
        if player_index < len(self.players):
            player = self.players[player_index]
            other_player = self.players[1 - player_index] if len(self.players) > 1 else None
            
            # Prepare player's hand (only send to the player themselves)
            hand_data = []
            for card in player.hand:
                hand_data.append({
                    'name': card.getName(),
                    'power': card.getPower(),
                    'cost': card.getCost(),
                    'wp': card.getWP(),
                    'ability': card.getAbility()
                })
            
            # Prepare market data
            market_data = []
            for card in self.market.available_cards:
                market_data.append({
                    'name': card.getName(),
                    'power': card.getPower(),
                    'cost': card.getCost(),
                    'wp': card.getWP(),
                    'ability': card.getAbility()
                })
            
            game_state = {
                'type': 'game_state',
                'current_player': self.current_player_index,
                'is_your_turn': player_index == self.current_player_index,
                'player': {
                    'name': player.name,
                    'hand': hand_data,
                    'hand_size': len(player.hand),
                    'draw_pile_size': len(player.draw_pile),
                    'discard_pile_size': len(player.discard_pile),
                    'turn_power': player.turn_power,
                    'total_wp': player.calculate_total_wp()
                },
                'opponent': {
                    'name': other_player.name if other_player else "Waiting...",
                    'hand_size': len(other_player.hand) if other_player else 0,
                    'draw_pile_size': len(other_player.draw_pile) if other_player else 0,
                    'discard_pile_size': len(other_player.discard_pile) if other_player else 0,
                    'turn_power': other_player.turn_power if other_player else 0,
                    'total_wp': other_player.calculate_total_wp() if other_player else 0
                },
                'market': {
                    'available_cards': market_data,
                    'market_draw_pile_size': len(self.market.market_draw_pile)
                }
            }
            self.send_to_client(client_socket, game_state)
    
    def is_current_player(self, player_index):
        """Check if it's the current player's turn"""
        return player_index == self.current_player_index and self.game_started and not self.game_ended
    
    def send_to_client(self, client_socket, message):
        """Send a message to a specific client"""
        try:
            client_socket.send(json.dumps(message).encode('utf-8'))
        except Exception as e:
            print(f"Failed to send message to client: {e}")
    
    def broadcast_to_all(self, message):
        """Send a message to all connected clients"""
        for client in self.client_connections:
            self.send_to_client(client, message)
    
    def send_error(self, client_socket, error_message):
        """Send an error message to a client"""
        error_msg = {
            'type': 'error',
            'message': error_message
        }
        self.send_to_client(client_socket, error_msg)
    
    def shutdown_server(self):
        """Shutdown the server gracefully"""
        print("Shutting down server...")
        self.connected = False
        self.game_ended = True

def main():
    """Main server function"""
    import sys
    
    # Default to bind to all interfaces for network access
    host = '0.0.0.0'  # Allows connections from any IP on the network
    port = 8888
    
    # Allow command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h', '--help']:
            print("Usage: python3 server.py [host] [port]")
            print("  host: IP address to bind to (default: 0.0.0.0 for all interfaces)")
            print("  port: Port to listen on (default: 8888)")
            print("\nExamples:")
            print("  python3 server.py                    # Bind to all interfaces on port 8888")
            print("  python3 server.py 10.1.2.100        # Bind to ZeroTier IP")
            print("  python3 server.py 192.168.1.100     # Bind to local WiFi IP")
            print("  python3 server.py 0.0.0.0 9999      # Bind to all interfaces on port 9999")
            print("\nTip: Use 'python3 network_info.py' to see your available IPs")
            return
        
        host = sys.argv[1]
        if len(sys.argv) > 2:
            try:
                port = int(sys.argv[2])
            except ValueError:
                print("Invalid port number, using default 8888")
                port = 8888
    
    print("🎮 === Rogue Deck Builder Server ===")
    print(f"Server will bind to: {host}:{port}")
    
    if host == '0.0.0.0':
        print("📡 Server accessible from any device on connected networks")
        # Try to show available network interfaces
        try:
            import subprocess
            result = subprocess.run(['hostname', '-I'], capture_output=True, text=True)
            if result.returncode == 0:
                local_ips = result.stdout.strip().split()
                if local_ips:
                    print("🔸 Available IP addresses:")
                    for ip in local_ips:
                        if not ip.startswith('127.'):
                            # Try to identify ZeroTier IPs
                            if ip.startswith('10.') or (ip.startswith('172.') and 16 <= int(ip.split('.')[1]) <= 31):
                                print(f"   🚀 {ip} (likely ZeroTier/VPN)")
                            else:
                                print(f"   📶 {ip} (local network)")
                    print(f"ℹ️  Run 'python3 network_info.py' for detailed network information")
        except:
            print("ℹ️  Run 'python3 network_info.py' to see your available networks")
    else:
        print(f"🎯 Server accessible at: {host}:{port}")
        if host.startswith('10.') or (host.startswith('172.') and 16 <= int(host.split('.')[1]) <= 31):
            print("🚀 Using ZeroTier/VPN network - great for bypassing WiFi restrictions!")
    
    print("\n🚀 Starting server...")
    print("   Waiting for 2 players to connect...")
    print("   Press Ctrl+C to stop server")
    print()
    
    server = GameServer(host, port)
    try:
        server.start_server()
    except KeyboardInterrupt:
        print("\n👋 Server shutting down...")
    except Exception as e:
        print(f"❌ Server error: {e}")

if __name__ == "__main__":
    main()
