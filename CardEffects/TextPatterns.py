import re

from effects_Definitions import EffectType, TargetType, TriggerCondition

# --- Ability Trigger Patterns ---
PATTERNS = [
		# Activated Abilities ({e} Cost - Effect)
		{'regex':   re.compile(r"^{e}(?:,\s*(?P<ink_cost>\d+){i})?\s*-\s*(?P<effect_text>.*)",
		                       re.IGNORECASE | re.DOTALL),
		 'trigger': TriggerCondition.ACTIVATED, 'has_cost': True},

		# Triggered Abilities (When/Whenever...)
		{'regex':   re.compile(r"^When you play this character,?\s*(?P<effect_text>.*)", re.IGNORECASE | re.DOTALL),
		 'trigger': TriggerCondition.ON_PLAY, 'has_cost': False},
		{'regex':   re.compile(r"^Whenever this character quests,?\s*(?P<effect_text>.*)", re.IGNORECASE | re.DOTALL),
		 'trigger': TriggerCondition.ON_QUEST, 'has_cost': False},
		{'regex':   re.compile(r"^Whenever this character challenges another character,?\s*(?P<effect_text>.*)",
		                       re.IGNORECASE | re.DOTALL),
		 'trigger': TriggerCondition.ON_CHALLENGE, 'has_cost': False},
		{'regex':   re.compile(r"^Whenever this character is challenged,?\s*(?P<effect_text>.*)",
		                       re.IGNORECASE | re.DOTALL),
		 'trigger': TriggerCondition.ON_BEING_CHALLENGED, 'has_cost': False},
		{'regex':   re.compile(r"^When this character is banished,?\s*(?P<effect_text>.*)", re.IGNORECASE | re.DOTALL),
		 'trigger': TriggerCondition.ON_BANISH, 'has_cost': False},
		{'regex':      re.compile(r"^Whenever one of your other characters is banished,?\s*(?P<effect_text>.*)",
		                          re.IGNORECASE | re.DOTALL),
		 'trigger':    TriggerCondition.ON_CHARACTER_LEAVES_PLAY, 'has_cost': False,
		 'parameters': {'filter': 'own_other_banished'}},  # Example filter
		{'regex':   re.compile(r"^At the start of your turn,?\s*(?P<effect_text>.*)", re.IGNORECASE | re.DOTALL),
		 'trigger': TriggerCondition.START_OF_TURN, 'has_cost': False},
		{'regex':   re.compile(r"^At the end of your turn,?\s*(?P<effect_text>.*)", re.IGNORECASE | re.DOTALL),
		 'trigger': TriggerCondition.END_OF_TURN, 'has_cost': False},
		{'regex':   re.compile(
			r"^When this character is chosen by an opponent as part of resolving an action's effect,?\s*(?P<effect_text>.*)",
			re.IGNORECASE | re.DOTALL),
		 'trigger': TriggerCondition.KEYWORD_VANISH, 'has_cost': False},
		{'regex':   re.compile(r"^When this character sings a song,?\s*(?P<effect_text>.*)", re.IGNORECASE | re.DOTALL),
		 'trigger': TriggerCondition.ON_SING, 'has_cost': False},
		{'regex':   re.compile(r"^During your turn,?\s*(?P<effect_text>.*)", re.IGNORECASE | re.DOTALL),
		 'trigger': TriggerCondition.ON_YOUR_TURN, 'has_cost': False},
		{'regex':   re.compile(r"^While this character is at a location,?\s*(?P<effect_text>.*)",
		                       re.IGNORECASE | re.DOTALL),
		 'trigger': TriggerCondition.WHILE_AT_LOCATION, 'has_cost': False},
		{'regex':   re.compile(r"^Whenever a character moves here,?\s*(?P<effect_text>.*)", re.IGNORECASE | re.DOTALL),
		 'trigger': TriggerCondition.ON_MOVE_TO_LOCATION, 'has_cost': False},

		# Passive/Continuous (If no trigger matched, assume continuous for now)
		{'regex':   re.compile(r"^(?P<effect_text>.*)"),  # Catch-all if no other trigger matches
		 'trigger': TriggerCondition.CONTINUOUS, 'has_cost': False},
]

# --- Effect Parsing Patterns (within effect_text) ---
EFFECT_PATTERNS = [
		# Examples - Order can matter (more specific first)
		{'regex':       re.compile(r"draw (?P<amount>\d+|a) card", re.IGNORECASE),
		 'effect_type': EffectType.DRAW_CARD, 'target': TargetType.SELF_PLAYER},
		{'regex':       re.compile(r"gain (?P<amount>\d+) lore", re.IGNORECASE),
		 'effect_type': EffectType.GAIN_LORE, 'target': TargetType.SELF_PLAYER},
		{'regex':       re.compile(r"each opponent loses (?P<amount>\d+) lore", re.IGNORECASE),
		 'effect_type': EffectType.LOSE_LORE, 'target': TargetType.OPPONENT_PLAYER},  # Target indicates who loses
		{'regex':       re.compile(r"deal (?P<amount>\d+) damage to chosen (?P<target_type>character|location)",
		                           re.IGNORECASE),
		 'effect_type': EffectType.DEAL_DAMAGE},  # Target type determined by regex group
		{'regex':              re.compile(
				r"remove up to (?P<amount>\d+) damage from chosen (?P<target_type>character|location)", re.IGNORECASE),
				'effect_type': EffectType.HEAL_DAMAGE},
		{'regex':              re.compile(
				r"chosen (?P<target_adj>opposing|other)?\s*character gets (?P<mod>[+\-]\d+) {(?P<stat>[swl])}",
				re.IGNORECASE),
				'effect_type': EffectType.MODIFY_STATS},
		{'regex':              re.compile(
				r"return chosen (?P<target_type>character|item) (?:card)? to (?:their|its) player's hand",
				re.IGNORECASE),
				'effect_type': EffectType.RETURN_TO_HAND},
		{'regex':       re.compile(r"banish chosen (?P<target_type>character|item|location)", re.IGNORECASE),
		 'effect_type': EffectType.BANISH_CARD},  # Need a BANISH effect type
		{'regex':       re.compile(r"exert chosen (?P<target_adj>opposing)?\s*character", re.IGNORECASE),
		 'effect_type': EffectType.EXERT_CARD},
		{'regex':       re.compile(r"ready chosen (?P<target_adj>other)?\s*character", re.IGNORECASE),
		 'effect_type': EffectType.READY_CARD},
		{'regex':       re.compile(r"each opponent chooses and discards (?P<amount>\d+|a) card", re.IGNORECASE),
		 'effect_type': EffectType.DISCARD_CARD_CHOSEN, 'target': TargetType.OPPONENT_PLAYER},
		{'regex':       re.compile(r"shuffle a card from any discard into its player's deck", re.IGNORECASE),
		 'effect_type': EffectType.SHUFFLE_INTO_DECK, 'target': TargetType.TARGET_CARD_IN_DISCARD_CHOSEN},
		{'regex':       re.compile(r"you may play that song again from your discard", re.IGNORECASE),
		 'effect_type': EffectType.PUT_INTO_PLAY, 'target': TargetType.CARD_TYPE,
		 'parameters':  {'type': 'Action', 'subtype': 'Song'}},
		{'regex':       re.compile(r"this character gets \+(?P<amount>\d+) {s} this turn", re.IGNORECASE),
		 'effect_type': EffectType.MODIFY_STATS, 'target': TargetType.SELF_CARD,
		 'parameters':  {'stat': 'strength', 'duration': 'turn'}},
		{'regex':       re.compile(r"this character can't be challenged this turn", re.IGNORECASE),
		 'effect_type': EffectType.CANNOT_BE_CHALLENGED, 'target': TargetType.SELF_CARD,
		 'parameters':  {'duration': 'turn'}},
		{'regex':       re.compile(r"look at the top (?P<amount>\d+) cards of your deck", re.IGNORECASE),
		 'effect_type': EffectType.LOOK_AT_TOP_CARDS, 'target': TargetType.SELF_PLAYER},
		{'regex':       re.compile(r"reveal (?:up to )?(?P<amount>\d+) (?P<card_type>\w+) cards", re.IGNORECASE),
		 'effect_type': EffectType.REVEAL_CARD},
		{'regex':       re.compile(r"put (?:them|it) into your hand", re.IGNORECASE),
		 'effect_type': EffectType.OTHER, 'parameters': {'action': 'put_into_hand'}},
		{'regex':       re.compile(
			r"chosen character gains (?P<keyword>\w+)( \+(?P<amount>\d+))? (?:this|their next) turn",
			re.IGNORECASE),
		 'effect_type': EffectType.GRANT_KEYWORD, 'parameters': {'duration': 'turn'}},
		{'regex':       re.compile(
			r"your (?P<target_adj>other)?\s*(?P<classification>[\w\s,]+) characters get \+(?P<amount>\d+) {(?P<stat>[swl])}",
			re.IGNORECASE),
		 'effect_type': EffectType.MODIFY_STATS, 'target': TargetType.ALL_OWN_CHARACTERS,
		 'parameters':  {'filter': 'classification'}},
]

# --- Keyword Pattern Recognition ---
KEYWORD_PATTERNS = [
		# Keywords with numeric values
		{'regex':   re.compile(r"^Challenger \+(?P<amount>\d+)$", re.IGNORECASE),
		 'keyword': 'Challenger', 'has_value': True, 'trigger': TriggerCondition.KEYWORD_CHALLENGER},
		{'regex':   re.compile(r"^Resist \+(?P<amount>\d+)$", re.IGNORECASE),
		 'keyword': 'Resist', 'has_value': True, 'trigger': TriggerCondition.KEYWORD_RESIST},
		{'regex':   re.compile(r"^Shift (?P<amount>\d+)$", re.IGNORECASE),
		 'keyword': 'Shift', 'has_value': True, 'trigger': TriggerCondition.KEYWORD_SHIFT},
		{'regex':   re.compile(r"^Singer (?P<amount>\d+)$", re.IGNORECASE),
		 'keyword': 'Singer', 'has_value': True, 'trigger': TriggerCondition.KEYWORD_SINGER},
		{'regex':   re.compile(r"^Sing Together (?P<amount>\d+)$", re.IGNORECASE),
		 'keyword': 'Sing Together', 'has_value': True, 'trigger': TriggerCondition.OTHER},

		# Classification-based Shift variants
		{'regex':   re.compile(r"^(?P<classification>\w+) Shift (?P<amount>\d+)$", re.IGNORECASE),
		 'keyword': 'Classification Shift', 'has_value': True, 'trigger': TriggerCondition.KEYWORD_SHIFT},
		{'regex':   re.compile(r"^Universal Shift (?P<amount>\d+)$", re.IGNORECASE),
		 'keyword': 'Universal Shift', 'has_value': True, 'trigger': TriggerCondition.KEYWORD_SHIFT},

		# Fixed keywords without values
		{'regex':   re.compile(r"^Bodyguard$", re.IGNORECASE),
		 'keyword': 'Bodyguard', 'has_value': False, 'trigger': TriggerCondition.KEYWORD_BODYGUARD},
		{'regex':   re.compile(r"^Evasive$", re.IGNORECASE),
		 'keyword': 'Evasive', 'has_value': False, 'trigger': TriggerCondition.KEYWORD_EVASIVE},
		{'regex':   re.compile(r"^Reckless$", re.IGNORECASE),
		 'keyword': 'Reckless', 'has_value': False, 'trigger': TriggerCondition.KEYWORD_RECKLESS},
		{'regex':   re.compile(r"^Rush$", re.IGNORECASE),
		 'keyword': 'Rush', 'has_value': False, 'trigger': TriggerCondition.KEYWORD_RUSH},
		{'regex':   re.compile(r"^Support$", re.IGNORECASE),
		 'keyword': 'Support', 'has_value': False, 'trigger': TriggerCondition.KEYWORD_SUPPORT},
		{'regex':   re.compile(r"^Vanish$", re.IGNORECASE),
		 'keyword': 'Vanish', 'has_value': False, 'trigger': TriggerCondition.KEYWORD_VANISH},
		{'regex':   re.compile(r"^Ward$", re.IGNORECASE),
		 'keyword': 'Ward', 'has_value': False, 'trigger': TriggerCondition.KEYWORD_WARD},
]

# Mapping for stat abbreviations
STAT_MAP = {'s': 'strength', 'w': 'willpower', 'l': 'lore'}


# Function to parse keywords with values
def parse_keyword(ability_text):
	"""Parse a keyword ability text and return the base keyword and any value."""
	for pattern in KEYWORD_PATTERNS:
		match = pattern['regex'].match(ability_text)
		if match:
			if pattern['has_value']:
				# Handle keywords with values
				amount = int(match.group('amount')) if 'amount' in match.groupdict() else None

				# Handle classification-based shift variants
				if pattern['keyword'] == 'Classification Shift' and 'classification' in match.groupdict():
					classification = match.group('classification')
					return {
							'keyword':        f"{classification} Shift",
							'amount':         amount,
							'trigger':        pattern['trigger'],
							'classification': classification
					}
				return {
						'keyword': pattern['keyword'],
						'amount':  amount,
						'trigger': pattern['trigger']
				}
			else:
				# Handle simple keywords
				return {
						'keyword': pattern['keyword'],
						'trigger': pattern['trigger']
				}
	return None
