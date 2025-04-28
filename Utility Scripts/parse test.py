import json
import os
import sys
import re
from CardEffects.ability_parser import parse_keyword


def extract_keywords_from_text(text):
	"""Extract potential keywords from card text."""
	if not text:
		return []

	# Split by newlines and look for potential keyword phrases
	lines = text.split('\n')
	keywords = []

	for line in lines:
		# Look for keyword-like patterns (words before a dash or colon)
		keyword_match = re.match(r'^([^-:]+)[-:]', line)
		if keyword_match:
			potential_keyword = keyword_match.group(1).strip()
			keywords.append(potential_keyword)

		# Also check for standalone keywords that might appear in the text
		standalone_keywords = ["Challenger", "Resist", "Shift", "Singer",
		                       "Sing Together", "Bodyguard", "Evasive",
		                       "Reckless", "Rush", "Support", "Vanish", "Ward"]

		for keyword in standalone_keywords:
			if re.search(rf'\b{keyword}\b', line, re.IGNORECASE):
				# Look for patterns like "Challenger +2" or "Shift 3"
				keyword_with_value = re.search(rf'\b{keyword}\s+\+?\d+\b', line, re.IGNORECASE)
				if keyword_with_value:
					keywords.append(keyword_with_value.group(0))
				else:
					keywords.append(keyword)

	return keywords


def main():
	# Get the parent directory of the script's directory
	script_dir = os.path.dirname(os.path.abspath(__file__))
	parent_dir = os.path.dirname(script_dir)

	# Define the file paths using the parent directory
	json_file = os.path.join(parent_dir, "lorcana_cards_simplified.json")

	# Try to load the JSON file
	with open(json_file, 'r', encoding='utf-8') as f:
		cards = json.load(f)


	print(f"Analyzing keywords in {len(cards)} cards...")

	for card in cards:
		card_name = card.get("Name", "Unknown Card")
		body_text = card.get("Body_Text", "")

		print(f"\n----- {card_name} -----")
		print(f"Body Text: {body_text}")

		# Extract potential keywords
		potential_keywords = extract_keywords_from_text(body_text)

		if potential_keywords:
			print("Potential Keywords Found:")
			for keyword_text in potential_keywords:
				print(f"  - {keyword_text}")

				# Try to parse with the parse_keyword function
				parsed = parse_keyword(keyword_text)
				if parsed:
					print(f"    Parsed: {parsed}")
				else:
					print(f"    Not recognized as a keyword by parse_keyword")
		else:
			print("No potential keywords found")


if __name__ == "__main__":
	main()
