import json
import os

# Get the parent directory of the script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(
    script_dir
)  # This goes up one level to the parent directory

# Define the file paths using the parent directory
input_file = os.path.join(parent_dir, "lorcana_cards_simplified2.json")
output_file = os.path.join(script_dir,"StartingText.json")

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
        for card in cards:
            # Clean the Body_Text field
            bodyText = card.get("Body_Text")
            bodyText = bodyText[:15] if bodyText else ""

            simplified_card = {
                # "Unique_ID": card.get("Unique_ID"),
                "Body_Text": bodyText,
                # "Abilities": card.get("Abilities"),
            }
            simplified_cards.append(simplified_card)
        simplified_cards.sort(key=lambda x: x["Body_Text"])
        # Write the simplified data to a new file
        unique_cards = list({c["Body_Text"]: c for c in simplified_cards}.values())

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(unique_cards, f, indent=2)

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
            output_file = os.path.join(output_dir, "lorcana_cards_simplified2.json")

    create_smaller_json(input_file, output_file)
