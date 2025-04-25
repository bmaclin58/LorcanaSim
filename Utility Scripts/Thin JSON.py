import json
import os
import re

# Get the parent directory of the script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)  # This goes up one level to the parent directory

# Define the file paths using the parent directory
input_file = os.path.join(parent_dir, "lorcana_cards.json")
output_file = os.path.join(parent_dir, "lorcana_cards_simplified.json")


def clean_body_text(text):
	if not text:
		return text

	# Remove text between parentheses
	text = re.sub(r'\([^)]*\)', '', text)

	# Specific pattern for abilities followed by a colon
	# Match a word or phrase at the start of a line or after a newline, followed by a colon and whitespace
	text = re.sub(r'(^|\n)([^:\n]+):\s*', r'\1', text)

	# Specific pattern for abilities followed by a dash
	# Match a word or phrase at the start of a line or after a newline, followed by a dash and whitespace
	text = re.sub(r'(^|\n)([^-\n]+)-\s*', r'\1', text)

	# Replace patterns like "Trapped! " at the start of a line or after newline
	text = re.sub(r'(^|\n)(\w+)!\s*', r'\1', text)

	# Remove any redundant newlines that might have been created
	text = re.sub(r'\n\s*\n', '\n', text)

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
