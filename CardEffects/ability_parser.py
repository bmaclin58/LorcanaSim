import re
from typing import List, Optional
from effects_Definitions import TriggerCondition, EffectType, TargetType
from ability import Ability, AbilityCost, Effect

# --- Regex Patterns (Copy Pased from User Input) ---
# NOTE: Ensure TriggerCondition, EffectType, TargetType enums match these patterns

# Adjusted {e} and {i} regex to be less strict about placement within patterns
EXERT_COST_REGEX = re.compile(r"{e}", re.IGNORECASE)
INK_COST_REGEX = re.compile(r"(?P<ink_cost>\d+)\s*{i}", re.IGNORECASE)

# --- Trigger/Ability Structure Patterns ---
PATTERNS = [
       # Activated Abilities ({e} Cost - Effect) - Updated to handle cost flexibly
       {'regex':   re.compile(r"^(?P<cost_text>.*?)-\s*(?P<effect_text>.*)", re.IGNORECASE | re.DOTALL),
        'trigger': TriggerCondition.ACTIVATED, 'has_cost': True}, # Cost parsing logic needed separately

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
        'parameters': {'filter': 'own_other_banished'}},
       {'regex':   re.compile(r"^At the start of your turn,?\s*(?P<effect_text>.*)", re.IGNORECASE | re.DOTALL),
        'trigger': TriggerCondition.START_OF_TURN, 'has_cost': False},
       {'regex':   re.compile(r"^At the end of your turn,?\s*(?P<effect_text>.*)", re.IGNORECASE | re.DOTALL),
        'trigger': TriggerCondition.END_OF_TURN, 'has_cost': False},
       {'regex':   re.compile(r"^Whenever this character sings a song,?\s*(?P<effect_text>.*)", re.IGNORECASE | re.DOTALL),
        'trigger': TriggerCondition.ON_SING, 'has_cost': False},
       {'regex':   re.compile(r"^During your turn,?\s*(?P<effect_text>.*)", re.IGNORECASE | re.DOTALL),
        'trigger': TriggerCondition.ON_YOUR_TURN, 'has_cost': False},
       {'regex':   re.compile(r"^While this character is at a location,?\s*(?P<effect_text>.*)",
                              re.IGNORECASE | re.DOTALL),
        'trigger': TriggerCondition.WHILE_AT_LOCATION, 'has_cost': False},
       {'regex':   re.compile(r"^Whenever a character moves here,?\s*(?P<effect_text>.*)", re.IGNORECASE | re.DOTALL),
        'trigger': TriggerCondition.ON_MOVE_TO_LOCATION, 'has_cost': False},

       # Passive/Continuous (If no trigger matched, assume continuous for now)
       # This catch-all should always be last
       {'regex':   re.compile(r"^(?P<effect_text>.*)"),
        'trigger': TriggerCondition.CONTINUOUS, 'has_cost': False},
]

# --- Effect Parsing Patterns (within effect_text) ---
# Simplified list for initial implementation - needs significant expansion
EFFECT_PATTERNS = [
    {'regex': re.compile(r"draw (?P<amount>\d+|a) card", re.IGNORECASE),
     'effect_type': EffectType.DRAW_CARD, 'target': TargetType.SELF_PLAYER, 'params': {'amount': 1}}, # Default amount 1, update if digit found
    {'regex': re.compile(r"gain (?P<amount>\d+) lore", re.IGNORECASE),
     'effect_type': EffectType.GAIN_LORE, 'target': TargetType.SELF_PLAYER},
    {'regex': re.compile(r"each opponent loses (?P<amount>\d+) lore", re.IGNORECASE),
     'effect_type': EffectType.LOSE_LORE, 'target': TargetType.OPPONENT_PLAYER},
    {'regex': re.compile(r"deal (?P<amount>\d+) damage to chosen (?P<target_type>character|location)", re.IGNORECASE),
     'effect_type': EffectType.DEAL_DAMAGE}, # Target determined by group
    {'regex': re.compile(r"remove up to (?P<amount>\d+) damage from chosen (?P<target_type>character|location)", re.IGNORECASE),
     'effect_type': EffectType.HEAL_DAMAGE},
    {'regex': re.compile(r"gets (?P<mod>[+\-]\d+) {(?P<stat>[swl])}", re.IGNORECASE), # Simplified stat gain
      'effect_type': EffectType.MODIFY_STATS, 'target': TargetType.SELF_CARD}, # Target might need adjustment based on context
    # Add many more patterns here...
]


# --- Keyword Pattern Recognition ---
# Simplified list - Needs expansion and handling of values (Shift X, Challenger +X)
KEYWORD_PATTERNS = [
    {'regex': re.compile(r"^Rush$", re.IGNORECASE), 'keyword': 'Rush', 'trigger': TriggerCondition.KEYWORD_RUSH, 'has_value': False},
    {'regex': re.compile(r"^Bodyguard$", re.IGNORECASE), 'keyword': 'Bodyguard', 'trigger': TriggerCondition.KEYWORD_BODYGUARD, 'has_value': False},
    {'regex': re.compile(r"^Evasive$", re.IGNORECASE), 'keyword': 'Evasive', 'trigger': TriggerCondition.KEYWORD_EVASIVE, 'has_value': False},
    {'regex': re.compile(r"^Ward$", re.IGNORECASE), 'keyword': 'Ward', 'trigger': TriggerCondition.KEYWORD_WARD, 'has_value': False},
	{'regex': re.compile(r"^Vanish$", re.IGNORECASE), 'keyword': 'Vanish', 'trigger': TriggerCondition.KEYWORD_VANISH, 'has_value': False},
    {'regex': re.compile(r"^Challenger \+(?P<amount>\d+)$", re.IGNORECASE), 'keyword': 'Challenger', 'trigger': TriggerCondition.KEYWORD_CHALLENGER, 'has_value': True},
    {'regex': re.compile(r"^Resist \+(?P<amount>\d+)$", re.IGNORECASE), 'keyword': 'Resist', 'trigger': TriggerCondition.KEYWORD_RESIST, 'has_value': True},
    {'regex': re.compile(r"^Shift (?P<amount>\d+)$", re.IGNORECASE), 'keyword': 'Shift', 'trigger': TriggerCondition.KEYWORD_SHIFT, 'has_value': True},
     {'regex': re.compile(r"^Singer (?P<amount>\d+)$", re.IGNORECASE), 'keyword': 'Singer', 'trigger': TriggerCondition.KEYWORD_SINGER, 'has_value': True},
    # ... Add other keywords (Support, Reckless, Vanish, classifications for Shift)
]

# --- Helper Functions ---

def parse_cost(cost_text: str) -> Optional[AbilityCost]:
    """Parses standard {e} and ink costs from a string segment."""
    if not cost_text:
        return None

    cost = AbilityCost()
    cost_text = cost_text.strip()

    # Check for exert cost
    if EXERT_COST_REGEX.search(cost_text):
        cost.exert_self = True
        # Remove {e} part for ink parsing
        cost_text = EXERT_COST_REGEX.sub('', cost_text).strip(' ,')

    # Check for ink cost
    ink_match = INK_COST_REGEX.search(cost_text)
    if ink_match:
        cost.ink_cost = int(ink_match.group('ink_cost'))

    # Basic check if any cost was actually found
    if cost.ink_cost > 0 or cost.exert_self:
        return cost
    else:
        # Check for non-standard costs mentioned (basic version)
        # This needs more sophisticated NLP/pattern matching
        lower_text = cost_text.lower()
        if "discard a card" in lower_text: cost.discard_card = True # Basic check
        # Add checks for damage_card, banish_card if specific phrases are common
        if cost.discard_card or cost.damage_card or cost.banish_card:
             return cost # Return if non-standard cost found

    return None # No parsable cost found

def parse_effects(effect_text: str) -> List[Effect]:
    """
    Parses the effect description text into a list of Effect objects.
    This is a simplified version and needs significant enhancement.
    """
    effects: List[Effect] = []
    remaining_text = effect_text.strip().rstrip('.') # Remove trailing period

    # --- Very Simple Effect Parsing Logic ---
    # TODO: This needs to handle multiple effects, conditions, complex targets, etc.
    # It should likely loop and consume parts of the string, or use more advanced parsing.

    matched_an_effect = False
    for pattern_info in EFFECT_PATTERNS:
        match = pattern_info['regex'].search(remaining_text)
        if match:
            effect_type = pattern_info['effect_type']
            target_type = pattern_info.get('target', TargetType.OTHER) # Default target
            params = pattern_info.get('params', {}).copy() # Get default params

            # Extract parameters from regex groups
            for key, value in match.groupdict().items():
                if value is not None:
                    # Basic type conversion (needs refinement)
                    if key == 'amount':
                       if value.isdigit():
                           params[key] = int(value)
                       elif value.lower() == 'a':
                           params[key] = 1
                    elif key == 'mod' and value:
                        params['modifier'] = int(value) # Assuming mod becomes modifier
                    elif key == 'stat':
                        stat_map = {'s': 'strength', 'w': 'willpower', 'l': 'lore'}
                        params[key] = stat_map.get(value.lower())
                    elif key == 'target_type':
                        # Map matched target type string to Enum
                        target_str = f"TARGET_{value.upper()}_CHOSEN" # Basic assumption
                        try:
                            target_type = TargetType[target_str]
                        except KeyError:
                            print(f"Warning: Could not map target_type '{value}' to TargetType enum.")
                            target_type = TargetType.OTHER
                    else:
                        params[key] = value

            effects.append(Effect(effect_type=effect_type, target=target_type, parameters=params))
            matched_an_effect = True
            # TODO: Ideally, remove the matched part and continue parsing remaining_text
            # For now, we just take the first match for simplicity
            break # Exit after first match in this basic version

    if not matched_an_effect and remaining_text:
        # If no specific effect pattern matched, create a generic 'OTHER' effect
        effects.append(Effect(effect_type=EffectType.OTHER, target=TargetType.NONE, parameters={'raw_text': remaining_text}))

    return effects


# --- Main Parsing Function ---

def parse_abilities(body_text: Optional[str], abilities_text: Optional[str]) -> List[Ability]:
    """
    Parses the Body_Text and Abilities fields of a card into a list of Ability objects.

    Args:
        body_text: The string from the 'Body_Text' field.
        abilities_text: The string from the 'Abilities' field (often lists keywords).

    Returns:
        A list of parsed Ability objects.
    """
    parsed_abilities: List[Ability] = []
    processed_text_segments = set() # Avoid processing the same text twice if duplicated

    # 1. Process Keywords first (usually in abilities_text, but check both)
    keyword_texts = []
    if abilities_text:
       # Keywords in abilities_text are often comma-separated
       keyword_texts.extend([kw.strip() for kw in abilities_text.split(',')])
    # Sometimes keywords are also mentioned standalone in body_text
    # This is simplistic; NLP might be needed for complex cases
    if body_text:
        # Check if body_text seems to just list keywords found in abilities_text
        # This prevents adding duplicate keyword abilities
        simple_body = ''.join(filter(str.isalnum, body_text.lower()))
        simple_abilities = ''.join(filter(str.isalnum, abilities_text.lower())) if abilities_text else ""
        if simple_body != simple_abilities:
             # Simple split by sentence/period for potential keywords in body text
             potential_keywords = [seg.strip() for seg in body_text.split('.') if seg.strip()]
             keyword_texts.extend(potential_keywords)


    for text in keyword_texts:
        text = text.strip()
        if not text or text in processed_text_segments:
            continue

        matched_keyword = False
        for pattern_info in KEYWORD_PATTERNS:
            match = pattern_info['regex'].fullmatch(text) # Use fullmatch for keywords
            if match:
                params = {}
                if pattern_info['has_value']:
                    try:
                       params['amount'] = int(match.group('amount'))
                    except (IndexError, KeyError, ValueError):
                         print(f"Warning: Keyword '{pattern_info['keyword']}' expected value but couldn't parse from '{text}'")
                # Keywords often don't have distinct effects in our structure,
                # their trigger implies behavior handled by the game engine.
                # If a keyword *grants* an effect (rare), parse_effects could be called.
                effects = [Effect(effect_type=EffectType.OTHER, target=TargetType.SELF_CARD, parameters=params)] if params else []

                parsed_abilities.append(Ability(
                    trigger=pattern_info['trigger'],
                    effects=effects, # Usually empty or just holds the value
                    cost=None,
                    source_text=text
                ))
                processed_text_segments.add(text)
                matched_keyword = True
                break # Found keyword match for this segment
        # Keep track of keyword texts even if not matched by patterns, maybe add as OTHER later?


    # 2. Process Body Text for triggered/activated/continuous abilities
    if body_text:
        # Split body text into potential ability chunks (e.g., by sentences)
        # This splitting needs to be robust (handle periods in abbreviations, etc.)
        # Simple split by period for now:
        ability_chunks = [chunk.strip() for chunk in body_text.split('.') if chunk.strip()]

        for chunk in ability_chunks:
            if chunk in processed_text_segments: # Skip if already processed as a keyword
                continue

            chunk = chunk.strip()
            if not chunk: continue

            matched_trigger = False
            for pattern_info in PATTERNS:
                match = pattern_info['regex'].match(chunk) # Use match (starts with)
                if match:
                    trigger = pattern_info['trigger']
                    cost = None
                    effect_text = ""
                    params_from_trigger = pattern_info.get('parameters', {}).copy()

                    if 'effect_text' in match.groupdict() and match.group('effect_text'):
                         effect_text = match.group('effect_text').strip()
                    else:
                         # Handle cases where regex might not have effect_text group but implies one
                         # E.g. the catch-all Continuous pattern
                         effect_text = chunk # Use the whole chunk if no specific effect part

                    # Attempt to parse cost if the pattern expects one (mainly ACTIVATED)
                    if pattern_info['has_cost']:
                        cost_text = ""
                        if 'cost_text' in match.groupdict() and match.group('cost_text'):
                           cost_text = match.group('cost_text').strip()
                           # Remove cost part from effect_text if structure is Cost - Effect
                           if effect_text.startswith(cost_text + '-'):
                               effect_text = effect_text[len(cost_text + '-'):].strip()
                           elif effect_text == cost_text: # If only cost was matched somehow
                               effect_text = "" # No effect text remains
                        cost = parse_cost(cost_text) # Parse the extracted cost text

                    # If cost parsing failed for ACTIVATED, maybe it's not an activated ability after all?
                    if trigger == TriggerCondition.ACTIVATED and cost is None:
                       # This might be a misclassification by the regex, potentially skip or reconsider trigger?
                       # For now, we proceed but log a warning.
                       # print(f"Warning: ACTIVATED trigger matched, but no cost parsed for: '{chunk}'")
                       pass # Continue processing as activated with no cost (might be wrong)


                    # Parse the extracted effect text into Effect objects
                    effects = parse_effects(effect_text)

                    # Add trigger parameters to the first effect if relevant
                    if effects and params_from_trigger:
                        effects[0].parameters.update(params_from_trigger) # Merge dicts


                    # Add the parsed ability
                    parsed_abilities.append(Ability(
                        trigger=trigger,
                        cost=cost,
                        effects=effects,
                        source_text=chunk
                    ))
                    processed_text_segments.add(chunk)
                    matched_trigger = True
                    break # Move to the next chunk once a trigger pattern is matched

            # If no pattern matched (should only happen if PATTERNS is incomplete)
            # The CONTINUOUS catch-all should always match if reached.
            # if not matched_trigger:
            #     print(f"Debug: No trigger pattern matched chunk: '{chunk}'")


    # 3. Final filtering/cleanup (e.g., remove redundant CONTINUOUS if specific triggers found?)
    # Example: If a card has "Rush" keyword and also "When you play this character..."
    # both might generate abilities. This is usually correct.

    return parsed_abilities


# --- Example Usage ---
if __name__ == '__main__':
    print("--- Parsing Examples ---")

    # Example 1: Gaston - Pure Paragon
    gaston_body = "For each damaged character you have in play, you pay 2 {i} less to play this character. Rush"
    gaston_abilities = "Rush" # Often keywords are duplicated
    print(f"\nParsing: Gaston - Pure Paragon")
    gaston_parsed = parse_abilities(gaston_body, gaston_abilities)
    for ability in gaston_parsed: print(ability)
    # Expected: A KEYWORD_RUSH Ability. The cost reduction is complex - currently likely parsed as CONTINUOUS effect. Needs specific handling.

    # Example 2: Robin Hood - Sharpshooter
    robin_body = "Whenever this character quests, look at the top 4 cards of your deck. You may reveal an action card with cost 6 or less and play it for free. Put the rest in your discard."
    robin_abilities = None
    print(f"\nParsing: Robin Hood - Sharpshooter")
    robin_parsed = parse_abilities(robin_body, robin_abilities)
    for ability in robin_parsed: print(ability)
    # Expected: ON_QUEST trigger. Effect parsing needs improvement to capture the sequence.

    # Example 3: Activated Ability
    activated_body = "{e}, 2{i} - Draw a card."
    activated_abilities = None
    print(f"\nParsing: Activated Draw")
    activated_parsed = parse_abilities(activated_body, activated_abilities)
    for ability in activated_parsed: print(ability)
    # Expected: ACTIVATED trigger, cost parsed, DRAW_CARD effect.

    # Example 4: Simple Keyword
    rush_body = None # Sometimes body is null if only keywords
    rush_abilities = "Rush"
    print(f"\nParsing: Simple Rush")
    rush_parsed = parse_abilities(rush_body, rush_abilities)
    for ability in rush_parsed: print(ability)
    # Expected: KEYWORD_RUSH Ability.

    # Example 5: Continuous Aura
    aura_body = "Your other characters get +1 {s}."
    aura_abilities = None
    print(f"\nParsing: Strength Aura")
    aura_parsed = parse_abilities(aura_body, aura_abilities)
    for ability in aura_parsed: print(ability)
    # Expected: CONTINUOUS trigger, MODIFY_STATS effect. Needs target refinement.
