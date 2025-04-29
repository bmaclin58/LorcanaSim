import json
import os
import re

import unicodedata

# Get the parent directory of the script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)  # This goes up one level to the parent directory

# Define the file paths using the parent directory
input_file = os.path.join(parent_dir, "lorcana_cards.json")
output_file = os.path.join(parent_dir, "lorcana_cards_simplified.json")


def clean_body_text(text):
    if not text:
        return text

    text = re.sub(r"(?mi)^[ \t]*Shift\s+\d+\s*(?:\r?\n)?", "", text)

    # 1) Remove any line that starts with one of these keywords + parentheses
    keyword_pattern = (
        r"(?:Evasive|Bodyguard|Rush|Ward|Vanish|Support|"
        r"Challenger \+\d+|Resist \+\d+|Singer \d+|Shift \d+|Reckless|Universal Shift \d+|Sing Together \d+)"
    )
    text = re.sub(rf"(?mi)^[ \t]*{keyword_pattern}\s*\([^)]*\)\s*(?:\r?\n)?", "", text)

    # 2) Strip off any "Label: " at the start of a line
    text = re.sub(r"(?m)^[ \t]*[^:\n]+:\s*", "", text)

    # 3) Strip off any ALL-CAPS prefix before a dash
    text = re.sub(r"(?m)^[ \t]*(?:[A-Z0-9 ']+)[-–]\s*", "", text)

    # 4) Collapse multiple blank lines
    text = re.sub(r"\n{2,}", "\n", text)

    # 5) Merge all remaining line-breaks into spaces
    text = re.sub(r"\s*\r?\n\s*", " ", text)

    # 6) Remove **all** parenthetical text
    text = re.sub(r"\s*\([^)]*\)", "", text)

    # 7) Remove any leading ALL-CAPS phrase (words/spaces/digits/apostrophes)
    text = re.sub(r"^(?:\s*\b[A-Z0-9']+\b\s*)+", "", text)

    # 8) Normalize Unicode punctuation → ASCII
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"[‘’]", "'", text)
    text = re.sub(r"[“”]", '"', text)
    text = text.encode("ascii", "ignore").decode("ascii")

    # 9) Your symbol replacements
    text = re.sub(r"{i}", "ink", text)
    text = re.sub(r"{w}", " willpower", text)
    text = re.sub(r"{s}", " strength", text)
    text = re.sub(r"{l}", " lore", text)
    text = re.sub(r"{e}", " exert", text)
    text = re.sub(r"^[?]+\s*", "", text)

    return text.strip()

def create_smaller_json(input_file, output_file):
	try:
		print(f"Attempting to open file at: {input_file}")
		with open(input_file, 'r', encoding='utf-8') as f:
			data = json.load(f)

		# Check if the data is an array directly or nested under a key
		if isinstance(data, list):
			cards = data
		elif isinstance(data, dict) and 'cards' in data:
			cards = data['cards']
		else:
			print(f"Unexpected JSON structure in {input_file}")
			return False

		# Create new list with only the specified fields
		simplified_cards = []
		for card in cards:
			# Clean the Body_Text field
			body_text = card.get("Body_Text")
			cleaned_body_text = clean_body_text(body_text)

			simplified_card = {
					"Name":      card.get("Name"),
					"Color":     card.get("Color"),
					"Cost":      card.get("Cost"),
					"Inkable":   card.get("Inkable"),
					"Type":      card.get("Type"),
					"Unique_ID": card.get("Unique_ID"),
					"Body_Text": cleaned_body_text,
					"Abilities": card.get("Abilities"),
					"Willpower": card.get("Willpower"),
					"Move Cost": card.get("Move Cost"),
					"Strength":  card.get("Strength"),
					"Lore":      card.get("Lore"),
			}
			simplified_cards.append(simplified_card)

		# Write the simplified data to a new file
		with open(output_file, 'w', encoding='utf-8') as f:
			json.dump(simplified_cards, f, indent=2)

		print(f"Successfully created {output_file} with {len(simplified_cards)} cards")
		return True

	except Exception as e:
		print(f"Error processing JSON file: {e}")
		# Print more detailed information for debugging
		import traceback
		traceback.print_exc()
		return False


# Example usage
if __name__ == "__main__":
	# Check if the file exists at the expected location
	if not os.path.exists(input_file):
		print(f"File not found at {input_file}")
		user_input = input("Please enter the full path to lorcana_cards.json: ")
		if user_input:
			input_file = user_input
			# Update output file to be in the same directory
			output_dir = os.path.dirname(input_file)
			output_file = os.path.join(output_dir, "lorcana_cards_simplified.json")

	create_smaller_json(input_file, output_file)
