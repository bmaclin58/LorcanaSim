import re
from typing import List, Optional, Dict, Any

from CardEffects.ability import Ability, AbilityCost, Effect
from CardEffects.effects_Definitions import EffectType, TargetType, TriggerCondition

# --- Trigger Parsing Patterns ---
PATTERNS = [
    # 1. Activated (manual-cost) abilities
    # Activated Abilities with costs
    {
        "regex": re.compile(
            r"^(?P<cost_text>.*?)-\s*(?P<effect_text>.*)", re.IGNORECASE | re.DOTALL
        ),
        "trigger": TriggerCondition.ACTIVATED,
        "has_cost": True,
    },
    {
        "regex": re.compile(
            r"^(?P<cost>(?:exert|shift|\d+ink|Banish[^-]+))(?:[, ]+-)\s*(?P<effect>.*)$",
            re.IGNORECASE | re.DOTALL,
        ),
        "trigger": TriggerCondition.ACTIVATED,
        "has_cost": True,
    },
    # 2. On-Play effects
    {
        "regex": re.compile(
            r"^When you play (?:this character|an action|an item|a location),?\s*(?P<effect>.*)",
            re.IGNORECASE | re.DOTALL,
        ),
        "trigger": TriggerCondition.ON_PLAY,
        "has_cost": False,
    },
    # 3a. Quest triggers
    {
        "regex": re.compile(
            r"^Whenever this character quests,?\s*(?P<effect>.*)",
            re.IGNORECASE | re.DOTALL,
        ),
        "trigger": TriggerCondition.ON_QUEST,
        "has_cost": False,
    },
    # 3b. Challenge triggers
    {
        "regex": re.compile(
            r"^Whenever this character challenges another character,?\s*(?P<effect>.*)",
            re.IGNORECASE | re.DOTALL,
        ),
        "trigger": TriggerCondition.ON_CHALLENGE,
        "has_cost": False,
    },
    # 3c. Being challenged
    {
        "regex": re.compile(
            r"^Whenever this character is challenged,?\s*(?P<effect>.*)",
            re.IGNORECASE | re.DOTALL,
        ),
        "trigger": TriggerCondition.ON_BEING_CHALLENGED,
        "has_cost": False,
    },
    # 3d. Banish triggers
    {
        "regex": re.compile(
            r"^Whenever this character is banished,?\s*(?P<effect>.*)",
            re.IGNORECASE | re.DOTALL,
        ),
        "trigger": TriggerCondition.ON_BANISH,
        "has_cost": False,
    },
    # 3e. Ready triggers
    {
        "regex": re.compile(
            r"^Whenever you ready this character,?\s*(?P<effect>.*)",
            re.IGNORECASE | re.DOTALL,
        ),
        "trigger": TriggerCondition.ON_READY,
        "has_cost": False,
    },
    # Time-based triggers (start/end of turn)
    {
        "regex": re.compile(
            r"^At the (start|end) of your turn,?\s*(?P<effect_text>.*)",
            re.IGNORECASE | re.DOTALL,
        ),
        "trigger": TriggerCondition.DYNAMIC_TURN_TRIGGER,
        "has_cost": False,
        "dynamic_mapping": {
            "start": TriggerCondition.START_OF_TURN,
            "end": TriggerCondition.END_OF_TURN,
        },
    },
    # 5. “Whenever a card event” (inkwell/draw/discard/damage)
    {
        "regex": re.compile(
            r"^Whenever (?:a card is put into your inkwell|you draw a card|you remove \d+ damage|you discard).*?,?\s*(?P<effect>.*)",
            re.IGNORECASE | re.DOTALL,
        ),
        "trigger": TriggerCondition.GENERAL_WHENEVER,
        "has_cost": False,
    },
    # 6a. “While” continuous conditions
    {
        "regex": re.compile(
            r"^While (?:you have|you have more|this character has)[^,]+,\s*(?P<effect>.*)",
            re.IGNORECASE | re.DOTALL,
        ),
        "trigger": TriggerCondition.DYNAMIC_CONDITION,
        "has_cost": False,
    },
    # Conditional phrases (During/While)
    {
        "regex": re.compile(
            r"^(During|While) (your turn|an opponent's turn|this character is at a location|this character is exerted|this character (?P<condition>.*?)),?\s*(?P<effect_text>.*)",
            re.IGNORECASE | re.DOTALL,
        ),
        "trigger": TriggerCondition.DYNAMIC_CONDITION,
        "has_cost": False,
        "dynamic_mapping": {
            "your turn": TriggerCondition.ON_YOUR_TURN,
            "an opponent's turn": TriggerCondition.DURING_TURN,
            "this character is at a location": TriggerCondition.WHILE_AT_LOCATION,
        },
    },
    # 6b. Static keyword grants / continuous buffs
    {
        "regex": re.compile(
            r"^(Your [A-Za-z ]+ characters get [+-]\d+ [A-Za-z ]+)\.?$", re.IGNORECASE
        ),
        "trigger": TriggerCondition.STATIC_BONUS,
        "has_cost": False,
    },
    # "Once per/during" triggers
    {
        "regex": re.compile(
            r"^Once (per|during) your turn,\s*(?P<effect_text>.*)",
            re.IGNORECASE | re.DOTALL,
        ),
        "trigger": TriggerCondition.ONCE_PER_TURN,
        "has_cost": False,
    },
    # All character bonuses
    {
        "regex": re.compile(
            r"^(Your other characters|This character|Your (?P<character_type>\w+) characters|Chosen character) (get|gets|gain|gains) (?P<bonus>\+\d+\s+(?P<stat>\w+)|(?P<keyword>Challenger \+\d+|Resist \+\d+|Rush|Evasive|Bodyguard|Ward|Vanish|Support|Reckless))(\s+(this turn|until the start of your next turn))?",
            re.IGNORECASE | re.DOTALL,
        ),
        "trigger": TriggerCondition.DYNAMIC_BONUS,
        "has_cost": False,
        "dynamic_handler": "handle_character_bonus",
    },
    # Conditional effects
    {
        "regex": re.compile(
            r"^(If|While) (you have (?P<condition>.*?)|the challenging character has (?P<challenge_condition>.*?)),\s*(?P<effect_text>.*)",
            re.IGNORECASE | re.DOTALL,
        ),
        "trigger": TriggerCondition.CONDITIONAL_EFFECT,
        "has_cost": False,
    },
    # Enters play and other similar effects
    {
        "regex": re.compile(
            r"^This character (enters play|can't be challenged) (?P<effect_text>.*)?",
            re.IGNORECASE | re.DOTALL,
        ),
        "trigger": TriggerCondition.DYNAMIC_CHARACTER_STATE,
        "has_cost": False,
        "dynamic_mapping": {
            "enters play": TriggerCondition.ENTERS_PLAY_EFFECT,
            "can't be challenged": TriggerCondition.PROTECTION_CHALLENGE,
        },
    },
    {
        "regex": re.compile(
            r"^For each (?P<condition>.+?),\s*you pay\s*(?P<amount>\d+)\s*ink\s*less\s*(?P<effect>.+)$",
            re.IGNORECASE | re.DOTALL,
        ),
        "trigger": TriggerCondition.STATIC_COST_MODIFIER,
        "has_cost": False,
    },
    # Action card effects
    {
        "regex": re.compile(
            r"^(Deal \d+ damage to chosen (character|location)|Remove up to \d+ damage from chosen (character|location)|Draw \d+ Cards|Banish chosen character|Chosen exerted character can't ready at the start of their next turn|Discard \d+ cards|Put all opposing characters with \d+ strength or less on the bottom of their player's decks)$",
            re.IGNORECASE | re.DOTALL,
        ),
        "trigger": TriggerCondition.SIMPLE_ACTION_EFFECT,
        "has_cost": False,
    },
    # Win condition modifier
    {
        "regex": re.compile(
            r"^Opponents (need \d+ lore to win the game)\.",
            re.IGNORECASE | re.DOTALL,
        ),
        "trigger": TriggerCondition.WIN_CONDITION_MODIFIER,
        "has_cost": False,
    },
    # Named character effects
    {
        "regex": re.compile(
            r"^Your characters named (?P<character_name>\w+) (gain|get) (?P<effect>.*?)$",
            re.IGNORECASE | re.DOTALL,
        ),
        "trigger": TriggerCondition.NAMED_CHARACTER_EFFECT,
        "has_cost": False,
    },
    # 7. Catch-all
    {
        "regex": re.compile(r"^(?P<effect>.*)$", re.IGNORECASE | re.DOTALL),
        "trigger": TriggerCondition.OTHER,
        "has_cost": False,
    },
]

# --- Effect Parsing Patterns ---
EFFECT_PATTERNS = [
    # Draw cards
    {
        'regex': re.compile(r"(you may )?(draw|Draw) (?P<amount>\d+|a) card", re.IGNORECASE),
        'effect_type': EffectType.DRAW_CARD,
        'target': TargetType.SELF_PLAYER,
        'params': {'amount': 1}
    },
    # Gain lore
    {
        'regex': re.compile(r"gain (?P<amount>\d+) lore", re.IGNORECASE),
        'effect_type': EffectType.GAIN_LORE,
        'target': TargetType.SELF_PLAYER
        },
    
    # Lose lore
    {
        'regex': re.compile(r"(each opponent |opponents )?(loses|lose) (?P<amount>\d+) lore", re.IGNORECASE),
        'effect_type': EffectType.LOSE_LORE,
        'target': TargetType.OPPONENT_PLAYER
        },
    
    # Deal damage
    {
        'regex': re.compile(r"deal (?P<amount>\d+) damage to chosen (?P<target_type>character|location)", re.IGNORECASE),
        'effect_type': EffectType.DEAL_DAMAGE
        },
    
    # Heal damage
    {
        'regex': re.compile(r"remove( up to)? (?P<amount>\d+) damage from chosen (?P<target_type>character|location)", re.IGNORECASE),
        'effect_type': EffectType.HEAL_DAMAGE
        },
    
    # Stat modification
    {
        'regex': re.compile(r"(gets|get|gains|gain) (?P<mod>[+\-]\d+) ((\{(?P<stat>[swl])})|((?P<stat_text>strength|willpower|lore)))", re.IGNORECASE),
        'effect_type': EffectType.MODIFY_STATS,
        'target': TargetType.SELF_CARD
        },
    
    # Add keyword
    {
        'regex': re.compile(r"(gains|gain) (?P<keyword>Challenger \+\d+|Resist \+\d+|Rush|Evasive|Bodyguard|Ward|Vanish|Support|Reckless)", re.IGNORECASE),
        'effect_type': EffectType.GRANT_KEYWORD
        },
    
    # Prevent actions
    {
        'regex': re.compile(r"(opponents|chosen character) can't (?P<action>play actions|ready|challenge|be challenged|quest)", re.IGNORECASE),
        'effect_type': EffectType.PREVENT_ACTION
        },
    
    # Look at top cards
    {
        'regex': re.compile(r"look at the top (?P<amount>\d+) cards of (your|an opponent's) deck", re.IGNORECASE),
        'effect_type': EffectType.LOOK_AT_TOP_CARDS
        },
    
    # Play card from zone
    {
        'regex': re.compile(r"(you may )?(reveal|play) (an? )?(?P<card_type>\w+) card( with (?P<condition>.*?))?( and play it( for free)?)?", re.IGNORECASE),
        'effect_type': EffectType.PLAY_CARD,
        'target': TargetType.LOOKED_AT_CARDS
        },
    
    # Bottom of deck effect
    {
        'regex': re.compile(r"put (all|the rest|the remaining cards|chosen character) (?P<filter>.*?) (on|in) (the bottom of|your discard|their player's decks)", re.IGNORECASE),
        'effect_type': EffectType.PUT_ON_BOTTOM
        },
    ]

# --- Keyword Pattern Recognition ---
KEYWORD_PATTERNS = [
    {'regex': re.compile(r"^Rush$", re.IGNORECASE), 'keyword': 'Rush', 'trigger': TriggerCondition.KEYWORD_RUSH, 'has_value': False},
    {'regex': re.compile(r"^Bodyguard$", re.IGNORECASE), 'keyword': 'Bodyguard', 'trigger': TriggerCondition.KEYWORD_BODYGUARD, 'has_value': False},
    {'regex': re.compile(r"^Evasive$", re.IGNORECASE), 'keyword': 'Evasive', 'trigger': TriggerCondition.KEYWORD_EVASIVE, 'has_value': False},
    {'regex': re.compile(r"^Ward$", re.IGNORECASE), 'keyword': 'Ward', 'trigger': TriggerCondition.KEYWORD_WARD, 'has_value': False},
    {'regex': re.compile(r"^Vanish$", re.IGNORECASE), 'keyword': 'Vanish', 'trigger': TriggerCondition.KEYWORD_VANISH, 'has_value': False},
    {'regex': re.compile(r"^Reckless$", re.IGNORECASE), 'keyword': 'Reckless', 'trigger': TriggerCondition.KEYWORD_RECKLESS, 'has_value': False},
    {'regex': re.compile(r"^Challenger \+(?P<amount>\d+)$", re.IGNORECASE), 'keyword': 'Challenger', 'trigger': TriggerCondition.KEYWORD_CHALLENGER, 'has_value': True},
    {'regex': re.compile(r"^Resist \+(?P<amount>\d+)$", re.IGNORECASE), 'keyword': 'Resist', 'trigger': TriggerCondition.KEYWORD_RESIST, 'has_value': True},
    {'regex': re.compile(r"^Shift (?P<amount>\d+)$", re.IGNORECASE), 'keyword': 'Shift', 'trigger': TriggerCondition.KEYWORD_SHIFT, 'has_value': True},
    {'regex': re.compile(r"^Singer (?P<amount>\d+)$", re.IGNORECASE), 'keyword': 'Singer', 'trigger': TriggerCondition.KEYWORD_SINGER, 'has_value': True},
    {'regex': re.compile(r"^Support$", re.IGNORECASE), 'keyword': 'Support', 'trigger': TriggerCondition.KEYWORD_SUPPORT, 'has_value': False},
    {'regex': re.compile(r"^Sing Together (?P<amount>\d+)$", re.IGNORECASE), 'keyword': 'Sing Together', 'trigger': TriggerCondition.SING_TOGETHER, 'has_value': True},
    ]

# --- Helper Functions ---

def handle_keywords(result: Dict[str, Any], match) -> Dict[str, Any]:
    """
    Processes keyword matches to determine whether it's a single keyword or multiple keywords.
    Also handles keywords with numeric values.
    """
    keyword1 = match.group('keyword1')
    keyword2 = match.group('keyword2') if 'keyword2' in match.groupdict() and match.group('keyword2') else None
    
    # Store all detected keywords
    result["keywords"] = []
    
    # Process first keyword
    keyword_info = process_single_keyword(keyword1)
    result["keywords"].append(keyword_info)
    
    # If there's a second keyword, process it too
    if keyword2:
        result["trigger"] = TriggerCondition.MULTIPLE_KEYWORDS
        keyword_info = process_single_keyword(keyword2)
        result["keywords"].append(keyword_info)
    else:
        # Use the trigger from the first (and only) keyword
        result["trigger"] = keyword_info["trigger"]
        # Copy any value to the main result
        if "value" in keyword_info:
            result["value"] = keyword_info["value"]
    
    return result

def process_single_keyword(keyword_text: str) -> Dict[str, Any]:
    """Process a single keyword and extract any value it might have."""
    result = {
        "keyword": None,
        "trigger": TriggerCondition.KEYWORD_ONLY,
        "value": None
        }
    
    # Match against known keyword patterns
    for pattern in KEYWORD_PATTERNS:
        match = pattern["regex"].match(keyword_text)
        if match:
            result["keyword"] = pattern["keyword"]
            result["trigger"] = pattern["trigger"]
            
            # Extract value if present
            if pattern["has_value"] and "amount" in match.groupdict():
                try:
                    result["value"] = int(match.group("amount"))
                except (ValueError, TypeError):
                    # Couldn't parse value, leave as None
                    pass
            
            break
    
    # If no pattern matched, store the raw text
    if not result["keyword"]:
        result["keyword"] = keyword_text
    
    return result

def handle_character_bonus(result: Dict[str, Any], match) -> Dict[str, Any]:
    """
    Process character bonus patterns (stat boosts, keyword grants, etc.)
    """
    target_text = match.group(0).lower()
    
    # Determine target
    if "your other characters" in target_text:
        result["trigger"] = TriggerCondition.STATIC_BONUS
        result["target"] = TargetType.ALL_OWN_CHARACTERS
        result["parameters"]["filter"] = "other"
    elif "this character" in target_text:
        result["trigger"] = TriggerCondition.SELF_BONUS
        result["target"] = TargetType.SELF_CARD
    elif "chosen character" in target_text:
        result["trigger"] = TriggerCondition.SIMPLE_ACTION_EFFECT
        result["target"] = TargetType.TARGET_CHARACTER_CHOSEN
    elif "your " in target_text and " characters" in target_text and 'character_type' in match.groupdict():
        result["trigger"] = TriggerCondition.CHARACTER_TYPE_EFFECT
        result["target"] = TargetType.ALL_OWN_CHARACTERS
        result["parameters"]["character_type"] = match.group('character_type')
    
    # Extract stat and bonus value if present
    if 'bonus' in match.groupdict() and match.group('bonus'):
        bonus = match.group('bonus')
        
        # Check if it's a keyword grant
        if 'keyword' in match.groupdict() and match.group('keyword'):
            keyword = match.group('keyword')
            result["effect_type"] = EffectType.GRANT_KEYWORD
            result["parameters"]["keyword"] = keyword
            
            # Extract value if the keyword has one (e.g., Challenger +2)
            value_match = re.search(r"\+(\d+)", keyword)
            if value_match:
                result["parameters"]["value"] = int(value_match.group(1))
        else:
            # It's a stat bonus
            result["effect_type"] = EffectType.MODIFY_STATS
            
            # Extract value
            value_match = re.search(r"\+(\d+)", bonus)
            if value_match:
                result["parameters"]["modifier"] = int(value_match.group(1))
            
            # Extract stat
            if 'stat' in match.groupdict() and match.group('stat'):
                stat_map = {'s': 'strength', 'w': 'willpower', 'l': 'lore'}
                stat = match.group('stat').lower()
                result["parameters"]["stat"] = stat_map.get(stat, stat)
            elif 'stat_text' in match.groupdict() and match.group('stat_text'):
                result["parameters"]["stat"] = match.group('stat_text').lower()
    
    # Check for duration
    if "this turn" in target_text:
        result["parameters"]["duration"] = "this_turn"
    elif "until the start of your next turn" in target_text:
        result["parameters"]["duration"] = "until_next_turn"
    
    return result

def parse_effects(effect_text: str) -> List[Effect]:
    """
    Parses the effect description text into a list of Effect objects.
    Supports multiple effects in sequence and conditional effects.
    """
    effects: List[Effect] = []
    
    # Skip empty text
    if not effect_text or effect_text.strip() == "":
        return effects
    
    # Clean up the text for parsing
    effect_text = effect_text.strip().rstrip('.')
    
    # Split by periods and semicolons to separate multiple effects
    effect_segments = []
    for sentence in effect_text.split('.'):
        sentence = sentence.strip()
        if not sentence:
            continue
        
        # Further split by semicolons
        for segment in sentence.split(';'):
            segment = segment.strip()
            if segment:
                effect_segments.append(segment)
    
    # Process each effect segment
    for segment in effect_segments:
        matched = False
        
        # Process conditional effects (If X, then Y)
        if segment.lower().startswith(('if ', 'when ')):
            # Find the condition/effect split
            parts = re.split(r",\s*", segment, 1)
            if len(parts) > 1:
                condition_text = parts[0]
                conditional_effect_text = parts[1]
                
                # Create a conditional effect wrapper
                conditional_effect = Effect(
                        effect_type=EffectType.CONDITIONAL,
                        target=TargetType.NONE,
                        parameters={
                            'condition_text': condition_text,
                            'nested_effects': parse_effects(conditional_effect_text)
                            }
                        )
                
                effects.append(conditional_effect)
                matched = True
        
        # Try to match standard effect patterns
        if not matched:
            for pattern in EFFECT_PATTERNS:
                match = pattern['regex'].search(segment)
                if match:
                    effect_type = pattern['effect_type']
                    
                    # Determine target
                    if 'target' in pattern:
                        target_type = pattern['target']
                    else:
                        # Handle targets differently based on context
                        if 'target_type' in match.groupdict() and match.group('target_type'):
                            target_str = match.group('target_type').lower()
                            if target_str == 'character':
                                target_type = TargetType.TARGET_CHARACTER_CHOSEN
                            elif target_str == 'location':
                                target_type = TargetType.TARGET_LOCATION_CHOSEN
                            else:
                                target_type = TargetType.OTHER
                        else:
                            # Default target based on effect type
                            target_type = TargetType.SELF_CARD
                    
                    # Build parameters from match groups
                    params = pattern.get('params', {}).copy()
                    
                    for key, value in match.groupdict().items():
                        if value is not None:
                            if key == 'amount':
                                if value.isdigit():
                                    params[key] = int(value)
                                elif value.lower() == 'a':
                                    params[key] = 1
                            elif key == 'mod' and value:
                                params['modifier'] = int(value)
                            elif key == 'stat':
                                stat_map = {'s': 'strength', 'w': 'willpower', 'l': 'lore'}
                                params[key] = stat_map.get(value.lower(), value)
                            elif key == 'stat_text':
                                params['stat'] = value.lower()
                            elif key == 'keyword':
                                params[key] = value
                                # Extract any value from keyword
                                value_match = re.search(r"\+(\d+)", value)
                                if value_match:
                                    params['value'] = int(value_match.group(1))
                            elif key == 'filter' or key == 'condition':
                                params[key] = value
                            elif key == 'action':
                                params[key] = value.lower()
                            elif key == 'card_type':
                                params[key] = value.lower()
                            else:
                                params[key] = value
                    
                    # Create the effect
                    effects.append(Effect(
                            effect_type=effect_type,
                            target=target_type,
                            parameters=params
                            ))
                    
                    matched = True
                    break
        
        # If no pattern matched, create a generic effect
        if not matched and segment:
            effects.append(Effect(
                    effect_type=EffectType.OTHER,
                    target=TargetType.NONE,
                    parameters={'raw_text': segment}
                    ))
    
    return effects

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
    processed_text_segments = set()  # Avoid processing the same text twice
    
    # Process keywords from abilities_text
    if abilities_text:
        # Split keywords (typically comma-separated)
        keyword_texts = [kw.strip() for kw in abilities_text.split(',') if kw.strip()]
        
        for keyword in keyword_texts:
            if keyword in processed_text_segments:
                continue
            
            # Try to match against known keyword patterns
            for pattern in KEYWORD_PATTERNS:
                match = pattern['regex'].fullmatch(keyword)
                if match:
                    # Get the trigger type
                    trigger = pattern['trigger']
                    
                    # Build parameters
                    params = {}
                    if pattern['has_value'] and 'amount' in match.groupdict():
                        try:
                            params['amount'] = int(match.group('amount'))
                        except (ValueError, TypeError):
                            pass
                    
                    # Create the keyword effect
                    effects = [Effect(
                            effect_type=EffectType.GRANT_KEYWORD,
                            target=TargetType.SELF_CARD,
                            parameters={
                                'keyword': pattern['keyword'],
                                **params
                                }
                            )]
                    
                    # Add the ability
                    parsed_abilities.append(Ability(
                            trigger=trigger,
                            effects=effects,
                            cost=None,
                            source_text=keyword
                            ))
                    
                    processed_text_segments.add(keyword)
                    break
    
    # Process body_text for abilities
    if body_text:
        # First check if body_text is just keywords already processed
        if abilities_text and ''.join(filter(str.isalnum, body_text.lower())) == ''.join(filter(str.isalnum, abilities_text.lower())):
            # Skip body_text processing as it's identical to abilities_text
            return parsed_abilities
        
        # Split body text into potential ability chunks
        # This could be improved with proper sentence parsing
        ability_chunks = []
        
        # Handle possible line breaks
        if '\r\n' in body_text:
            lines = body_text.split('\r\n')
            for line in lines:
                line = line.strip()
                if line:
                    # Split further by periods
                    line_chunks = [chunk.strip() for chunk in line.split('.') if chunk.strip()]
                    ability_chunks.extend(line_chunks)
        else:
            # Simple split by period
            ability_chunks = [chunk.strip() for chunk in body_text.split('.') if chunk.strip()]
        
        for chunk in ability_chunks:
            if chunk in processed_text_segments:
                continue
            
            chunk = chunk.strip()
            if not chunk:
                continue
            
            # Match against pattern dictionary
    
    return parsed_abilities

def parse_Keyword_ability ():


# --- Example Usage ---
if __name__ == '__main__':
    # Test cases from the card examples
    print("=== Testing Card Parsing ===")
    
'''
    # Example 1: Tiana - Celebrating Princess
    tiana_body = "While this character is exerted and you have no cards in your hand, opponents can't play actions."
    tiana_abilities = "Resist +2"
    print("\nParsing: Tiana - Celebrating Princess")
    tiana_parsed = parse_abilities(tiana_body, tiana_abilities)
    for ability in tiana_parsed:
        print(ability)

    # Example 2: Charge!
    charge_body = "Chosen character gains Challenger +2 and Resist +2 this turn."
    charge_abilities = "Challenger +2, Resist +2"
    print("\nParsing: Charge!")
    charge_parsed = parse_abilities(charge_body, charge_abilities)
    for ability in charge_parsed:
        print(ability)

    # Example 3: Under the Sea
    sea_body = "Sing Together 8 \r Put all opposing characters with 2 strength or less on the bottom of their player's decks in any order."
    sea_abilities = "Sing Together 8"
    print("\nParsing: Under the Sea")
    sea_parsed = parse_abilities(sea_body, sea_abilities)
    for ability in sea_parsed:
        print(ability)

    # Example 4: Signed Contract
    contract_body = "Whenever an opponent plays a song, you may draw a card."
    contract_abilities = None
    print("\nParsing: Signed Contract")
    contract_parsed = parse_abilities(contract_body, contract_abilities)
    for ability in contract_parsed:
        print(ability)

    # Example 5: Snuggly Duckling
    duckling_body = "Whenever a character with 3 strength or more challenge another character while here, gain 1 lore. If the challenging character has 6 strength or more, gain 3 lore instead."
    duckling_abilities = None
    print("\nParsing: Snuggly Duckling")
    duckling_parsed = parse_abilities(duckling_body, duckling_abilities)
    for ability in duckling_parsed:
        print(ability)
'''
