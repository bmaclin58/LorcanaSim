import json

class Card:
    """Represents a single Lorcana card with relevant attributes for simulation."""

    def __init__(self, card_data: dict):
        """
        Initializes a Card object from a dictionary of card data (from API).

        Args:
            card_data (dict): A dictionary containing the raw data for one card.
        """
        # --- Core Identification & Cost ---
        self.name: str = card_data.get("Name", "Unknown Name")
        # Store Unique_ID for precise identification if needed later
        self.unique_id: str | None = card_data.get("Unique_ID")
        self.cost: int = card_data.get("Cost", 0) # Default cost 0 if missing
        self.inkable: bool = card_data.get("Inkable", False) # Default False if missing

        # --- Card Type & Colors ---
        self.type: str = card_data.get("Type", "Unknown Type") # e.g., Character, Action, Item
        raw_color: str | None = card_data.get("Color")
        # Split comma-separated colors into a list, handle None/empty string
        self.colors: list[str] = [c.strip() for c in raw_color.split(',')] if raw_color else []

        # --- Character Stats (handle None for non-characters) ---
        self.strength: int | None = card_data.get("Strength")
        self.willpower: int | None = card_data.get("Willpower")
        self.lore: int | None = card_data.get("Lore") # Use None if missing, check type later

        # --- Rules Text & Keywords ---
        # Store raw text - parsing happens in game engine
        self.body_text: str = card_data.get("Body_Text", "")
        # Store list of classifications (e.g., Dreamborn, Hero, Princess)
        raw_class: str | None = card_data.get("Classifications")
        self.classifications: list[str] = [c.strip() for c in raw_class.split(',')] if raw_class else []
        # Store list of keyword abilities (often repeated in body_text)
        raw_abilities: str | None = card_data.get("Abilities")
        self.abilities: list[str] = [a.strip() for a in raw_abilities.split(',')] if raw_abilities else []

        # --- Sanity check/conversion for numerical stats ---
        # Ensure numerical fields are integers if they exist
        if self.strength is not None:
            try:
                self.strength = int(self.strength)
            except (ValueError, TypeError):
                print(f"Warning: Could not convert Strength '{self.strength}' to int for card '{self.name}'. Setting to None.")
                self.strength = None
        if self.willpower is not None:
            try:
                self.willpower = int(self.willpower)
            except (ValueError, TypeError):
                print(f"Warning: Could not convert Willpower '{self.willpower}' to int for card '{self.name}'. Setting to None.")
                self.willpower = None
        if self.lore is not None:
            try:
                self.lore = int(self.lore)
            except (ValueError, TypeError):
                print(f"Warning: Could not convert Lore '{self.lore}' to int for card '{self.name}'. Setting to None.")
                self.lore = None

        # Store the original raw data dictionary if needed for debugging or future fields
        # self._raw_data = card_data


    def __str__(self) -> str:
        """Provides a user-friendly string representation."""
        if self.type == "Character":
            stats = f"{self.strength}/{self.willpower} {self.lore}L"
        else:
            stats = self.type
        ink = "Inkable" if self.inkable else "Non-Ink"
        return f"{self.name} ({self.cost}) [{'/'.join(self.colors)}] - {stats} ({ink})"

    def __repr__(self) -> str:
        """Provides a developer-friendly string representation."""
        # Consider adding unique_id here for clarity if needed
        return f"<Card(Name='{self.name}', Cost={self.cost}, Type='{self.type}')>"

# --- Helper function to parse the full list ---

def parse_card_data(raw_data_list: list[dict]) -> dict[str, Card]:
    """
    Parses a list of raw card dictionaries into a dictionary of Card objects.

    Args:
        raw_data_list: A list of dictionaries, where each dict is raw card data.

    Returns:
        A dictionary mapping unique card identifiers (e.g., Unique_ID or Name)
        to Card objects. Using Unique_ID is generally safer if available.
        Falls back to Name if Unique_ID is missing.
    """
    cards = {}
    if not raw_data_list:
        return cards

    for card_data in raw_data_list:
        card_obj = Card(card_data)
        # Use Unique_ID as the primary key if available and valid
        key = card_obj.unique_id if card_obj.unique_id else card_obj.name
        if not key:
            print(f"Warning: Card data missing both Unique_ID and Name: {card_data}")
            continue # Skip cards without a usable identifier

        if key in cards:
             # This might happen if fallback to Name is used and names aren't unique
             # Or if the API somehow returns duplicate Unique_IDs
             print(f"Warning: Duplicate card identifier '{key}' found. Overwriting previous entry.")
        cards[key] = card_obj

    print(f"Parsed {len(cards)} cards into Card objects.")
    return cards

# --- Example usage (demonstrates using fetcher and parser) ---
if __name__ == "__main__":
    try:
        from dataFetcher import fetch_lorcana_data
    except ImportError:
        print("Error: data_fetcher.py not found or fetch_lorcana_data function missing.")
        # Define a dummy function for basic testing if fetcher is unavailable
        '''
        def fetch_lorcana_data(**kwargs):
            print("Using dummy fetch_lorcana_data.")
            # Example structure matching the user's provided data
            return [
                {
                    "Artist": "Aubrey Archer", "Set_Name": "Archazia's Island", "Classifications": "Storyborn, Ally",
                    "Date_Added": "2025-03-08T22:29:21", "Abilities": "Evasive", "Set_Num": 7,
                    "Color": "Amber, Amethyst", "Gamemode": "Lorcana", "Franchise": "Tangled",
                    "Image": "https://lorcana-api.com/images/pascal/garden_chameleon/pascal-garden_chameleon-large.png",
                    "Cost": 4, "Inkable": False, "Name": "Pascal - Garden Chameleon", "Type": "Character",
                    "Lore": 3, "Rarity": "Uncommon", "Flavor_Text": "Once Pascal got into Archazia's flowerbeds...",
                    "Unique_ID": "ARI-019", "Card_Num": 19,
                    "Body_Text": "Evasive (Only characters with Evasive can challenge this character.)",
                    "Willpower": 3, "Date_Modified": "2025-03-09 00:50:35.0", "Strength": 3, "Set_ID": "ARI"
                },
                {
                    "Name": "Fire the Cannons!", "Cost": 1, "Inkable": True, "Type": "Action", "Color": "Ruby",
                    "Body_Text": "Deal 2 damage to chosen character.", "Unique_ID": "TFC-001",
                    "Abilities": None, "Classifications": None, "Lore": None, "Strength": None, "Willpower": None
                }
            ]
'''
    # 1. Fetch the raw data
    raw_cards = fetch_lorcana_data() # Uses local file if available and recent

    if raw_cards:
        # 2. Parse the raw data into Card objects
        all_cards = parse_card_data(raw_cards)

        # 3. Now you can access the cards dictionary
        print(f"\nTotal distinct cards parsed: {len(all_cards)}")

        # Example: Accessing a specific card (if it exists)
        pascal_key = "ARI-019" # Using Unique_ID
        if pascal_key in all_cards:
            pascal_card = all_cards[pascal_key]
            print(f"\nExample Access:")
            print(f"  Card: {pascal_card.name}")
            print(f"  Cost: {pascal_card.cost}, Inkable: {pascal_card.inkable}")
            print(f"  Type: {pascal_card.type}")
            print(f"  Colors: {pascal_card.colors}")
            print(f"  Stats: S:{pascal_card.strength} W:{pascal_card.willpower} L:{pascal_card.lore}")
            print(f"  Keywords: {pascal_card.abilities}")
            print(f"  Classifications: {pascal_card.classifications}")
            print(f"  Body Text: {pascal_card.body_text}")
            print(f"  Repr: {repr(pascal_card)}")
            print(f"  Str: {str(pascal_card)}")

        # Example: Accessing an action card
        fire_cannons_key = "TFC-197"
        if fire_cannons_key in all_cards:
             cannon_card = all_cards[fire_cannons_key]
             print(f"\nExample Action Card:")
             print(f"  Card: {cannon_card.name}")
             print(f"  Cost: {cannon_card.cost}, Inkable: {cannon_card.inkable}")
             print(f"  Type: {cannon_card.type}")
             print(f"  Colors: {cannon_card.colors}")
             print(f"  Stats: Str:{cannon_card.strength} Will:{cannon_card.willpower} Lore:{cannon_card.lore}") # Expect None
             print(f"  Body Text: {cannon_card.body_text}")
             print(f"  Str: {str(cannon_card)}")

    else:
        print("Could not retrieve card data to parse.")
