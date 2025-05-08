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
output_file = os.path.join(script_dir, "StartingText.json")


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
	
	simplified_cards = []
	activation_count = 0
	unique_Word_Count = {}
	unique_Keyword_Collection = {}
	
	for card in cards:
		# Clean the Body_Text field
		bodyText = card.get("Body_Text")
		bodyTextFull = bodyText
		if bodyText:  # Ensure bodyText is not None or empty
			if ":" in bodyText:
				activation = re.search(":", bodyText)
				activation = activation.start() + 1
				bodyText = bodyText[:activation]
				activation_count += 1
			
			elif " " in bodyText:
				matches = list(re.finditer(" ", bodyText))
				activation = matches[1].start()
				uniqueWordIndex = matches[0].start()
				bodyText = bodyText[:activation]
				eachKeyword = bodyText[:uniqueWordIndex]
				
				if eachKeyword in unique_Word_Count:
					unique_Word_Count[eachKeyword] += 1
				else:
					unique_Word_Count[eachKeyword] = 1
				
				if eachKeyword in unique_Keyword_Collection:
					unique_Keyword_Collection[eachKeyword].append(bodyTextFull)
				else:
					unique_Keyword_Collection[eachKeyword] = [bodyTextFull]
			
			else:
				bodyText = ""
		else:
			bodyText = ""  # Default to an empty string if Body_Text is None or empty
	
		simplified_card = {
			# "Unique_ID": card.get("Unique_ID"),
			"Body_Text": bodyText,
			# "Abilities": card.get("Abilities"),
			}
		simplified_cards.append(simplified_card)

	simplified_cards.sort(key = lambda x: x["Body_Text"])
	# Write the simplified data to a new file
	unique_cards = list({c["Body_Text"]: c for c in simplified_cards}.values())
	
	unique_Word_Count = dict(sorted(unique_Word_Count.items(), key = lambda item: item[1], reverse = True))
	
	unique_Keyword_Collection = dict(
			sorted(
					{key: sorted(set(value)) for key, value in unique_Keyword_Collection.items()}.items()
					)
			)
	
	for key, value in unique_Word_Count.items():
		print(f"{key}: {value}")

	with open("KeywordCollection.JSON", "w", encoding = "utf-8") as f:
		json.dump(unique_Keyword_Collection, f, indent = 2)
		
	with open(output_file, "w", encoding = "utf-8") as f:
		json.dump(unique_cards, f, indent = 2)
	
	print(f"Successfully created {output_file} with {len(unique_cards)} cards")

# Example usage
if __name__ == "__main__":
	create_smaller_json(input_file, output_file)
