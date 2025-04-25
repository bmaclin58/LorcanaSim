import json
import os
import re
from CardEffects.TextPatterns import PATTERNS, EFFECT_PATTERNS, KEYWORD_PATTERNS


def load_cards(json_file_path):
	"""Load the cards from the JSON file."""
	with open(json_file_path, 'r', encoding='utf-8') as file:
		return json.load(file)


def check_for_pattern_matches(body_text, patterns_list):
	"""Check if the body text matches any pattern in the given patterns list."""
	if not body_text:
		return False

	for pattern_info in patterns_list:
		regex = pattern_info['regex']
		match = regex.search(body_text)
		if match:
			return True
	return False


def find_cards_without_pattern_matches(cards):
	"""Find cards whose Body_Text doesn't match any patterns."""
	no_matches = []

	for card in cards:
		body_text = card.get("Body_Text")
		if not body_text:
			continue  # Skip cards with no body text

		# Check if body text matches any patterns
		trigger_match = check_for_pattern_matches(body_text, PATTERNS)
		effect_match = check_for_pattern_matches(body_text, EFFECT_PATTERNS)

		# If the body text doesn't match any patterns, add to the list
		if not (trigger_match or effect_match):
			# Check for keyword matches in the Abilities field if it exists
			abilities = card.get("Abilities")
			keyword_match = False

			if abilities:
				# If Abilities is a string, split it by commas
				if isinstance(abilities, str):
					ability_list = [a.strip() for a in abilities.split(',')]
					for ability in ability_list:
						if check_for_pattern_matches(ability, KEYWORD_PATTERNS):
							keyword_match = True
							break

			# If no matches in either Body_Text or Abilities, add to no_matches list
			if not keyword_match:
				no_matches.append(card)

	return no_matches


def main():
	"""Main function to run the analysis."""

	# Get the parent directory of the script's directory
	script_dir = os.path.dirname(os.path.abspath(__file__))
	parent_dir = os.path.dirname(script_dir)  # This goes up one level to the parent directory

	# Define the file paths using the parent directory
	json_file_path = os.path.join(parent_dir, "lorcana_cards_simplified.json")
	cards = load_cards(json_file_path)

	print(f"Loaded {len(cards)} cards from the JSON file.")

	no_matches = find_cards_without_pattern_matches(cards)

	print(f"\nFound {len(no_matches)} cards without pattern matches:")
	for card in no_matches:
		print(f"\nName: {card.get('Name')}")
		print(f"Unique_ID: {card.get('Unique_ID')}")
		print(f"Type: {card.get('Type')}")
		print(f"Body_Text: {card.get('Body_Text')}")
		print(f"Abilities: {card.get('Abilities')}")


if __name__ == "__main__":
	main()
