import json
import os
import re
from typing import List, Dict, Any, Optional

# Using your existing PATTERNS list from the code you shared
PATTERNS = [
    # Activated Abilities
    {
        "regex": re.compile(
            r"^(?P<cost_text>.*?)-\s*(?P<effect_text>.*)", re.IGNORECASE | re.DOTALL
        ),
        "trigger": "ACTIVATED",
        "has_cost": True,
    },
    # Triggered Abilities
    {
        "regex": re.compile(
            r"^When you play this character,?\s*(?P<effect_text>.*)",
            re.IGNORECASE | re.DOTALL,
        ),
        "trigger": "ON_PLAY",
        "has_cost": False,
    },
    {
        "regex": re.compile(
            r"^Whenever this character quests,?\s*(?P<effect_text>.*)",
            re.IGNORECASE | re.DOTALL,
        ),
        "trigger": "ON_QUEST",
        "has_cost": False,
    },
    {
        "regex": re.compile(
            r"^Whenever this character challenges another character,?\s*(?P<effect_text>.*)",
            re.IGNORECASE | re.DOTALL,
        ),
        "trigger": "ON_CHALLENGE",
        "has_cost": False,
    },
    {
        "regex": re.compile(
            r"^Whenever this character is challenged,?\s*(?P<effect_text>.*)",
            re.IGNORECASE | re.DOTALL,
        ),
        "trigger": "ON_BEING_CHALLENGED",
        "has_cost": False,
    },
    {
        "regex": re.compile(
            r"^When this character is banished,?\s*(?P<effect_text>.*)",
            re.IGNORECASE | re.DOTALL,
        ),
        "trigger": "ON_BANISH",
        "has_cost": False,
    },
    {
        "regex": re.compile(
            r"^Whenever one of your other characters is banished,?\s*(?P<effect_text>.*)",
            re.IGNORECASE | re.DOTALL,
        ),
        "trigger": "ON_CHARACTER_LEAVES_PLAY",
        "has_cost": False,
        "parameters": {"filter": "own_other_banished"},
    },
    {
        "regex": re.compile(
            r"^At the start of your turn,?\s*(?P<effect_text>.*)",
            re.IGNORECASE | re.DOTALL,
        ),
        "trigger": "START_OF_TURN",
        "has_cost": False,
    },
    {
        "regex": re.compile(
            r"^At the end of your turn,?\s*(?P<effect_text>.*)",
            re.IGNORECASE | re.DOTALL,
        ),
        "trigger": "END_OF_TURN",
        "has_cost": False,
    },
    {
        "regex": re.compile(
            r"^Whenever this character sings a song,?\s*(?P<effect_text>.*)",
            re.IGNORECASE | re.DOTALL,
        ),
        "trigger": "ON_SING",
        "has_cost": False,
    },
    {
        "regex": re.compile(
            r"^During your turn,?\s*(?P<effect_text>.*)", re.IGNORECASE | re.DOTALL
        ),
        "trigger": "ON_YOUR_TURN",
        "has_cost": False,
    },
    {
        "regex": re.compile(
            r"^While this character is at a location,?\s*(?P<effect_text>.*)",
            re.IGNORECASE | re.DOTALL,
        ),
        "trigger": "WHILE_AT_LOCATION",
        "has_cost": False,
    },
    {
        "regex": re.compile(
            r"^Once per turn, when this character moves to a location,?\s*(?P<effect_text>.*)",
            re.IGNORECASE | re.DOTALL,
        ),
        "trigger": "ON_MOVE_TO_LOCATION",
        "has_cost": False,
    },
    {
        "regex": re.compile(
            r"^Whenever this character moves to a location,,?\s*(?P<effect_text>.*)",
            re.IGNORECASE | re.DOTALL,
        ),
        "trigger": "ON_MOVE_TO_LOCATION",
        "has_cost": False,
    },
    # Standalone keywords and multiple keywords
    {
        "regex": re.compile(
            r"^(Evasive|Bodyguard|Rush|Ward|Vanish|Support|Challenger \+\d+|Resist \+\d+|Singer \d+|Shift \d+|Reckless)$",
            re.IGNORECASE | re.DOTALL,
        ),
        "trigger": "KEYWORD_ONLY",
        "has_cost": False,
    },
    {
        "regex": re.compile(
            r"^(?P<keyword1>Evasive|Bodyguard|Rush|Ward|Vanish|Support|Challenger \+\d+|Resist \+\d+|Singer \d+|Shift \d+|Reckless)\s+(?P<keyword2>Evasive|Bodyguard|Rush|Ward|Vanish|Support|Challenger \+\d+|Resist \+\d+|Singer \d+|Shift \d+|Reckless)",
            re.IGNORECASE | re.DOTALL,
        ),
        "trigger": "MULTIPLE_KEYWORDS",
        "has_cost": False,
    },
    # Stats bonus patterns
    {
        "regex": re.compile(
            r"^Your other characters get \+\d+\s+(?P<stat>\w+)\.",
            re.IGNORECASE | re.DOTALL,
        ),
        "trigger": "STATIC_BONUS",
        "has_cost": False,
    },
    {
        "regex": re.compile(
            r"^This character gets \+\d+\s+(?P<stat>\w+)(\s+(this turn|until the start of your next turn))?.",
            re.IGNORECASE | re.DOTALL,
        ),
        "trigger": "SELF_BONUS",
        "has_cost": False,
    },
    # Protection patterns
    {
        "regex": re.compile(
            r"^This character can't be challenged\.", re.IGNORECASE | re.DOTALL
        ),
        "trigger": "PROTECTION_CHALLENGE",
        "has_cost": False,
    },
    # Conditional patterns
    {
        "regex": re.compile(
            r"^(If|While) you have (?P<condition>.*?),\s*(?P<effect_text>.*)",
            re.IGNORECASE | re.DOTALL,
        ),
        "trigger": "CONDITIONAL",
        "has_cost": False,
    },
    # On ready trigger
    {
        "regex": re.compile(
            r"^Whenever you ready this character,\s*(?P<effect_text>.*)",
            re.IGNORECASE | re.DOTALL,
        ),
        "trigger": "ON_READY",
        "has_cost": False,
    },
    # Enters play effect
    {
        "regex": re.compile(
            r"^This character enters play (?P<effect_text>.*)",
            re.IGNORECASE | re.DOTALL,
        ),
        "trigger": "ENTERS_PLAY_EFFECT",
        "has_cost": False,
    },
    # General whenever triggers
    {
        "regex": re.compile(
            r"^Whenever (?P<trigger>one of your (other )?(characters|Hyena characters|Racer characters|Madrigal characters) (is banished|challenges|sings a song|quests)|you play (a character|an action|a Floodborn character|another character)|one of your characters (sings a song|challenges|is banished|quests)),\s*(?P<effect_text>.*)",
            re.IGNORECASE | re.DOTALL,
        ),
        "trigger": "GENERAL_WHENEVER",
        "has_cost": False,
    },
    # Cost reduction pattern
    {
        "regex": re.compile(
            r"^For each (?P<condition>.*?), you pay (?P<amount>\d+)\s*\{[a-z]\} less to play this character\.",
            re.IGNORECASE | re.DOTALL,
        ),
        "trigger": "COST_REDUCTION",
        "has_cost": False,
    },
    # Self conditional
    {
        "regex": re.compile(
            r"^While this character (?P<condition>.*?), (?P<effect_text>.*)",
            re.IGNORECASE | re.DOTALL,
        ),
        "trigger": "SELF_CONDITIONAL",
        "has_cost": False,
    },
    # Stat value pattern (just numerical values like "3 strength until the start of your next turn.")
    {
        "regex": re.compile(
            r"^(?P<amount>\d+)\s+(?P<stat>\w+)(\s+(this turn|until the start of your next turn))?.",
            re.IGNORECASE | re.DOTALL,
        ),
        "trigger": "STAT_VALUE",
        "has_cost": False,
    },
    # Character type interactions
    {
        "regex": re.compile(
            r"^Your (?P<character_type>\w+) characters (get|gain|gets|gains) (?P<effect>.*)",
            re.IGNORECASE | re.DOTALL,
        ),
        "trigger": "CHARACTER_TYPE_EFFECT",
        "has_cost": False,
    },
    # During your turn/opponent's turn
    {
        "regex": re.compile(
            r"^During (your|an opponent's) turn,\s*(?P<effect_text>.*)",
            re.IGNORECASE | re.DOTALL,
        ),
        "trigger": "DURING_TURN",
        "has_cost": False,
    },
    # Once during your turn
    {
        "regex": re.compile(
            r"^Once during your turn, (?P<effect_text>.*)", re.IGNORECASE | re.DOTALL
        ),
        "trigger": "ONCE_PER_TURN",
        "has_cost": False,
    },
    # Opponents need X lore
    {
        "regex": re.compile(
            r"^Opponents need \d+ lore to win the game\.", re.IGNORECASE | re.DOTALL
        ),
        "trigger": "WIN_CONDITION_MODIFIER",
        "has_cost": False,
    },
    # Action cards
    {
        "regex": re.compile(r"^(?P<effect_text>.*?)\.", re.IGNORECASE | re.DOTALL),
        "trigger": "ACTION_EFFECT",
        "has_cost": False,
    },
    # Passive/Continuous (catch-all pattern)
    {
        "regex": re.compile(r"^(?P<effect_text>.*)"),
        "trigger": "CONTINUOUS",
        "has_cost": False,
    },
    # For specific keyword format like "Challenger+2" (no space after keyword)
    {
        "regex": re.compile(
            r"^(?P<keyword>Challenger|Resist)\+(?P<value>\d+)$",
            re.IGNORECASE | re.DOTALL,
        ),
        "trigger": "KEYWORD_WITH_VALUE_NO_SPACE",
        "has_cost": False,
    },
    # For multiple keywords with different formatting (including newline)
    {
        "regex": re.compile(
            r"^(?P<keyword1>Bodyguard|Shift \d+|Resist \+\d+)\\n(?P<keyword2>Resist \+\d+|Shift \d+|Bodyguard)$",
            re.IGNORECASE | re.DOTALL,
        ),
        "trigger": "MULTIPLE_KEYWORDS_WITH_NEWLINE",
        "has_cost": False,
    },
    # For multiple keywords with different spacing patterns
    {
        "regex": re.compile(
            r"^(?P<keyword1>Shift \d+|Resist \+\d+)\s+(?P<keyword2>Resist \+\d+|Shift \d+)$",
            re.IGNORECASE | re.DOTALL,
        ),
        "trigger": "MULTIPLE_KEYWORDS_WITH_SPACE",
        "has_cost": False,
    },
    # For action cards with simple effects
    {
        "regex": re.compile(
            r"^(Deal \d+ damage to chosen (character|location)|Remove up to \d+ damage from chosen (character|location)|Draw \d+ Cards|Banish chosen character|Chosen exerted character can't ready at the start of their next turn)$",
            re.IGNORECASE | re.DOTALL,
        ),
        "trigger": "SIMPLE_ACTION_EFFECT",
        "has_cost": False,
    },
    # For "Support" followed by an effect
    {
        "regex": re.compile(
            r"^Support\s+(?P<effect_text>Your other characters with Support get \+\d+\s+\w+)$",
            re.IGNORECASE | re.DOTALL,
        ),
        "trigger": "SUPPORT_WITH_EFFECT",
        "has_cost": False,
    },
    # For "Discard X cards" effect
    {
        "regex": re.compile(r"^Discard \d+ cards$", re.IGNORECASE | re.DOTALL),
        "trigger": "DISCARD_EFFECT",
        "has_cost": False,
    },
    # For "Your characters named X gain/get Y" pattern
    {
        "regex": re.compile(
            r"^Your characters named (?P<character_name>\w+) (gain|get) (?P<effect>.*?)$",
            re.IGNORECASE | re.DOTALL,
        ),
        "trigger": "NAMED_CHARACTER_EFFECT",
        "has_cost": False,
    },
    # For stat bonuses based on other characters
    {
        "regex": re.compile(
            r"^(?P<keyword>Resist \+\d+)\s+This character gets \+\d+ \w+ for each other character named (?P<character_name>.*?) you have in play$",
            re.IGNORECASE | re.DOTALL,
        ),
        "trigger": "STAT_BONUS_BY_CHARACTER_COUNT",
        "has_cost": False,
    },
]


def find_unmatched_entries(json_file_path: str) -> List[Dict[str, Any]]:
	"""
	Find entries in the JSON file where Body_Text doesn't match any pattern.

	Args:
		json_file_path: Path to the JSON file containing card data

	Returns:
		List of entries (dictionaries) with no pattern matches
	"""
	# Get the parent directory of the script's directory
	script_dir = os.path.dirname(os.path.abspath(__file__))
	parent_dir = os.path.dirname(script_dir)  # This goes up one level to the parent directory

	# Define the file paths using the parent directory
	json_file_path = os.path.join(parent_dir, "lorcana_cards_simplified.json")
	# Load the JSON file
	with open(json_file_path, 'r', encoding='utf-8') as f:
		cards_data = json.load(f)

	# List to store entries with no pattern matches
	unmatched_entries = []

	# Check each entry
	for card in cards_data:
		# Skip entries with null Body_Text
		if card.get('Body_Text') is None:
			continue

		body_text = card['Body_Text']

		# The catch-all pattern should match everything, so we need to check if ANY
		# pattern other than the last one (catch-all) matches
		matched = False

		# Skip the last pattern (catch-all) for matching check
		for pattern_info in PATTERNS[:-1]:
			if pattern_info['regex'].match(body_text):
				matched = True
				break

		# If no patterns matched (except potentially the catch-all), add to unmatched list
		if not matched:
			unmatched_entries.append(card)

	return unmatched_entries


def main():
	# File path
	json_file_path = 'lorcana_cards_simplified.json'

	# Find unmatched entries
	unmatched = find_unmatched_entries(json_file_path)

	# Print the results
	print(f"Found {len(unmatched)} entries with no pattern matches:")
	for card in unmatched:
		print(f"Name: {card['Name']}")
		print(f"Unique_ID: {card['Unique_ID']}")
		print(f"Body_Text: {card['Body_Text']}")
		print("-" * 50)

	# Optionally, save to a new JSON file
	with open('unmatched_entries.json', 'w', encoding='utf-8') as f:
		json.dump(unmatched, f, indent=2)

	print(f"Unmatched entries saved to 'unmatched_entries.json'")


if __name__ == "__main__":
	main()
