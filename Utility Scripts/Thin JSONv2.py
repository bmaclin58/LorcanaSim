import json
import os
import re

import unicodedata

# Get the parent directory of the script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)  # This goes up one level to the parent directory

# Define the file paths using the parent directory
input_file = os.path.join(parent_dir, "lorcana_cards.json")
output_file = os.path.join(parent_dir, "lorcana_cards_simplified2.json")


def clean_body_text(text, classifications):
    if not text:
        return text
    
    
    
    # List of keywords to look for (with space after each word)
    keywords = [
        "At the end ",
        "At the start ",
        "Banish ",
        "Banish chosen ",
        "Characters ",
        "Choose ",
        "Chosen ",
        "Count the number ",
        "Damaged characters ",
        "Deal damage ",
        "During an ",
        "During your ",
        "During each ",
        "During opponent ",
        "During your ",
        "Each Opponent ",
        "Each player ",
        "Exert ",
        "For each ",
        "If an ",
        "If chosen ",
        "If you have ",
        "Look at the top ",
        "Move a ",
        "Move up to ",
        "Name a card ",
        "Once during your",
        "Once per turn",
        "Opponents ",
        "Opposing ",
        "Play a ",
        "Ready all ",
        "Ready chosen ",
        "Remove up to ",
        "Return ",
        "Reveal the top ",
        "Search your ",
        "Shuffle ",
        "This character ",
        "This item ",
        "This turn, ",
        "When challenging ",
        "When play",
        "When this ",
        "When you ",
        "When you play ",
        "Whenever ",
        "While ",
        "You can't play",
        "You characters ",
        "You may ",
        "You other ",
        "You pay ",
        "Your characters ",
        "Your damaged characters ",
        "Your exerted characters ",
        "Your locations ",
        "Your other characters ",
        "{e}",
        "{i}",
    ]
    for type in classifications:
        keywords.extend([f"Your {type} characters ",
                         f"{type} characters "])

    keyword_pattern_numbers = r"\b\d+\s*{i}\b"
    if text:
        matches = re.findall(keyword_pattern_numbers, text)
        keywords.extend(matches)
        
    numbers_with_keywords = [
        "Deal", "Draw", "Move", "Put", "Gain"
        ]
    
    for word in numbers_with_keywords:
        number_keyword_pattern_numbers = fr"{word} \d+"
        number_Matches = re.findall(number_keyword_pattern_numbers, text)
        keywords.extend(number_Matches)
    
    # Prep the text

    # 1) Remove keywords from the start of a line
    keyword_pattern = (
        r"(?:Evasive|Bodyguard|Rush|Ward|Vanish|Support|Reckless|"  # single word keywords
        r"Challenger \+\d+|Resist \+\d+|Challenger\+\d+|"  # + Keywords
        r"Singer \d+|Sing Together \d+|"  # singing
        r"Puppy Shift \d+:?|Shift \d+:?|Universal Shift \d+:?)"
    )
    text = re.sub(rf"(?mi)^[ \t]*{keyword_pattern}\s*\([^)]*\)\s*(?:\r?\n)?", "", text)

    # 2) Strip off any "Label: " at the start of a line
    # text = re.sub(r"(?m)^[ \t]*[^:\n]+:\s*", "", text)

    # 3) Strip off any ALL-CAPS prefix before a dash
    pattern = re.compile(
        r"""(?mx)          # multi-line, verbose
           ^[ \t]*            # start of line + optional indent
           (?=[^a-z]*[-–])    # assert: from here to the dash there are NO lowercase letters
           [^-–]+[-–]\s*      # consume everything up through the dash + any following space
           """,
    )

    text = pattern.sub("", text)

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
    text = text.replace("\r", "")
    text = text.replace("\n", "")
    text = text.encode("ascii", "ignore").decode("ascii")

    # Find the earliest occurrence of any keyword
    first_position = len(text)  # Default to end of text
    found_keyword = None
    text_lower = text.lower()

    for keyword in keywords:
        # Search in lowercase text
        position = text_lower.find(keyword.lower())
        if position != -1 and position < first_position:
            first_position = position
            found_keyword = keyword

    # If a keyword was found, trim the text using the original position
    if found_keyword:
        return text[first_position:].strip()
    else:
        # No keyword found, return the original text
        return text


def create_smaller_json(input_file, output_file):
    try:
        print(f"Attempting to open file at: {input_file}")
        with open(input_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Check if the data is an array directly or nested under a key
        if isinstance(data, list):
            cards = data
        elif isinstance(data, dict) and "cards" in data:
            cards = data["cards"]
        else:
            print(f"Unexpected JSON structure in {input_file}")
            return False

        # Create new list with only the specified fields
        simplified_cards = []
        classifications = set()

        for card in cards:
            cardType = card.get("Classifications")
            if cardType:
                # Split the classifications by "," and strip any whitespace from each item
                classifications.update(item.strip() for item in cardType.split(","))
                
        classifications = list(classifications)
        # print (classifications)
        
        for card in cards:
            # Clean the Body_Text field
            body_text = card.get("Body_Text")
            
            cleaned_body_text = clean_body_text(body_text, classifications)

            simplified_card = {
                "Name": card.get("Name"),
                "Classifications": card.get("Classifications"),
                "Color": card.get("Color"),
                "Cost": card.get("Cost"),
                "Inkable": card.get("Inkable"),
                "Type": card.get("Type"),
                "Unique_ID": card.get("Unique_ID"),
                "Body_Text": cleaned_body_text,
                "Abilities": card.get("Abilities"),
                "Willpower": card.get("Willpower"),
                "Move_Cost": card.get("Move_Cost"),
                "Strength": card.get("Strength"),
                "Lore": card.get("Lore"),
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
			output_file = os.path.join(output_dir, "lorcana_cards_simplified2.json")

	create_smaller_json(input_file, output_file)
