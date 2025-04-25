import json
import os
import re

# Get the parent directory of the script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)  # This goes up one level to the parent directory

# Define the file paths using the parent directory
output_file = os.path.join(parent_dir, "lorcana_cards_simplified.json")

# Read the JSON file
with open(output_file, 'r', encoding='utf-8') as f:
	cards = json.load(f)

# Get the keywords from KEYWORD_MAP
keywords_in_map = [
		"Bodyguard", "Evasive", "Reckless", "Rush", "Support", "Ward", "Vanish",
		"Challenger", "Resist", "Shift", "Singer", "Sing Together"
]


# Function to find keywords in the body text
def extract_keywords(text):
	if not text:
		return []

	# Create a regex pattern to find keywords (standalone words that match our keywords)
	# This will find keywords like "Shift", "Challenger 2", "Resist 1", etc.
	keyword_pattern = r'\b(' + '|'.join(re.escape(kw) for kw in keywords_in_map) + r')(?:\s+\d+)?\b'

	# Also look for any capitalized words that might be keywords
	potential_keyword_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+\d+)?\b'

	# Find all matches
	known_keywords = set(re.findall(keyword_pattern, text))
	potential_keywords = set(re.findall(potential_keyword_pattern, text))

	# Remove known keywords from potential keywords
	for kw in known_keywords:
		base_kw = kw.split()[0]  # Get base keyword without number
		potential_keywords = {pk for pk in potential_keywords if base_kw not in pk}

	return list(known_keywords), list(potential_keywords)


# Collect all keywords and potential keywords
all_known_keywords = set()
all_potential_keywords = set()

# Process each card
for card in cards:
	if card["Body_Text"]:
		known_kws, potential_kws = extract_keywords(card["Body_Text"])

		# Clean up keywords (remove numbers, etc.)
		known_kws = [kw.split()[0] for kw in known_kws]  # Get base keyword without number

		all_known_keywords.update(known_kws)
		all_potential_keywords.update(potential_kws)

# Find potential keywords that are not in our known keywords list
not_in_keyword_map = set()
for kw in all_potential_keywords:
	base_kw = kw.split()[0]  # Get base keyword without number
	if base_kw not in keywords_in_map and kw not in keywords_in_map:
		not_in_keyword_map.add(kw)

print(f"All known keywords found in card texts: {sorted(all_known_keywords)}")
print(f"\nKeywords in KEYWORD_MAP but not found in card texts: {sorted(set(keywords_in_map) - all_known_keywords)}")
print(f"\nPotential keywords not in KEYWORD_MAP: {sorted(not_in_keyword_map)}")

# Also check the Abilities field
abilities_in_cards = set()
for card in cards:
	if card["Abilities"] and card["Abilities"] not in [None, "null"]:
		# Split abilities by comma if it's a string
		if isinstance(card["Abilities"], str):
			card_abilities = [ability.strip() for ability in card["Abilities"].split(',')]
			abilities_in_cards.update(card_abilities)
		elif isinstance(card["Abilities"], list):
			abilities_in_cards.update(card["Abilities"])

print(f"\nAbilities explicitly listed in the Abilities field: {sorted(abilities_in_cards)}")

# Check for abilities in the Abilities field that are not in KEYWORD_MAP
abilities_not_in_map = set()
for ability in abilities_in_cards:
	base_ability = ability.split()[0]  # Get base ability without number
	if base_ability not in keywords_in_map and ability not in keywords_in_map:
		abilities_not_in_map.add(ability)

print(f"\nAbilities in the Abilities field not in KEYWORD_MAP: {sorted(abilities_not_in_map)}")
