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

keyword_pattern = (
    r"(?:Evasive|Bodyguard|Rush|Ward|Vanish|Support|Reckless|Shift: |"  # single word keywords
    r"Challenger \+\d+|Resist \+\d+|Challenger\+\d+|"  # + Keywords
    r"Singer \d+|Sing Together \d+|"  # singing
    r"Puppy Shift \d+:?|Shift \d+:?|Universal Shift \d+:? )"
)

def clean_body_text (text, classifications):
    if not text:
        return text

    pattern = re.compile(keyword_pattern)
    
    text = re.sub('\r \r', '\n', text)
    text = re.sub(r'\)\r', ')\n', text)
    text = re.sub('\r', '', text)
    
    # Remove parenthetical text
    text = re.sub(r'(\([^)]*?)\n([^)]*\))', '', text)
    text = re.sub(r'(\d+)\s+(\{)', r'\1\2', text)
    
    text = re.sub(r'([+-])\s*(\d+)\s*(\{[sw]\})', r'\1\2\3', text)
    
    # Split the text
    text_parts = text.split('\n')
    
    # Filter out lines that START WITH any of the keywords (notice the NOT operator)
    text_parts = [line for line in text_parts if not pattern.match(line)]
    
    cleaned_parts = []
    
    # Process each part separately
    for part in text_parts:
        cleaned_part = process_text_part(part, classifications)
        if cleaned_part:  # Only add non-empty parts
            cleaned_parts.append(cleaned_part)
    
    # Join the cleaned parts back together with newlines
    return ' '.join(cleaned_parts)


def process_text_part (text, classifications):
    if not text:
        return text
    
    # List of keywords to look for (with space after each word)
    keywords = [
        "All cards in your hand ",
        "At the end ",
        "At the start ",
        "All opposing characters ",
        "Banish ",
        "Banish chosen ",
        "Characters ",
        "Choose ",
        "Chosen ",
        "Count the number ",
        "Damaged characters ",
        "Damage counters ",
        "Deal damage ",
        "Draw a card",
        "During an ",
        "During your ",
        "During each ",
        "During opponent ",
        "During opponents' ",
        "During your ",
        "Each Opponent ",
        "Each player ",
        "Exert ",
        "For each ",
        "If an ",
        "If chosen ",
        "If you have ",
        "If you used ",
        "Look at the top ",
        "Move a ",
        "Move up to ",
        "Name a card",
        "Once during your",
        "Once per turn",
        "Opponents ",
        "Opposing ",
        "Play a ",
        "Put chosen ",
        "Put the top",
        "Put up to ",
        "Put all opposing ",
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
                         f"Your other {type} ",
                         f"Your {type} and ",
                         f"{type} characters "])
    
    keyword_pattern_numbers = r"\b\d+\s*\{i\}"
    
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
    
    text = re.sub(rf"(?mi)^[ \t]*{keyword_pattern}\s*\([^)]*\)\s*(?:\r?\n)?", "", text)
    
    # Remove ability keywords that might be at the beginning
    # This pattern will match comma-separated lists of ability keywords
    ability_keywords = ["Bodyguard", "Support", "Evasive", "Rush", "Ward", "Vanish", "Reckless",
                        "Challenger", "Resist", "Singer", "Sing Together", "Shift", "Universal Shift", "Puppy Shift"]
    
    # Create a pattern that matches one or more ability keywords separated by commas
    ability_pattern = r"^(?:" + "|".join(ability_keywords) + r")(?:\s*,\s*(?:" + "|".join(ability_keywords) + r"))*\s*-?\s*"
    text = re.sub(ability_pattern, "", text, flags = re.IGNORECASE)
    
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

    text = text.replace("\r", "")
    text = text.replace("\n", "")
    text = text.encode("ascii", "ignore").decode("ascii")
    
    # Inserting specifics
    text = text.replace("Banish this item - ", "Banish this item : ")
    text = text.replace("{i} - ", "{i} : ")
    text = text.replace("{e} - ", "{e} : ")
    text = text.replace("{e} one of your items - ", "{e} one of your items : ")
    text = text.replace("Banish one of your items - ", "Banish one of your items : ")
    text = text.replace(" characters - ", " characters : ")
    text = text.replace(" - ", " : ")
    
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
        return text.strip()


def create_smaller_json (input_file, output_file):
    try:
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
        
        # Create new list with only the specified fields
        simplified_cards = []
        classifications = set()  # Initialize as a set
        
        for card in cards:
            card_Type = card.get("Classifications")
            body_Text = card.get("Body_Text")
            card_Abilities = card.get("Abilities")
            
            if card_Abilities and "Shift" in card_Abilities and not re.search(r"Shift \d", card_Abilities):
                matches = re.findall(r":(.*?)\(", body_Text)
                if matches:  # Add check to make sure matches is not empty
                    shift_Extract = f'Shift {matches[0].strip()}'
                    card_Abilities = card_Abilities.replace("Shift", shift_Extract)
            
            if card_Type:
                # Check if card_Type is a string before splitting
                if isinstance(card_Type, str):
                    # Split the classifications by "," and strip any whitespace from each item
                    classifications.update(item.strip() for item in card_Type.split(","))
                elif isinstance(card_Type, list):
                    # If card_Type is already a list, add each item to the set
                    classifications.update(item.strip() if isinstance(item, str) else item for item in card_Type)
        
        # Convert to list only after all updates are done
        classifications_list = list(classifications)
        
        # You also need to define clean_body_text function or pass it to your function
        for card in cards:
            card_Type = card.get("Classifications")
            body_Text = card.get("Body_Text")
            card_Abilities = card.get("Abilities")
            
            if card_Abilities and "Shift" in card_Abilities and not re.search(r"Shift \d", card_Abilities):
                matches = re.findall(r":(.*?)\(", body_Text)
                if matches:
                    shift_Extract = f'Shift {matches[0].strip()}'
                    card_Abilities = card_Abilities.replace("Shift", shift_Extract)
            
            # Assuming clean_body_text is defined elsewhere
            cleaned_body_text = clean_body_text(body_Text, classifications_list)
            
            simplified_card = {
                "Name"           : card.get("Name"),
                "Classifications": card.get("Classifications"),
                "Color"          : card.get("Color"),
                "Cost"           : card.get("Cost"),
                "Inkable"        : card.get("Inkable"),
                "Type"           : card.get("Type"),
                "Unique_ID"      : card.get("Unique_ID"),
                "Body_Text"      : cleaned_body_text,
                "Abilities"      : card_Abilities,
                "Willpower"      : card.get("Willpower"),
                "Move_Cost"      : card.get("Move_Cost"),
                "Strength"       : card.get("Strength"),
                "Lore"           : card.get("Lore"),
                }
            simplified_cards.append(simplified_card)
        
        # Write the simplified data to a new file
        with open(output_file, 'w', encoding = 'utf-8') as f:
            json.dump(simplified_cards, f, indent = 2)
        
        print(f"Successfully created {output_file} with {len(simplified_cards)} cards")
        return True
    
    except Exception as e:
        print(f"Error processing JSON file: {e}")
        # Print more detailed information for debugging
        import traceback
        traceback.print_exc()
        return False


def find_Unique_BodyTexts (input_file, output_file):
    try:
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
        
        # Create new list with only the specified fields
        simplified_cards = []
        for card in cards:
            # Clean the Body_Text field
            
            simplified_card = {
                # "Unique_ID": card.get("Unique_ID"),
                "Body_Text": card.get("Body_Text"),
                # "Abilities": card.get("Abilities"),
                }
            simplified_cards.append(simplified_card)
        
        # Write the simplified data to a new file
        unique_cards = list({c["Body_Text"]: c for c in simplified_cards}.values())
        unique_cards = sorted(unique_cards, key = lambda x: (x["Body_Text"] is None, x["Body_Text"] or ""))
        with open(output_file, "w", encoding = "utf-8") as f:
            json.dump(unique_cards, f, indent = 2)
        
        print(f"Successfully created {output_file} with {len(unique_cards)} cards")
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
    
    input_file = os.path.join(parent_dir, "lorcana_cards_simplified.json")
    output_file = os.path.join(script_dir, "bodytext.json")
    
    find_Unique_BodyTexts(input_file, output_file)
