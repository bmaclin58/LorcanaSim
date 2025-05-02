import json


def create_Card_Database ():
    card_data_file = "lorcana_cards_simplified.json"
    card_database = {}
    with open(card_data_file, "r", encoding="utf-8") as f:
        card_data = json.load(f)

    for card in card_data:
        cardID = card.get("Unique_ID")

        card_database[cardID] = {
            "Name":     card.get("Name"),
            "Color":    card.get("Color"),
            "Cost":     card.get("Cost"),
            "Inkable":  card.get("Inkable"),
            "Type":     card.get("Type"),
            "Body_Text": card.get("Body_Text"),
            "Abilities": card.get("Abilities"),
            "Willpower": card.get("Willpower"),
            "Move Cost": card.get("Move Cost"),
            "Strength":  card.get("Strength"),
            "Lore":      card.get("Lore"),
        }

    return card_database

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
        self.unique_id: str | None = card_data.get("Unique_ID") # Keep Unique_ID if available
        self.cost: int = card_data.get("Cost", 0)
        self.inkable: bool = card_data.get("Inkable", False)

        # --- Card Type & Colors ---
        self.type: str = card_data.get("Type", "Unknown Type")
        raw_color: str | None = card_data.get("Color")
        self.colors: list[str] = [c.strip() for c in raw_color.split(',')] if raw_color else []

        # --- Character Stats (handle None for non-characters) ---
        self.strength: int | None = card_data.get("Strength")
        self.willpower: int | None = card_data.get("Willpower")
        self.lore: int | None = card_data.get("Lore")

        # --- Rules Text & Keywords ---
        self.body_text: str = card_data.get("Body_Text", "")
        raw_class: str | None = card_data.get("Classifications")
        self.classifications: list[str] = [c.strip() for c in raw_class.split(',')] if raw_class else []
        raw_abilities: str | None = card_data.get("Abilities")
        self.abilities: list[str] = [a.strip() for a in raw_abilities.split(',')] if raw_abilities else []

        # --- Sanity check/conversion for numerical stats ---
        if self.strength is not None:
            try:
                self.strength = int(self.strength)
            except (ValueError, TypeError):
                # print(f"Warning: Could not convert Strength '{self.strength}' to int for card '{self.name}'. Setting to None.")
                self.strength = None
        if self.willpower is not None:
            try:
                self.willpower = int(self.willpower)
            except (ValueError, TypeError):
                # print(f"Warning: Could not convert Willpower '{self.willpower}' to int for card '{self.name}'. Setting to None.")
                self.willpower = None
        if self.lore is not None:
            try:
                self.lore = int(self.lore)
            except (ValueError, TypeError):
                # print(f"Warning: Could not convert Lore '{self.lore}' to int for card '{self.name}'. Setting to None.")
                self.lore = None

    def __str__(self) -> str:
        """Provides a user-friendly string representation."""
        if self.type == "Character":
            stats = f"{self.strength or '?'}/{self.willpower or '?'} {self.lore or '?'}L"
        else:
            stats = self.type
        ink = "Inkable" if self.inkable else "Non-Ink"
        return f"{self.name} ({self.cost}) [{'/'.join(self.colors)}] - {stats} ({ink})"

    def __repr__(self) -> str:
        """Provides a developer-friendly string representation."""
        return f"<Card(Name='{self.name}', ID='{self.unique_id or 'N/A'}', Cost={self.cost}, Type='{self.type}')>"

# --- Updated Helper function to parse the full list ---

def parse_card_data(raw_data_list: list[dict]) -> tuple[dict[str, Card], dict[str, Card], dict[str, Card]]:
    """
    Parses a list of raw card dictionaries into dictionaries of Card objects,
    mapped by Unique_ID, by Name, and by lowercase Name.

    Args:
        raw_data_list: A list of dictionaries, where each dict is raw card data.

    Returns:
        A tuple containing three dictionaries:
        1. cards_by_id: Maps Unique_ID (str) to Card object.
        2. cards_by_name: Maps Name (str) to Card object.
        3. cards_by_lowercase_name: Maps lowercase Name (str) to Card object.
    """
    cards_by_id = {}
    cards_by_name = {}
    cards_by_lowercase_name = {}
    if not raw_data_list:
        return cards_by_id, cards_by_name, cards_by_lowercase_name  # Return all three

    duplicate_names = set()
    seen_names = set()

    for card_data in raw_data_list:
        card_obj = Card(card_data)

        # Map by Unique_ID if available
        if card_obj.unique_id:
            if card_obj.unique_id in cards_by_id:
                print(f"Warning: Duplicate Unique_ID '{card_obj.unique_id}' found. Overwriting previous entry.")
            cards_by_id[card_obj.unique_id] = card_obj
        else:
            print(f"Warning: Card '{card_obj.name}' missing Unique_ID.")

        # Map by Name
        if card_obj.name:
            if card_obj.name in cards_by_name:
                # Lorcana rules generally allow different versions of Characters
                # but deckbuilding limits copies by *full name*.
                # If names are truly identical across different Unique_IDs, it's ambiguous.
                # For now, we'll store the *last* one encountered for the name map,
                # but flag duplicates. Relying on Unique_ID is safer if possible.
                if card_obj.name not in seen_names:  # Only warn once per duplicated name
                    print(
                        f"Warning: Duplicate card Name '{card_obj.name}' found. Name map will only store one version.")
                    duplicate_names.add(card_obj.name)
                seen_names.add(card_obj.name)
            cards_by_name[card_obj.name] = card_obj

            # Also map by lowercase name for case-insensitive lookups
            cards_by_lowercase_name[card_obj.name.lower()] = card_obj
        else:
            print(f"Warning: Card data missing Name field: {card_data}")

    print(f"Parsed {len(cards_by_id)} cards by Unique_ID and {len(cards_by_name)} cards by Name.")
    if duplicate_names:
        print(f"Note: The following card names appeared multiple times: {list(duplicate_names)}")
    return cards_by_id, cards_by_name, cards_by_lowercase_name  # Return all three

# --- Example usage (demonstrates using fetcher and parser) ---
if __name__ == "__main__":

    raw_cards = create_Card_Database()
    print(f"Raw Card Data: {raw_cards['ARI-019']}")
    '''
    if raw_cards:
        all_cards_by_id, all_cards_by_name, all_cards_by_lowercase_name = parse_card_data(raw_cards)

        print(f"\nTotal distinct cards parsed (by ID): {len(all_cards_by_id)}")
        print(f"Total distinct cards parsed (by Name): {len(all_cards_by_name)}")

        # Example: Accessing via ID
        pascal_id_key = "ARI-019"
        if pascal_id_key in all_cards_by_id:
            print(f"\nAccess via ID '{pascal_id_key}': {repr(all_cards_by_id[pascal_id_key])}")

        # Example: Accessing via Name
        pascal_name_key = "Pascal - Garden Chameleon"
        if pascal_name_key in all_cards_by_name:
            print(f"Access via Name '{pascal_name_key}': {repr(all_cards_by_name[pascal_name_key])}")

    else:
        print("Could not retrieve card data to parse.")
'''
