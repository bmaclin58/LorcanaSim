import os
import random
from typing import List, Optional, Tuple

# Attempt to import necessary classes
try:
    from player import Player
    from card import Card
    from deck import Deck
except ImportError:
    print("Warning: Could not import Player, Card, or Deck classes. GameState functionality/example will be limited.")
    exit()
class GameState:
    """Manages the state and flow of a Lorcana game between two players."""

    TARGET_LORE = 20 # Standard lore goal to win

    def __init__(self, player1: Player, player2: Player):
        """
        Initializes the game state.

        Args:
            player1: The first Player object.
            player2: The second Player object.
        """
        self.players: List[Player] = [player1, player2]
        self.turn: int = 1
        self.game_over: bool = False
        self.winner: Optional[Player] = None

        # Randomly determine the starting player
        self.active_player_index: int = random.choice([0, 1])
        self.active_player: Player = self.players[self.active_player_index]
        self.inactive_player: Player = self.players[1 - self.active_player_index]

        print(f"\n--- Game Start ---")
        print(f"{self.active_player.name} will go first.")

        # Initial state display (optional)
        # self.display_state()

        # Perform start-of-game actions for the first player
        self.active_player.turn_start_ready_phase()
        # Note: Official rules skip the first player's draw phase on turn 1.
        # We'll implement this rule in the game loop logic later,
        # for now, the player methods exist.

    def get_opponent(self, player: Player) -> Player:
        """Returns the opponent of the given player."""
        if player == self.players[0]:
            return self.players[1]
        elif player == self.players[1]:
            return self.players[0]
        else:
            raise ValueError("Provided player is not part of this game state.")

    def check_win_condition(self) -> bool:
        """
        Checks if the game has ended based on lore count or decking out.
        Updates self.game_over and self.winner if a condition is met.

        Returns:
            True if the game is over, False otherwise.
        """
        if self.game_over: # Don't re-evaluate if already decided
            return True

        # Check lore win condition (at start of turn, handled by game loop usually)
        # Here we check if *either* player is at or above the target lore
        for player in self.players:
            if player.lore >= self.TARGET_LORE:
                self.game_over = True
                self.winner = player
                print(f"\n--- Game Over ---")
                print(f"{self.winner.name} wins by reaching {player.lore} lore!")
                return True

        # Check loss condition (decking out)
        player1_lost = self.players[0].lost_game
        player2_lost = self.players[1].lost_game

        if player1_lost and player2_lost:
            # Rare case: Both players deck out simultaneously? Declare a draw.
            self.game_over = True
            self.winner = None # Indicate a draw
            print(f"\n--- Game Over ---")
            print("Draw! Both players lost simultaneously (decked out).")
            return True
        elif player1_lost:
            self.game_over = True
            self.winner = self.players[1]
            print(f"\n--- Game Over ---")
            print(f"{self.players[0].name} lost (decked out). {self.winner.name} wins!")
            return True
        elif player2_lost:
            self.game_over = True
            self.winner = self.players[0]
            print(f"\n--- Game Over ---")
            print(f"{self.players[1].name} lost (decked out). {self.winner.name} wins!")
            return True

        return False # No win/loss condition met yet

    def next_turn(self):
        """Advances the game to the next player's turn."""
        if self.game_over:
            print("Cannot advance turn, game is already over.")
            return

        # Switch active player
        self.active_player_index = 1 - self.active_player_index
        self.active_player = self.players[self.active_player_index]
        self.inactive_player = self.players[1 - self.active_player_index]

        # Increment turn counter only when player 1 starts their turn again
        if self.active_player_index == 0:
            self.turn += 1
            print(f"\n=== Starting Turn {self.turn} ===")

        # Perform start-of-turn actions for the new active player
        # Win condition check (lore) should happen *before* readying according to rules
        if self.check_win_condition():
             return # Stop if game ended due to lore check

        self.active_player.turn_start_ready_phase()
        self.active_player.turn_start_draw_phase()

        # Check if drawing caused the player to lose
        if self.check_win_condition():
             return # Stop if game ended due to decking out on draw

        # Optional: Display state at start of new turn
        # self.display_state()


    def display_state(self):
        """Prints the state of both players."""
        print(f"\n===== Game State - Turn {self.turn} =====")
        print(f"Active Player: {self.active_player.name}")
        for player in self.players:
            player.display_state()
        print("==============================")


# --- Example Usage ---
if __name__ == "__main__":
    # Requires data_fetcher, card, deck, and player modules
    try:
        from dataFetcher import fetch_lorcana_data
        from card import parse_card_data
        from deck import Deck, load_deck_identifiers_from_file
        # Player is imported at the top
    except ImportError:
        print("Could not import required modules for GameState example. Exiting.")
        exit()

    # 1. Load Card Data
    print("Loading card data...")
    raw_card_data = fetch_lorcana_data()
    if not raw_card_data: exit("Failed to load card data.")
    all_cards_by_id, all_cards_by_name, all_cards_by_lowercase_name = parse_card_data(raw_card_data)
    if not all_cards_by_name: exit("Card name map is empty.")
    combined_name_map = {**all_cards_by_name, **all_cards_by_lowercase_name}

    # 2. Load Decks for two players
    deck_file_1 = "Decks/LandGo.txt" # Player 1's deck
    deck_file_2 = "Decks/BouncingBosses.txt" # Player 2's deck

    print(f"\nLoading deck for Player 1: '{deck_file_1}'...")
    p1_names = load_deck_identifiers_from_file(deck_file_1)
    if not p1_names: exit(f"Failed to load deck file '{deck_file_1}'.")
    deck1 = Deck(p1_names, combined_name_map)
    if deck1.failed_lookups: print(f"Warning: Deck 1 created with missing cards.")
    if not deck1.is_valid(check_size=True, check_copies=True):
         print("Warning: Deck 1 is not valid.")

    print(f"\nLoading deck for Player 2: '{deck_file_2}'...")
    # Ensure example_deck.txt exists or use another file like LandGo.txt again
    if not os.path.exists(deck_file_2):
        print(f"Warning: Deck file '{deck_file_2}' not found. Using '{deck_file_1}' for Player 2 as well.")
        deck_file_2 = deck_file_1 # Fallback to player 1's deck

    p2_names = load_deck_identifiers_from_file(deck_file_2)
    if not p2_names: exit(f"Failed to load deck file '{deck_file_2}'.")
    deck2 = Deck(p2_names, combined_name_map)
    if deck2.failed_lookups: print(f"Warning: Deck 2 created with missing cards.")
    if not deck2.is_valid(check_size=True, check_copies=True):
         print("Warning: Deck 2 is not valid.")


    # 3. Create Player instances
    player1 = Player(name="Alyssa", deck=deck1, player_id=0)
    player2 = Player(name="Brian", deck=deck2, player_id=1)

    # 4. Create GameState instance
    game = GameState(player1, player2)

    # 5. Simulate a few turns
    print("\n--- Simulating Turns ---")

    # Turn 1 (Active player already determined and readied by __init__)
    print(f"\n--- {game.active_player.name}'s Main Phase (Turn 1) ---")
    # (Add simple AI actions here later: ink, play)
    # Example: Find and ink first inkable card
    active_p = game.active_player
    inkable_card = next((c for c in active_p.hand if c.inkable), None)
    if inkable_card and not active_p.has_inked_this_turn:
        active_p.ink_card(inkable_card)
    game.display_state()
    game.next_turn() # -> Player 2's turn 1 start

    # Turn 1 - Player 2
    print(f"\n--- {game.active_player.name}'s Main Phase (Turn 1) ---")
    active_p = game.active_player
    inkable_card = next((c for c in active_p.hand if c.inkable), None)
    if inkable_card and not active_p.has_inked_this_turn:
        active_p.ink_card(inkable_card)
    game.display_state()
    game.next_turn() # -> Player 1's turn 2 start (Turn counter increments)

    # Turn 2 - Player 1
    print(f"\n--- {game.active_player.name}'s Main Phase (Turn 2) ---")
    active_p = game.active_player
    # Try to play a 1-cost
    play_1 = next((c for c in active_p.hand if c.cost == 1), None)
    if play_1 and active_p.ready_ink >= 1:
        active_p.play_card(play_1)
    # Try to ink
    inkable_card = next((c for c in active_p.hand if c.inkable), None)
    if inkable_card and not active_p.has_inked_this_turn:
         active_p.ink_card(inkable_card)
    game.display_state()
    game.next_turn() # -> Player 2's turn 2 start

    print("\nSimulation Example Finished.")
