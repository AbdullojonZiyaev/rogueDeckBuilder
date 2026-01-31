#!/usr/bin/env python3

import sys
import subprocess

def main():
    print("=== Rogue Deck Builder Launcher ===")
    print("1. Single Player Game")
    print("2. Start Multiplayer Server")
    print("3. Join Multiplayer Game")
    print("4. Quit")
    
    while True:
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == '1':
            print("Starting single player game...")
            subprocess.run([sys.executable, "singleplayer_client.py"])
            break
            
        elif choice == '2':
            print("Starting multiplayer server...")
            print("Players can connect using option 3")
            subprocess.run([sys.executable, "server.py"])
            break
            
        elif choice == '3':
            print("Connecting to multiplayer game...")
            subprocess.run([sys.executable, "multiplayer_client.py"])
            break
            
        elif choice == '4':
            print("Goodbye!")
            break
            
        else:
            print("Invalid choice. Please select 1-4.")

if __name__ == "__main__":
    main()