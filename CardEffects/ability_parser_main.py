import json
import re
import sys
import os
from typing import List, Dict, Any, Optional, Tuple

# Add the parent directory to the path so we can import from CardEffects
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from CardEffects.ability import Ability, AbilityCost, Effect
from CardEffects.ability_parser import parse_abilities
from CardEffects.effects_Definitions import EffectType, TargetType, TriggerCondition
from CardEffects.KeywordMap import create_keyword_effect

def load_cards(file_path: str) -> List[Dict[str, Any]]:
    """
    Load card data from a JSON file.

    Args:
        file_path: Path to the JSON file containing card data

    Returns:
        List of card data dictionaries
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_body_texts(file_path: str) -> List[str]:
    """
    Load unique body texts from a JSON file.

    Args:
        file_path: Path to the JSON file containing body texts

    Returns:
        List of unique body text strings
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Extract just the body text strings
    return [item.get("Body_Text", "") for item in data if item.get("Body_Text")]

def parse_card_abilities(cards: List[Dict[str, Any]]) -> Dict[str, List[Ability]]:
    """
    Parse abilities for all cards.

    Args:
        cards: List of card data dictionaries

    Returns:
        Dictionary mapping card Unique_ID to a list of parsed Ability objects
    """
    card_abilities = {}

    for card in cards:
        card_id = card.get("Unique_ID")
        if not card_id:
            continue

        body_text = card.get("Body_Text", "")
        abilities_text = card.get("Abilities", "")

        # Skip cards with no text
        if not body_text and not abilities_text:
            card_abilities[card_id] = []
            continue

        # Parse abilities using the existing parser
        abilities = parse_abilities(body_text, abilities_text)
        card_abilities[card_id] = abilities

    return card_abilities

def analyze_body_texts(body_texts: List[str]) -> Dict[str, int]:
    """
    Analyze body texts to identify common patterns and their frequencies.

    Args:
        body_texts: List of body text strings

    Returns:
        Dictionary mapping pattern types to their frequencies
    """
    pattern_counts = {}

    # Common patterns to look for
    patterns = {
        "ink_cost": r"\d+\{i\}",
        "exert": r"\{e\}",
        "strength_mod": r"[+-]\d+\{s\}",
        "willpower_mod": r"[+-]\d+\{w\}",
        "lore_mod": r"[+-]\d+\{l\}",
        "draw_card": r"draw (?:a|one|\d+) card",
        "gain_lore": r"gain \d+ lore",
        "deal_damage": r"deal \d+ damage",
        "start_of_turn": r"At the start of your turn",
        "end_of_turn": r"At the end of your turn",
        "when_play": r"When you play",
        "whenever": r"Whenever",
        "chosen_character": r"[Cc]hosen character",
        "if_condition": r"[Ii]f .+?,",
        "while_condition": r"[Ww]hile .+?,",
        "banish": r"[Bb]anish",
        "ready": r"[Rr]eady",
        "exert": r"[Ee]xert",
    }

    for text in body_texts:
        if not text:
            continue

        for pattern_name, pattern in patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                pattern_counts[pattern_name] = pattern_counts.get(pattern_name, 0) + 1

    return pattern_counts

def main():
    """Main function to parse all card abilities."""
    # Load card data
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    json_File = os.path.join(parent_dir, "lorcana_cards_simplified.json")
    utility_Script_dir = os.path.join(parent_dir,"Utility Scripts","bodytext.json")
    
    cards = load_cards(json_File)
    print(f"Loaded {len(cards)} cards")

    # Load unique body texts
    body_texts = load_body_texts(utility_Script_dir)
    print(f"Loaded {len(body_texts)} unique body texts")

    # Analyze body texts
    pattern_counts = analyze_body_texts(body_texts)
    print("\nBody Text Pattern Analysis:")
    for pattern, count in sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"{pattern}: {count}")

    # Parse abilities for all cards
    card_abilities = parse_card_abilities(cards)
    print(f"\nParsed abilities for {len(card_abilities)} cards")

    # Count cards with parsed abilities
    cards_with_abilities = sum(1 for abilities in card_abilities.values() if abilities)
    print(f"Cards with at least one parsed ability: {cards_with_abilities}")

    # Sample output for a few cards
    print("\nSample Ability Parsing Results:")
    sample_count = 0
    for card_id, abilities in card_abilities.items():
        if abilities and sample_count < 5:
            card_name = next((card["Name"] for card in cards if card["Unique_ID"] == card_id), "Unknown")
            print(f"\n{card_name} ({card_id}):")
            for ability in abilities:
                print(f"  {ability}")
            sample_count += 1

if __name__ == "__main__":
    main()
