import requests
import json
import os
import time

'''
{i} = ink
{w} = willpower
{s} = strength
{l} = lore

'''

API_URL = "https://api.lorcana-api.com/bulk/cards"
LOCAL_FILENAME = "lorcana_cards.json"
MAX_FILE_AGE_SECONDS = 86400 * 7 # 7 days

def fetch_lorcana_data(url=API_URL, filename=LOCAL_FILENAME, max_age=MAX_FILE_AGE_SECONDS, force_update=False):
    """
    Fetches Lorcana card data from the API or loads it from a local file.

    Args:
        url (str): The API endpoint URL.
        filename (str): The name of the local file to save/load data.
        max_age (int): Maximum age of the local file in seconds before re-downloading.
                       Set to 0 or None to disable age check.
        force_update (bool): If True, always download fresh data from the API.

    Returns:
        list: A list of dictionaries, where each dictionary represents a card.
              Returns None if fetching fails.
    """
    use_local_file = False
    if not force_update and os.path.exists(filename):
        if max_age is None or max_age <= 0:
            use_local_file = True
        else:
            # Check file modification time
            file_mod_time = os.path.getmtime(filename)
            if (time.time() - file_mod_time) < max_age:
                use_local_file = True
            else:
                print(f"Local file '{filename}' is older than {max_age // 3600} hours. Re-fetching.")

    if use_local_file:
        print(f"Loading card data from local file: {filename}")
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"Successfully loaded {len(data)} cards from local file.")
            return data
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading local file '{filename}': {e}. Attempting to fetch from API.")
            # Fall through to fetch from API if local file is corrupted

    # --- Fetch data from API ---
    print(f"Fetching card data from API: {url}")
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status() # Raises an HTTPError for bad responses (4xx or 5xx)

        data = response.json()
        print(f"Successfully fetched {len(data)} cards from API.")

        # Save the data locally
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                # Use indent for readability, ensure_ascii=False for potential special characters
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"Card data saved locally to: {filename}")
        except IOError as e:
            print(f"Error saving data to local file '{filename}': {e}")
        return data

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from API: {e}")
        if os.path.exists(filename):
            print(f"Attempting to load potentially stale data from {filename} as a fallback.")
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"Successfully loaded {len(data)} cards from stale local file.")
                return data
            except Exception as load_err:
                print(f"Could not load stale local file: {load_err}")
        return None # Return None if fetching failed and no usable local file

# --- Main execution block ---
if __name__ == "__main__":
    # Example usage:
    # To force an update, run: fetch_lorcana_data(force_update=True)
    # To use local file indefinitely if it exists: fetch_lorcana_data(max_age=None)
    card_data = fetch_lorcana_data()

    if card_data:
        print(f"\nFetched/Loaded a total of {len(card_data)} cards.")
        # You can optionally print the details of the first card for verification
        if len(card_data) > 0:
             print("\nExample card data (first card):")
             # Print only the fields requested for brevity, though all fields are loaded/saved
             first_card = card_data[0]
             relevant_fields = [
                 "Classifications", "Abilities", "Color", "Cost", "Inkable",
                 "Name", "Type", "Lore", "Body_Text", "Willpower", "Strength"
             ]
             print("{")
             for field in relevant_fields:
                 # Use .get() to avoid KeyError if a field is missing for some reason
                 print(f"  \"{field}\": {json.dumps(first_card.get(field))},")
             print("  ...") # Indicate that there are more fields
             print("}")

    else:
        print("\nFailed to fetch or load card data.")
