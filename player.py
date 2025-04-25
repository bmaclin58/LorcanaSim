from typing import List, Optional, Dict, Any
import random # mulligan, but not strictly needed yet

# Attempt to import necessary classes, handle potential ImportError
try:
    from card import Card
    from deck import Deck
except ImportError:
    print("Warning: Could not import Card or Deck classes.")
    exit()

# Define a type alias for cards in play for clarity
# Each item will be a dictionary holding the card and its state
PlayableCard = Dict[str, Any] # Keys: 'card': Card, 'exerted': bool, 'damage': int, etc.

class Player:
    """Represents a player in the Lorcana game."""

    def __init__(self, name: str, deck: Deck, player_id: int):
        """
        Initializes a Player.

        Args:
            name (str): The player's name (e.g., "Player 1").
            deck (Deck): The Deck object assigned to this player.
            player_id (int): A unique ID for the player (e.g., 0 or 1).
        """
        self.name: str = name
        self.player_id: int = player_id
        self.deck: Deck = deck
        self.hand: List[Card] = []
        self.inkwell: List[Card] = [] # Cards used as ink
        self.discard_pile: List[Card] = []
        # Cards currently on the board (characters, items, locations)
        # Each entry is a PlayableCard dictionary: {'card': Card, 'exerted': False, 'damage': 0}
        self.play_area: List[PlayableCard] = []
        self.lore: int = 0

        # Ink state
        self.total_ink: int = 0 # Total number of cards in inkwell
        self.ready_ink: int = 0 # Ink available to spend this turn
        self.exerted_ink: int = 0 # Ink already spent this turn

        # Game state flags
        self.has_drawn_this_turn: bool = False
        self.has_inked_this_turn: bool = False
        self.lost_game: bool = False # Flag if player lost (e.g., deck empty)

        # --- Initial Setup ---
        self._initial_draw()

    def _initial_draw(self, num_cards: int = 7):
        """Draws the initial hand."""
        print(f"{self.name}: Drawing initial hand of {num_cards} cards.")
        for _ in range(num_cards):
            self.draw_card()
        # Mulligan logic could be added here later

    def draw_card(self) -> Optional[Card]:
        """
        Draws a card from the deck and adds it to the hand.
        Sets the lost_game flag if the deck is empty.

        Returns:
            The Card drawn, or None if the deck was empty.
        """
        drawn_card = self.deck.draw()
        if drawn_card:
            self.hand.append(drawn_card)
            # print(f"{self.name}: Drew {drawn_card.name}") # Optional: for debugging
            return drawn_card
        else:
            if not self.lost_game: # Only print/set loss once
                 print(f"{self.name}: Deck is empty! Cannot draw.")
                 self.lost_game = True
            return None

    def ink_card(self, card_to_ink: Card) -> bool:
        """
        Moves a card from the hand to the inkwell if possible.

        Args:
            card_to_ink: The specific Card object instance from the hand to ink.

        Returns:
            True if the card was successfully inked, False otherwise.
        """
        if card_to_ink not in self.hand:
            print(f"{self.name} Error: Card '{card_to_ink.name}' not found in hand.")
            return False
        if not card_to_ink.inkable:
            print(f"{self.name} Error: Card '{card_to_ink.name}' is not inkable.")
            return False
        # Optional: Add check for self.has_inked_this_turn if enforcing 1 ink/turn strictly here

        # Move card
        self.hand.remove(card_to_ink)
        self.inkwell.append(card_to_ink)
        self.ready_ink =+ 1
        self.total_ink = len(self.inkwell) # Update total ink count
        self.has_inked_this_turn = True # Mark that ink action was taken
        print(f"{self.name}: Inked '{card_to_ink.name}'. Total ink: {self.total_ink}")
        return True

    def play_card(self, card_to_play: Card) -> bool:
        """
        Plays a card from the hand to the play area if enough ink is available.

        Args:
            card_to_play: The specific Card object instance from the hand to play.

        Returns:
            True if the card was successfully played, False otherwise.
        """
        if card_to_play not in self.hand:
            print(f"{self.name} Error: Card '{card_to_play.name}' not found in hand.")
            return False

        cost = card_to_play.cost
        if cost > self.ready_ink:
            print(f"{self.name} Error: Cannot play '{card_to_play.name}'. "
                  f"Cost {cost}, Ready Ink {self.ready_ink}.")
            return False

        # Pay the cost
        self.ready_ink -= cost
        self.exerted_ink += cost

        # Move card to play area
        self.hand.remove(card_to_play)
        # Add to play area with default state
        playable_card_state: PlayableCard = {'card': card_to_play, 'exerted': False, 'damage': 0}
        # Characters usually enter ready unless they have Rush or BodyGuard(handle later)
        # Items/Actions might resolve immediately (handle later)
        self.play_area.append(playable_card_state)

        print(f"{self.name}: Played '{card_to_play.name}' for {cost} ink. "
              f"({self.ready_ink} ink remaining).")

        # Basic handling for Actions - assume they resolve and discard immediately
        # More complex actions/songs will need engine support
        if card_to_play.type == "Action" or "Song" in card_to_play.type: # Simple check
             print(f"{self.name}: Action/Song '{card_to_play.name}' resolved (effect TBD) and discarded.")
             self.play_area.remove(playable_card_state) # Remove from play immediately
             self.discard_pile.append(card_to_play)

        return True

    def quest(self, playable_card: PlayableCard) -> bool:
        """
        Attempts to exert a character in play to gain lore.

        Args:
            playable_card: The dictionary representing the card in the play area.

        Returns:
            True if questing was successful, False otherwise.
        """
        if playable_card not in self.play_area:
             print(f"{self.name} Error: Card '{playable_card['card'].name}' not found in play area.")
             return False

        card = playable_card['card']
        if card.type != "Character":
             print(f"{self.name} Error: Cannot quest with non-character '{card.name}'.")
             return False
        if playable_card['exerted']:
             print(f"{self.name} Error: Cannot quest with exerted character '{card.name}'.")
             return False
        if card.lore is None or card.lore <= 0:
             print(f"{self.name} Error: Character '{card.name}' has no lore value to quest for.")
             return False

        # Exert the character
        playable_card['exerted'] = True
        # Gain lore
        lore_gained = card.lore
        self.lore += lore_gained
        print(f"{self.name}: Quested with '{card.name}' for {lore_gained} lore. "
              f"Total lore: {self.lore}.")
        return True

    # --- Turn Phase Methods ---

    def turn_start_ready_phase(self):
        """Performs start-of-turn readying actions."""
        print(f"\n--- {self.name}'s Turn Start ---")
        # 1. Ready all cards in play
        for p_card in self.play_area:
            if p_card['exerted']:
                 # print(f"{self.name}: Readying {p_card['card'].name}") # Can be verbose
                 p_card['exerted'] = False
        print(f"{self.name}: Readied all cards in play.")

        # 2. Ready ink
        self.ready_ink = self.total_ink
        self.exerted_ink = 0
        print(f"{self.name}: Readied {self.ready_ink} ink.")

        # 3. Reset turn flags
        self.has_drawn_this_turn = False
        self.has_inked_this_turn = False

    def turn_start_draw_phase(self):
        """Performs the start-of-turn draw."""
        if not self.has_drawn_this_turn:
            print(f"{self.name}: Drawing card for turn...")
            self.draw_card()
            self.has_drawn_this_turn = True
        else:
            print(f"{self.name}: Already drew this turn.")


    def display_state(self):
        """Prints a summary of the player's current state."""
        print(f"\n--- {self.name}'s State ---")
        print(f"Lore: {self.lore}")
        print(f"Hand ({len(self.hand)} cards): {[card.name for card in self.hand]}")
        print(f"Inkwell ({self.total_ink} total): Ready={self.ready_ink}, Exerted={self.exerted_ink}")
        # print(f"  Ink Cards: {[card.name for card in self.inkwell]}") # Optional detail
        print(f"Play Area ({len(self.play_area)} cards):")
        for p_card in self.play_area:
            state = "Ready" if not p_card['exerted'] else "Exerted"
            damage = f" ({p_card['damage']} dmg)" if p_card['damage'] > 0 else ""
            print(f"  - {p_card['card'].name} [{state}]{damage}")
        print(f"Deck: {len(self.deck)} cards remaining")
        print(f"Discard ({len(self.discard_pile)} cards): {[card.name for card in self.discard_pile]}")
        if self.lost_game: print("!! Player has lost the game (decked out) !!")
        print("--------------------")


# --- Example Usage ---
if __name__ == "__main__":
    # We need Cards and a Deck to test the Player
    try:
        from dataFetcher import fetch_lorcana_data
        from card import parse_card_data # Use the 3-map version
        from deck import Deck, load_deck_identifiers_from_file
    except ImportError:
        print("Could not import required modules for Player example. Exiting.")
        exit() # Cannot run example without dependencies

    # 1. Load Card Data
    print("Loading card data...")
    raw_card_data = fetch_lorcana_data()
    if not raw_card_data: exit("Failed to load card data.")
    all_cards_by_id, all_cards_by_name, all_cards_by_lowercase_name = parse_card_data(raw_card_data)
    if not all_cards_by_name: exit("Card name map is empty.")
    # Combine maps for robust lookup
    combined_name_map = {**all_cards_by_name, **all_cards_by_lowercase_name}


    # 2. Load a Deck
    deck_filename = "Decks/LandGo.txt" # Or your preferred test deck
    print(f"\nLoading deck '{deck_filename}'...")
    deck_card_names = load_deck_identifiers_from_file(deck_filename)
    if not deck_card_names: exit(f"Failed to load deck file '{deck_filename}'.")

    player1_deck = Deck(deck_card_names, combined_name_map)
    if player1_deck.failed_lookups: print("Warning: Deck created with missing cards.")
    if not player1_deck.is_valid(check_size=True, check_copies=True):
         print("Warning: Loaded deck is not valid according to rules.")
         # Continue anyway for testing player mechanics


    # 3. Create a Player instance
    player1 = Player(name="Player 1", deck=player1_deck, player_id=0)
    player1.display_state()

    # 4. Simulate some actions
    # --- Turn 1 ---
    player1.turn_start_ready_phase() # Readies initial state (0 ink)
    player1.turn_start_draw_phase() # Should already have initial hand, this is turn 1 draw

    # Find an inkable card in hand
    inkable_card = next((card for card in player1.hand if card.inkable), None)
    if inkable_card:
        player1.ink_card(inkable_card)
    else:
        print("Player 1: No inkable card found in hand to ink.")

    player1.display_state()

    # --- Turn 2 ---
    player1.turn_start_ready_phase() # Should ready 1 ink
    player1.turn_start_draw_phase() # Draw for turn 2

    # Try to play a 1-cost card (if available and affordable)
    playable_1_cost = next((card for card in player1.hand if card.cost == 1), None)
    if playable_1_cost and player1.ready_ink >= 1:
        player1.play_card(playable_1_cost)
    else:
        print("Player 1: Cannot play a 1-cost card (none in hand or not enough ink).")

    # Try to ink another card
    inkable_card_t2 = next((card for card in player1.hand if card.inkable), None)
    if inkable_card_t2:
        player1.ink_card(inkable_card_t2)

    player1.display_state()

    # --- Turn 3 ---
    player1.turn_start_ready_phase() # Should ready 2 ink
    player1.turn_start_draw_phase()

    # Try to quest with a character played last turn (if any)
    characters_in_play = [p_card for p_card in player1.play_area if p_card['card'].type == "Character"]
    if characters_in_play:
        # Quest with the first available character
        # (More complex AI needed later)
        char_to_quest = next((p_card for p_card in characters_in_play if not p_card['exerted']), None)
        if char_to_quest:
            player1.quest(char_to_quest)
        else:
            print("Player 1: No ready characters in play to quest with.")
    else:
        print("Player 1: No characters in play.")


    player1.display_state()
