import re
from typing import List, Optional, Dict


def _extract_draw_action (text: str) -> Optional[Dict]:
	"""Extracts draw actions from the text."""
	match = re.search(r"(draw) (\d+) cards", text.lower())
	if match:
		return {"action": "draw", "quantity": int(match.group(2))}
	elif "draw a card" in text.lower():
		return {"action": "draw", "quantity": 1}
	return None


def _extract_deal_damage_action (text: str) -> Optional[Dict]:
	"""Extracts deal damage actions from the text."""
	
	match = re.search(
		r"deal (\d+) damage to (chosen character|chosen location|each opposing character|another chosen character)",
		text.lower())
	if match:
		return {"action": "deal_damage", "quantity": int(match.group(1)), "target": match.group(2)}
	return None


def _extract_gain_lore_action (text: str) -> Optional[Dict]:
	"""Extracts gain lore actions."""
	
	match = re.search(r"gain (\d+) lore", text.lower())
	if match:
		return {"action": "gain_lore", "quantity": int(match.group(1))}
	elif "gain 1 lore" in text.lower():
		return {"action": "gain_lore", "quantity": 1}
	return None


def _extract_remove_damage_action (text: str) -> Optional[Dict]:
	"""Extracts remove damage actions."""
	
	match = re.search(
		r"remove up to (\d+) damage from (chosen character|chosen location|each of your characters|any number of chosen characters)",
		text.lower())
	if match:
		return {"action": "remove_damage", "quantity": int(match.group(1)), "target": match.group(2)}
	return None


def _extract_banish_action (text: str) -> Optional[Dict]:
	"""Extracts banish actions."""
	
	if "banish chosen character" in text.lower():
		return {"action": "banish", "target": "chosen character"}
	elif "banish chosen item" in text.lower():
		return {"action": "banish", "target": "chosen item"}
	elif "banish chosen location" in text.lower():
		return {"action": "banish", "target": "chosen location"}
	elif "banish this character" in text.lower():
		return {"action": "banish", "target": "this character"}
	return None


def _extract_ready_action (text: str) -> Optional[Dict]:
	"""Extracts ready actions."""
	
	if "ready chosen character" in text.lower():
		return {"action": "ready", "target": "chosen character"}
	return None


def _extract_exert_action (text: str) -> Optional[Dict]:
	"""Extracts exert actions."""
	
	if "exert chosen character" in text.lower():
		return {"action": "exert", "target": "chosen character"}
	return None


def _extract_return_to_hand_action (text: str) -> Optional[Dict]:
	"""Extracts return to hand actions."""
	
	if "return chosen character to their player's hand" in text.lower():
		return {"action": "return_to_hand", "target": "chosen character"}
	return None


def _extract_shuffle_into_deck_action (text: str) -> Optional[Dict]:
	"""Extracts shuffle into deck actions."""
	
	if "shuffle chosen card from your discard into your deck" in text.lower():
		return {"action": "shuffle_into_deck", "source": "your discard", "target": "chosen card"}
	return None


def parse_ability_text (text: str) -> List[Dict]:
	"""Parses the ability text and returns a list of action dictionaries."""
	
	actions: List[Dict] = []
	
	# --- Actions without commas or colons ---
	# Draw action
	draw_action = _extract_draw_action(text)
	if draw_action:
		actions.append(draw_action)
	
	# Deal damage action
	deal_damage_action = _extract_deal_damage_action(text)
	if deal_damage_action:
		actions.append(deal_damage_action)
	
	# Gain lore action
	gain_lore_action = _extract_gain_lore_action(text)
	if gain_lore_action:
		actions.append(gain_lore_action)
	
	# Remove damage
	remove_damage_action = _extract_remove_damage_action(text)
	if remove_damage_action:
		actions.append(remove_damage_action)
	
	# Banish action
	banish_action = _extract_banish_action(text)
	if banish_action:
		actions.append(banish_action)
	
	# Ready action
	ready_action = _extract_ready_action(text)
	if ready_action:
		actions.append(ready_action)
	
	# Exert action
	exert_action = _extract_exert_action(text)
	if exert_action:
		actions.append(exert_action)
	
	# Return to hand action
	return_to_hand_action = _extract_return_to_hand_action(text)
	if return_to_hand_action:
		actions.append(return_to_hand_action)
	
	# Shuffle into deck action
	shuffle_into_deck_action = _extract_shuffle_into_deck_action(text)
	if shuffle_into_deck_action:
		actions.append(shuffle_into_deck_action)
	
	return actions


# --- Example Usage ---
if __name__ == '__main__':
	ability_texts = [
		"Draw 2 cards",
		"Deal 3 damage to chosen character",
		"Gain 1 lore",
		"Remove up to 2 damage from chosen character",
		"Draw a card",
		"Deal 2 damage to each opposing character",
		"Gain 1 lore for each damaged character opponents have in play",
		"Remove up to 3 damage from chosen character or location Draw a card",
		"Banish chosen character",
		"Banish chosen item Its player gains 2 lore",
		"Banish this character : Banish chosen character",
		"Ready chosen character",
		"Exert chosen character",
		"Return chosen character to their player's hand",
		"Shuffle chosen card from your discard into your deck"
		]
	
	for text in ability_texts:
		parsed_actions = parse_ability_text(text)
		print(f"\nParsing: '{text}'")
		print(f"  --> {parsed_actions}")
