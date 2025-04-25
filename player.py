# player.py

from typing import List, Optional, Dict, Any # For type hinting
import random # Potentially for mulligan later, but not strictly needed yet

# Attempt to import necessary classes, handle potential ImportError
try:
    from card import Card
    from deck import Deck
except ImportError:
    print("Warning: Could not import Card or Deck classes. Player class functionality will be limited.")

# Define a type alias for cards in play for clarity
# Each item will be a dictionary holding the card and its state
# Added 'uuid' for unique identification within the play area if needed later
PlayableCard = Dict[str, Any] # Keys: 'card': Card, 'exerted': bool, 'damage': int, 'uuid': int

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
        # Each entry is a PlayableCard dictionary
        self.play_area: List[PlayableCard] = []
        self.lore: int = 0
        self._play_area_uuid_counter = 0 # Simple counter for unique IDs in play

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

    def _generate_play_uuid(self) -> int:
        """Generates a simple unique ID for a card entering the play area."""
        self._play_area_uuid_counter += 1
        return self._play_area_uuid_counter

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
        if self.has_inked_this_turn:
             print(f"{self.name} Error: Already inked a card this turn.")
             return False

        # Move card
        self.hand.remove(card_to_ink)
        self.inkwell.append(card_to_ink)
        self.total_ink = len(self.inkwell) # Update total ink count
        self.has_inked_this_turn = True # Mark that ink action was taken
        print(f"{self.name}: Inked '{card_to_ink.name}'. Total ink: {self.total_ink}")
        return True

    def play_card(self, card_to_play: Card) -> Optional[PlayableCard]:
        """
        Plays a card from the hand to the play area if enough ink is available.
        Handles immediate discard for Actions/Songs.

        Args:
            card_to_play: The specific Card object instance from the hand to play.

        Returns:
            The PlayableCard dictionary representing the card in play if it stays,
            or None if it was an Action/Song or playing failed.
        """
        if card_to_play not in self.hand:
            print(f"{self.name} Error: Card '{card_to_play.name}' not found in hand.")
            return None

        cost = card_to_play.cost
        if cost > self.ready_ink:
            print(f"{self.name} Error: Cannot play '{card_to_play.name}'. "
                  f"Cost {cost}, Ready Ink {self.ready_ink}.")
            return None

        # Pay the cost
        self.ready_ink -= cost
        self.exerted_ink += cost

        # Move card from hand
        self.hand.remove(card_to_play)

        print(f"{self.name}: Played '{card_to_play.name}' for {cost} ink. "
              f"({self.ready_ink} ink remaining).")

        # Handle Actions/Songs - assume they resolve and discard immediately
        # More complex effects need engine support
        if card_to_play.type == "Action" or "Song" in card_to_play.type: # Simple check
             print(f"{self.name}: Action/Song '{card_to_play.name}' resolved (effect TBD) and discarded.")
             self.discard_pile.append(card_to_play)
             # TODO: Trigger any "On Play" effects here later
             return None # Doesn't stay in play

        # For Characters, Items, Locations - Add to play area
        playable_card_state: PlayableCard = {
            'card': card_to_play,
            'exerted': False, # Characters enter ready unless Rush
            'damage': 0,
            'uuid': self._generate_play_uuid() # Assign a unique ID for this instance
            # Add other state flags later (e.g., 'can_challenge_this_turn': False for summoning sickness)
        }
        # TODO: Handle summoning sickness - characters usually can't challenge/quest the turn they are played unless they have Rush
        self.play_area.append(playable_card_state)
        # TODO: Trigger any "On Play" effects here later
        return playable_card_state


    def quest(self, playable_card: PlayableCard) -> bool:
        """
        Attempts to exert a character in play to gain lore.

        Args:
            playable_card: The dictionary representing the card in the play area.

        Returns:
            True if questing was successful, False otherwise.
        """
        if playable_card not in self.play_area:
             print(f"{self.name} Error: Card '{playable_card['card'].name}' (UUID: {playable_card.get('uuid', 'N/A')}) not found in play area.")
             return False

        card = playable_card['card']
        if card.type != "Character":
             print(f"{self.name} Error: Cannot quest with non-character '{card.name}'.")
             return False
        if playable_card['exerted']:
             print(f"{self.name} Error: Cannot quest with exerted character '{card.name}'.")
             return False
        # TODO: Add check for summoning sickness if not implemented elsewhere

        if card.lore is None or card.lore <= 0:
             # Some cards might gain lore ability later, but base check is useful
             print(f"{self.name}: Character '{card.name}' has no base lore value to quest for.")
             return False # Or potentially allow questing for 0 if effects can grant lore? TBD

        # Exert the character
        playable_card['exerted'] = True
        # Gain lore
        lore_gained = card.lore
        self.lore += lore_gained
        print(f"{self.name}: Quested with '{card.name}' for {lore_gained} lore. "
              f"Total lore: {self.lore}.")
        return True

    def challenge(self, attacker_pc: PlayableCard, defender_pc: PlayableCard, opponent: 'Player') -> bool:
        """
        Handles the challenge action between two characters.

        Args:
            attacker_pc: The PlayableCard dict of the attacking character (from self.play_area).
            defender_pc: The PlayableCard dict of the defending character (from opponent.play_area).
            opponent: The opposing Player object.

        Returns:
            True if the challenge sequence was initiated, False otherwise (e.g., invalid target).
        """
        # --- Validation ---
        if attacker_pc not in self.play_area:
            print(f"{self.name} Error: Attacker '{attacker_pc['card'].name}' not in play area.")
            return False
        if defender_pc not in opponent.play_area:
             print(f"{self.name} Error: Defender '{defender_pc['card'].name}' not in opponent's play area.")
             return False

        attacker_card = attacker_pc['card']
        defender_card = defender_pc['card']

        if attacker_card.type != "Character":
            print(f"{self.name} Error: Attacker '{attacker_card.name}' is not a character.")
            return False
        if defender_card.type != "Character":
            print(f"{self.name} Error: Defender '{defender_card.name}' is not a character.")
            return False
        if attacker_pc['exerted']:
            print(f"{self.name} Error: Attacker '{attacker_card.name}' is already exerted.")
            return False
        # TODO: Add check for summoning sickness for the attacker
        # TODO: Add checks for keywords like Evasive, Ward, Bodyguard

        print(f"{self.name}: '{attacker_card.name}' challenges '{defender_card.name}'!")

        # --- Exert Attacker ---
        attacker_pc['exerted'] = True

        # --- Damage Calculation ---
        # Use strength, default to 0 if None (shouldn't happen for chars, but safety)
        attacker_strength = attacker_card.strength or 0
        defender_strength = defender_card.strength or 0
        # TODO: Factor in Challenger keyword bonus here

        print(f"  > '{attacker_card.name}' ({attacker_strength} Str) deals {attacker_strength} damage.")
        print(f"  > '{defender_card.name}' ({defender_strength} Str) deals {defender_strength} damage.")

        # --- Apply Damage ---
        # Note: Damage is applied simultaneously
        defender_pc['damage'] += attacker_strength
        attacker_pc['damage'] += defender_strength

        print(f"  > '{defender_card.name}' now has {defender_pc['damage']} damage (Willpower: {defender_card.willpower or 0}).")
        print(f"  > '{attacker_card.name}' now has {attacker_pc['damage']} damage (Willpower: {attacker_card.willpower or 0}).")

        # --- Check for Banishment ---
        # Check defender first
        if defender_pc['damage'] >= (defender_card.willpower or 0):
            print(f"  > '{defender_card.name}' is banished!")
            opponent.banish(defender_pc) # Opponent handles their banishment

        # Check attacker (only if not already banished by the defender check, though simultaneous)
        # Need to refetch from play_area in case it was banished
        if attacker_pc in self.play_area and attacker_pc['damage'] >= (attacker_card.willpower or 0):
            print(f"  > '{attacker_card.name}' is banished!")
            self.banish(attacker_pc) # Self handles own banishment

        return True


    def banish(self, playable_card: PlayableCard):
        """
        Moves a card from the play area to the discard pile.

        Args:
            playable_card: The dictionary representing the card to be banished.
        """
        if playable_card in self.play_area:
             self.play_area.remove(playable_card)
             self.discard_pile.append(playable_card['card'])
             print(f"{self.name}: '{playable_card['card'].name}' moved from play to discard.")
             # TODO: Trigger any "On Banish" effects here later
        else:
             # This might happen if multiple effects try to banish the same card
             print(f"{self.name} Info: Tried to banish '{playable_card['card'].name}', but it was already removed.")


    # --- Turn Phase Methods ---

    def turn_start_ready_phase(self):
        """Performs start-of-turn readying actions."""
        print(f"\n--- {self.name}'s Turn Start (Ready Phase) ---")
        # 1. Ready all cards in play
        readied_count = 0
        for p_card in self.play_area:
            if p_card['exerted']:
                 p_card['exerted'] = False
                 readied_count += 1
        if readied_count > 0: print(f"{self.name}: Readied {readied_count} card(s) in play.")

        # 2. Ready ink
        self.ready_ink = self.total_ink
        self.exerted_ink = 0
        print(f"{self.name}: Readied {self.ready_ink} ink.")

        # 3. Reset turn flags
        self.has_drawn_this_turn = False
        self.has_inked_this_turn = False

    def turn_start_set_phase(self):
        """
        Performs start-of-turn 'Set' phase actions (Check win, effects).
        Called by GameState *before* Ready phase usually.
        """
        # Currently empty, win check is in GameState.next_turn
        # TODO: Add any "start of turn" effects triggering here later
        pass


    def turn_start_draw_phase(self):
        """Performs the start-of-turn draw."""
        print(f"--- {self.name}'s Turn Start (Draw Phase) ---")
        if not self.has_drawn_this_turn:
            # print(f"{self.name}: Drawing card for turn...") # Less verbose
            self.draw_card()
            self.has_drawn_this_turn = True
        # else: # No need to print if already drawn
            # print(f"{self.name}: Already drew this turn.")


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
            stats = ""
            if p_card['card'].type == 'Character':
                 stats = f" [{p_card['card'].strength or '?'}/{p_card['card'].willpower or '?'}|{p_card['card'].lore or '?'}]"
            print(f"  - {p_card['card'].name}{stats} [{state}]{damage} (UUID: {p_card.get('uuid', 'N/A')})")
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
    combined_name_map = {**all_cards_by_name, **all_cards_by_lowercase_name}


    # 2. Load a Deck (using dummy data for simplicity here)
    # Create some dummy cards for testing challenge
    dummy_card_data = [
        Card({'Name': 'Basic Attacker', 'Cost': 1, 'Inkable': True, 'Type': 'Character', 'Strength': 2, 'Willpower': 2, 'Lore': 1}),
        Card({'Name': 'Basic Defender', 'Cost': 1, 'Inkable': True, 'Type': 'Character', 'Strength': 1, 'Willpower': 3, 'Lore': 1}),
        Card({'Name': 'Big Guy', 'Cost': 3, 'Inkable': True, 'Type': 'Character', 'Strength': 4, 'Willpower': 4, 'Lore': 2}),
        Card({'Name': 'Ink Fodder', 'Cost': 1, 'Inkable': True, 'Type': 'Action'}), # Action to test play
    ]
    # Create a simple deck list from these dummies
    test_deck_cards = []
    for c in dummy_card_data:
        test_deck_cards.extend([c] * 4) # 4 copies of each
    random.shuffle(test_deck_cards)
    # Create a dummy Deck object directly (bypassing file load for this example)
    class SimpleDeck:
        def __init__(self, cards): self.cards = list(cards)
        def draw(self): return self.cards.pop(0) if self.cards else None
        def __len__(self): return len(self.cards)

    player1_deck = SimpleDeck(test_deck_cards[:]) # Give copies
    player2_deck = SimpleDeck(test_deck_cards[:])

    # 3. Create Player instances
    player1 = Player(name="Player 1", deck=player1_deck, player_id=0)
    player2 = Player(name="Player 2", deck=player2_deck, player_id=1)

    # Manually set up a scenario for challenge
    print("\n--- Setting up Challenge Scenario ---")
    player1.ready_ink = 5 # Give some ink
    player2.ready_ink = 5

    # Player 1 plays an attacker
    attacker_card_obj = next((c for c in dummy_card_data if c.name == 'Basic Attacker'), None)
    if attacker_card_obj:
        player1.hand.append(attacker_card_obj) # Add to hand first
        attacker_pc = player1.play_card(attacker_card_obj)
        if attacker_pc: print(f"Player 1 has '{attacker_pc['card'].name}' in play.")

    # Player 2 plays a defender
    defender_card_obj = next((c for c in dummy_card_data if c.name == 'Basic Defender'), None)
    if defender_card_obj:
        player2.hand.append(defender_card_obj)
        defender_pc = player2.play_card(defender_card_obj)
        if defender_pc: print(f"Player 2 has '{defender_pc['card'].name}' in play.")

    player1.display_state()
    player2.display_state()

    # 4. Simulate a challenge
    print("\n--- Simulating Challenge ---")
    if attacker_pc and defender_pc:
        # Assume it's Player 1's turn and they choose to challenge
        # TODO: Add summoning sickness check - for now assume attacker can challenge
        player1.challenge(attacker_pc, defender_pc, player2)
    else:
        print("Could not set up challenge scenario properly.")

    player1.display_state()
    player2.display_state()
