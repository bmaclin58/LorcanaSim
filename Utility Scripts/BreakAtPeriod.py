import json
import os
import re

# Get the parent directory of the script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(
		script_dir,
		)  # This goes up one level to the parent directory

# Define the file paths using the parent directory
input_file = os.path.join(parent_dir, "lorcana_cards_simplified.json")
output_file = os.path.join(script_dir, "Keyword With Breakpoint.json")


def create_smaller_json (input_file, output_file):
	print(f"Attempting to open file at: {input_file}")
	with open(input_file, "r", encoding = "utf-8") as f:
		data = json.load(f)
	# Check if the data is an array directly or nested under a key
	if isinstance(data, list):
		cards = data
	elif isinstance(data, dict) and "cards" in data:
		cards = data["cards"]
	else:
		print(f"Unexpected JSON structure in {input_file}")
		return False
	
	unique_Keyword_Collection = {}
	
	for card in cards:
		# Clean the Body_Text field
		bodyText = card.get("Body_Text")
		if bodyText:
			bodyText = bodyText.split(".")
		else:
			bodyText = []
		for text in bodyText:
			text = text.strip()
			if text:  # Ensure bodyText is not None or empty
				if ":" in text:
					activationIndex = re.search(":", text)
					activationIndex = activationIndex.start() + 1
					uniqueText = text[:activationIndex]
					
					if uniqueText in unique_Keyword_Collection:
						unique_Keyword_Collection[uniqueText].append(text)
					else:
						unique_Keyword_Collection[uniqueText] = [text]
						
				elif " " in text:
					matches = list(re.finditer(" ", text))
					# Change if you want 1 word or 2+
					uniqueWordIndex = matches[1].start()
					eachKeyword = text[:uniqueWordIndex]
					
					if eachKeyword in unique_Keyword_Collection:
						unique_Keyword_Collection[eachKeyword].append(text)
					else:
						unique_Keyword_Collection[eachKeyword] = [text]
				
				else:
					text = ""
			else:
				text = ""  # Default to an empty string if Body_Text is None or empty
	
	unique_Keyword_Collection = dict(
			sorted(
					{key: sorted(set(value)) for key, value in unique_Keyword_Collection.items()}.items()
					)
			)

	with open(output_file, "w", encoding = "utf-8") as f:
		json.dump(unique_Keyword_Collection, f, indent = 2)


# Example usage
if __name__ == "__main__":
	create_smaller_json(input_file, output_file)
