import os,re,json

script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
input_file = os.path.join(parent_dir, "lorcana_cards.json")
with open(input_file, "r", encoding = "utf-8") as f:
	data = json.load(f)

for card in data:
	card_Abilities = card.get("Abilities")
	body_Text = card.get("Body_Text")
	# Check if "Shift" is present but NOT followed by a number
	if card_Abilities and "Shift" in card_Abilities and not re.search(r"Shift \d", card_Abilities):
		matches = re.findall(r":(.*?)\(", body_Text)
		shift_Extract = f'Shift {matches[0].strip()}'
		card_Abilities = card_Abilities.replace("Shift", shift_Extract)
		
		print(matches)
		print(shift_Extract)
		print(card_Abilities)
