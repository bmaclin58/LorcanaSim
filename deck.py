import os  # For file path operations
import random
from collections import Counter
from typing import Dict, List, Optional  # Added Tuple
from card import Card, parse_card_data

# --- Load Decklist from File ---
def load_deck_identifiers_from_file(filepath: str) -> Optional[List[str]]:
    """
    Loads a decklist from a text file.

    The file format is expected to be:
    Count Card Name
    (e.g., "4 Mickey Mouse - Brave Little Tailor")
    Lines starting with # are ignored. Text after # on a line is ignored.

    Args:
        filepath: The path to the .txt decklist file.

    Returns:
        A list of card names (strings), repeated according to the count,
        or None if the file cannot be read or parsed correctly.
    """
    if not os.path.exists(filepath):
        print(f"Error: Deck file not found at '{filepath}'")
        return None

    card_names: List[str] = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                # Remove comments first
                if '#' in line:
                    line = line.split('#', 1)[0]

                line = line.strip()
                if not line:  # Skip empty lines (or lines that were only comments)
                    continue

                parts = line.split(maxsplit=1)  # Split into count and the rest
                if len(parts) != 2:
                    print(
                        f"Warning: Invalid format on line {line_num} in '{filepath}': '{line}' (after comment removal)")
                    continue

                count_str, name_str = parts
                # Ensure name_str is also stripped of any potential trailing whitespace
                name_str = name_str.strip()
                try:
                    count = int(count_str)
                    if count <= 0:
                        print(f"Warning: Non-positive count on line {line_num} in '{filepath}': '{line}'")
                        continue
                    # Add the card name 'count' times to the list
                    card_names.extend([name_str] * count)  # Use cleaned name_str
                except ValueError:
                    print(f"Warning: Invalid count '{count_str}' on line {line_num} in '{filepath}': '{line}'")
                    continue

        print(f"Successfully loaded {len(card_names)} card identifiers (names) from '{filepath}'")
        return card_names

    except IOError as e:
        print(f"Error reading deck file '{filepath}': {e}")
        return None
    except Exception as e:  # Catch other potential errors during processing
        print(f"An unexpected error occurred while parsing '{filepath}': {e}")
        return None


class Deck:
	"""Represents a Lorcana deck, holding Card objects and providing deck operations."""

	def __init__(self, card_names: List[str], name_to_card_map: Dict[str, Card]):
		"""
		Initializes a Deck from a list of card names and a name-to-Card map.

		Args:
			card_names: A list of card names (strings) representing the cards
						to include in the deck (duplicates allowed as per list).
			name_to_card_map: A dictionary mapping card names (str) to their
							  corresponding Card objects.
		"""
		self.cards: List[Card] = []
		self.failed_lookups: List[str] = []  # Track names not found

		# Create a case-insensitive lookup dictionary
		case_insensitive_map = {name.lower(): card for name, card in name_to_card_map.items()}

		name_counts = Counter(card_names)
		processed_failures = set()

		for name, count in name_counts.items():
			# Try exact match first
			card_obj = name_to_card_map.get(name)

			# If not found, try case-insensitive match
			if not card_obj:
				card_obj = case_insensitive_map.get(name.lower())

			if card_obj:
				self.cards.extend([card_obj] * count)
			else:
				if name not in processed_failures:
					self.failed_lookups.append(name)
					print(f"Warning: Card name '{name}' not found in name_to_card_map.")
					processed_failures.add(name)

		if self.failed_lookups:
			print(f"Deck created with {len(self.cards)} cards. Could not find "
			      f"{len(self.failed_lookups)} unique card names: {self.failed_lookups}")
		else:
			# Only print success message if no failures
			print(f"Deck created successfully with {len(self.cards)} cards.")

		self.shuffle()

	def shuffle(self) -> None:
		"""Randomly shuffles the cards currently in the deck."""
		random.shuffle(self.cards)

	def draw(self) -> Optional[Card]:
		"""Removes and returns the top card from the deck."""
		if not self.cards:
			return None
		return self.cards.pop(0)

	def add_card(self, card: Card, to_bottom: bool = True) -> None:
		"""Adds a card to the deck (default: bottom)."""
		if to_bottom:
			self.cards.append(card)
		else:
			self.cards.insert(0, card)

	def __len__(self) -> int:
		"""Returns the number of cards remaining in the deck."""
		return len(self.cards)

	def count(self) -> int:
		"""Explicit method to get the number of cards remaining."""
		return len(self.cards)

	def lookAt(self,number) -> list:
		"""Returns the top number cards from the deck, in order of the deck (top to bottom)."""
		lookingAt = self.cards[:number]
		return lookingAt

	# --- Validation Methods ---

	def validate_size(self, min_size: int = 60) -> bool:
		return len(self.cards) >= min_size

	def validate_copies(self, max_copies: int = 4) -> bool:
		card_name_counts = Counter(card.name for card in self.cards)
		for name, count in card_name_counts.items():
			if count > max_copies:
				print(f"Validation Error: Card '{name}' found {count} times (max {max_copies}).")
				return False
		return True

	def get_colors(self) -> set[str]:
		colors = set()
		for card in self.cards:
			colors.update(card.colors)
		return colors

	def validate_colors(self, max_colors: int = 2) -> bool:
		return len(self.get_colors()) <= max_colors

	def is_valid(self, check_size: bool = True, check_copies: bool = True, check_colors: bool = False,
	             min_size: int = 60, max_copies: int = 4, max_colors: int = 2) -> bool:
		valid = True
		initial_count = len(self.cards)  # Store initial count for messages
		size_valid = self.validate_size(min_size)
		copies_valid = self.validate_copies(max_copies)
		colors_valid = True  # Assume valid unless checked and failed
		if check_colors:
			colors_valid = self.validate_colors(max_colors)

		if check_size and not size_valid:
			print(f"Validation Failed: Deck size is {initial_count}, required >= {min_size}.")
			valid = False
		if check_copies and not copies_valid:
			# Error message printed within validate_copies
			valid = False
		if check_colors and not colors_valid:
			print(f"Validation Failed: Deck contains {len(self.get_colors())} colors "
			      f"(limit {max_colors}): {self.get_colors()}.")
			valid = False

		return valid

	def __str__(self) -> str:
		return f"Deck ({len(self.cards)} cards remaining)"

	def __repr__(self) -> str:
		return f"<Deck containing {len(self.cards)} cards>"


# --- Example Usage ---
if __name__ == "__main__":
	# Assuming card.py and dataFetcher.py are available
	try:
		from dataFetcher import fetch_lorcana_data
		# parse_card_data is already imported/defined above
	except ImportError:
		print("Could not import from dataFetcher.py. Exiting.")
		exit()

	# 1. Get all card data and parse into maps
	print("Loading card data...")
	raw_card_data = fetch_lorcana_data()
	if not raw_card_data:
		print("Cannot proceed without card data. Exiting.")
		exit()

	all_cards_by_id, all_cards_by_name, all_cards_by_lowercase_name = parse_card_data(raw_card_data)
	print(f"Loaded {len(all_cards_by_id)} unique cards by ID, {len(all_cards_by_name)} by Name.")

	# Merge the name mappings for the deck constructor
	combined_name_map = {**all_cards_by_name, **all_cards_by_lowercase_name}

	if not combined_name_map:
		print("Card name map is empty. Cannot load deck from file. Exiting.")
		exit()

	# 2. Define the decklist filename and content
	# --- Use a more realistic decklist for testing ---
	deck_filename = "Decks/BouncingBosses.txt"
	print(f"\n--- Using Deck File ({deck_filename}) ---")

	# 3. Load the deck identifiers from the file
	print(f"\n--- Loading Deck from {deck_filename} ---")
	deck_card_names = load_deck_identifiers_from_file(deck_filename)

	if deck_card_names:
		# 4. Create the Deck instance using the loaded names and the name map
		print("\n--- Creating Deck Instance ---")
		my_deck = Deck(deck_card_names, combined_name_map)
		# Creation message now printed inside __init__

		# Check if deck creation was successful (no failed lookups)
		if my_deck.failed_lookups:
			print("Deck creation encountered issues finding card names. Please check the deck file and API data.")
		else:
			# 5. Validate the created deck (only if creation was successful)
			print("\n--- Validating Loaded Deck ---")
			# Check size, copies, and optionally colors (expect success for the sample)
			is_deck_valid = my_deck.is_valid(check_size=True, check_copies=True, check_colors=True, max_colors=2)
			print(f"Deck validation result: {'Valid' if is_deck_valid else 'Invalid'}")
			print(f"Deck Colors: {my_deck.get_colors()}")

			# 6. Demonstrate operations (only if creation was successful)
			print("\n--- Deck Operations ---")
			print(f"Deck size before draw: {len(my_deck)}")
			print("Drawing 7 cards (initial hand):")
			hand = []
			for i in range(7):
				drawn_card = my_deck.draw()
				if drawn_card:
					hand.append(drawn_card)
					print(f"  Drew {i + 1}: {drawn_card.name}")
				else:
					print("  Deck ran out of cards!")
					break
			print(f"Hand size: {len(hand)}")
			print(f"Deck size after drawing: {len(my_deck)}")

	else:
		print("Failed to load deck identifiers from file.")

	print("\nScript finished.")
