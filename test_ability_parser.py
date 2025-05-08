import json
from card import Card, parse_card_data

def main():
    """Test the ability parser integration with the Card class."""
    print("Testing Ability Parser Integration")
    print("=================================")
    
    # Load card data
    with open("lorcana_cards_simplified.json", "r", encoding="utf-8") as f:
        card_data = json.load(f)
    
    print(f"Loaded {len(card_data)} cards from lorcana_cards_simplified.json")
    
    # Parse cards with lazy ability parsing
    cards_by_id, cards_by_name, _ = parse_card_data(card_data, parse_abilities_now=False)
    print(f"Parsed {len(cards_by_id)} cards (lazy ability parsing)")
    
    # Test with a few sample cards
    sample_card_ids = ["TFC-001", "TFC-010", "TFC-020", "TFC-050", "TFC-100"]
    
    print("\nSample Card Abilities:")
    print("---------------------")
    
    for card_id in sample_card_ids:
        if card_id in cards_by_id:
            card = cards_by_id[card_id]
            print(f"\n{card.name} ({card_id}):")
            print(f"Body Text: {card.body_text}")
            print(f"Abilities: {', '.join(card.abilities) if card.abilities else 'None'}")
            
            # Get parsed abilities (this will trigger parsing if not done yet)
            abilities = card.get_abilities()
            
            if abilities:
                print("Parsed Abilities:")
                for i, ability in enumerate(abilities, 1):
                    print(f"  {i}. {ability}")
            else:
                print("No parsed abilities")
        else:
            print(f"\nCard ID {card_id} not found")
    
    # Test with a card that has complex abilities
    print("\nTesting a card with complex abilities:")
    print("------------------------------------")
    
    # Find a card with "At the start of your turn" ability
    start_turn_cards = []
    for card in cards_by_id.values():
        if card.body_text and "At the start of your turn" in card.body_text:
            start_turn_cards.append(card)
    
    if start_turn_cards:
        card = start_turn_cards[0]
        print(f"\n{card.name} ({card.unique_id}):")
        print(f"Body Text: {card.body_text}")
        print(f"Abilities: {', '.join(card.abilities) if card.abilities else 'None'}")
        
        # Get parsed abilities
        abilities = card.get_abilities()
        
        if abilities:
            print("Parsed Abilities:")
            for i, ability in enumerate(abilities, 1):
                print(f"  {i}. {ability}")
                # Print effects for this ability
                for j, effect in enumerate(ability.effects, 1):
                    print(f"    - Effect {j}: {effect}")
        else:
            print("No parsed abilities")
    
    # Test with a card that has keyword abilities
    print("\nTesting a card with keyword abilities:")
    print("-----------------------------------")
    
    # Find a card with Rush keyword
    rush_cards = []
    for card in cards_by_id.values():
        if card.abilities and any("Rush" in ability for ability in card.abilities):
            rush_cards.append(card)
    
    if rush_cards:
        card = rush_cards[0]
        print(f"\n{card.name} ({card.unique_id}):")
        print(f"Body Text: {card.body_text}")
        print(f"Abilities: {', '.join(card.abilities) if card.abilities else 'None'}")
        
        # Get parsed abilities
        abilities = card.get_abilities()
        
        if abilities:
            print("Parsed Abilities:")
            for i, ability in enumerate(abilities, 1):
                print(f"  {i}. {ability}")
                # Print effects for this ability
                for j, effect in enumerate(ability.effects, 1):
                    print(f"    - Effect {j}: {effect}")
        else:
            print("No parsed abilities")

if __name__ == "__main__":
    main()
