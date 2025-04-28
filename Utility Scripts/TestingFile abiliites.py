import json
import os
from typing import Dict, List, Optional, Any

from CardEffects.ability import Ability, AbilityCost, Effect
from CardEffects.ability_parser import parse_abilities


def load_card_database(file_path: str) -> List[Dict[str, Any]]:
    """Load the card database from a JSON file."""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def find_card_by_id(
    card_database: List[Dict[str, Any]], unique_id: str
) -> Optional[Dict[str, Any]]:
    """Find a specific card by its Unique ID."""
    for card in card_database:
        if card.get("Unique_ID") == unique_id:
            return card
    return None


def parse_card_abilities(card: Dict[str, Any]) -> List[Ability]:
    """Parse the abilities and effects for a specific card."""
    body_text = card.get("Body_Text")
    abilities_text = card.get("Abilities")
    return parse_abilities(body_text, abilities_text)


def test_card_abilities(unique_id: str) -> None:
    """Test the abilities and effects for a card with a specific Unique ID."""
    # Get the parent directory of the script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)

    # Define the file paths using the parent directory
    json_file = os.path.join(parent_dir, "lorcana_cards_simplified.json")
    
    cards = load_card_database(json_file)

    # Find the card
    card = find_card_by_id(cards, unique_id)
    if not card:
        print(f"Card with Unique ID '{unique_id}' not found.")
        return

    # Print card info
    print(f"Testing Card: {card.get('Name')} ({card.get('Unique_ID')})")
    print(f"Type: {card.get('Type')}")
    print(f"Color: {card.get('Color')}")
    print(f"Cost: {card.get('Cost')}")
    print(f"Body Text: {card.get('Body_Text')}")
    print(f"Abilities: {card.get('Abilities')}")
    print("\n=== Parsed Abilities ===")

    # Parse and display abilities
    abilities = parse_card_abilities(card)
    for i, ability in enumerate(abilities, 1):
        print(f"\nAbility #{i}:")
        print(f"  Trigger: {ability.trigger.name}")
        if ability.cost:
            print(f"  Cost: {ability.cost}")

        # Print effects
        print(f"  Effects ({len(ability.effects)}):")
        for j, effect in enumerate(ability.effects, 1):
            print(f"    Effect #{j}: {effect.effect_type.name} on {effect.target.name}")
            if effect.parameters:
                print(f"      Parameters: {effect.parameters}")

    print("\n=== Effect Evaluation Simulation ===")
    # Here you could add logic to simulate the effects in your game state

    return abilities


# Example usage
if __name__ == "__main__":
    #test_card_abilities("URS-138")
    test_card_abilities("URS-158")
