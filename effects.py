from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import re
from card import Card
from effects_Definitions import TriggerCondition, EffectType, TargetType

@dataclass
class EffectCost:
    """Represents the cost required to activate an ability."""
    ink: int = 0
    exert: bool = False

@dataclass
class EffectData:
    """Represents a parsed game effect or ability."""
    original_text: str                    # The raw text for reference/debugging
    trigger: TriggerCondition
    effect_type: EffectType
    target: TargetType = TargetType.NONE  # Default to none if not applicable

    # Parameters specific to the effect (flexible storage)
    parameters: Dict[str, Any] = field(default_factory=dict)
    # Examples of parameters:
    # 'amount': 1 (for draw, damage, lore, stats modifier)
    # 'keyword': Keyword.EVASIVE (for grant/remove keyword)
    # 'duration': 'turn' / 'permanent' (for stat mods, restrictions)
    # 'target_filter': {'type': 'Character', 'color': 'Amber', 'cost': 3} (for targeting specifics)
    # 'stat': 'strength' / 'willpower' (for modify stats)

    # Cost associated with ACTIVATED abilities
    cost: Optional[EffectCost] = None

    # Optional: Link back to the card source if needed, though usually managed by game state
    # source_card_id: Optional[str] = None

    def __str__(self) -> str:
        # Simple string representation for debugging
        cost_str = f" Cost: {self.cost}" if self.cost else ""
        return f"[{self.trigger.name}] -> {self.effect_type.name} ({self.target.name}) Params: {self.parameters}{cost_str}"
# --- Keyword Mapping (Example - expand significantly) ---
KEYWORD_MAP = {
    "Evasive": EffectData(trigger=TriggerCondition.KEYWORD_EVASIVE, effect_type=EffectType.GRANT_KEYWORD, parameters={'keyword': 'Evasive'}, original_text="Evasive"),
    "Rush": EffectData(trigger=TriggerCondition.KEYWORD_RUSH, effect_type=EffectType.GRANT_KEYWORD, parameters={'keyword': 'Rush'}, original_text="Rush"),
    "Ward": EffectData(trigger=TriggerCondition.KEYWORD_WARD, effect_type=EffectType.GRANT_KEYWORD, parameters={'keyword': 'Ward'}, original_text="Ward"),
    # ... add other simple keywords
}

# --- Regex Patterns (Examples - expand significantly) ---
# Simple trigger examples
ON_PLAY_REGEX = re.compile(r"^When you play this character, (.*)", re.IGNORECASE)
ON_QUEST_REGEX = re.compile(r"^Whenever this character quests, (.*)", re.IGNORECASE)
ACTIVATED_REGEX = re.compile(r"^{e}(?:,\s*(\d+){i})?\s*-\s*(.*)", re.IGNORECASE | re.DOTALL) # Matches {e} - Effect, captures optional ink cost

# Simple effect examples
DRAW_CARD_REGEX = re.compile(r"draw (\d+|a) card", re.IGNORECASE) # Matches "draw a card" or "draw X cards"
GAIN_LORE_REGEX = re.compile(r"gain (\d+) lore", re.IGNORECASE)
DEAL_DAMAGE_REGEX = re.compile(r"deal (\d+) damage to chosen (character|location)", re.IGNORECASE)
STAT_MOD_REGEX = re.compile(r"gets ([+\-]\d+) {([swl])}", re.IGNORECASE) # e.g., "+2 {s}"

class EffectParser:

    def parse_effects(self, card: Card) -> List[EffectData]:
        """Parses abilities and body text into EffectData objects."""
        parsed_effects: List[EffectData] = []

        # 1. Parse Keywords from abilities list
        for ability_str in card.abilities:
            # Handle keywords with values (Singer, Shift, Resist, Challenger)
            match_singer = re.match(r"Singer (\d+)", ability_str, re.IGNORECASE)
            match_shift = re.match(r"Shift (\d+)", ability_str, re.IGNORECASE)
            # ... add patterns for Resist +N, Challenger +N ...

            if match_singer:
                amount = int(match_singer.group(1))
                parsed_effects.append(EffectData(
                    original_text=ability_str,
                    trigger=TriggerCondition.KEYWORD_SINGER,
                    effect_type=EffectType.MODIFY_COST_TO_PLAY, # Or a specific Singer effect type
                    parameters={'keyword': 'Singer', 'amount': amount}
                ))
            elif match_shift:
                 amount = int(match_shift.group(1))
                 parsed_effects.append(EffectData(
                     original_text=ability_str,
                     trigger=TriggerCondition.KEYWORD_SHIFT,
                     effect_type=EffectType.MODIFY_COST_TO_PLAY, # Shift is an alternate cost
                     parameters={'keyword': 'Shift', 'amount': amount} # Store shift cost
                 ))
            # --- Add elif blocks for Resist, Challenger ---
            elif ability_str in KEYWORD_MAP:
                 # Simple keyword mapping (create copies to avoid modification issues)
                 effect_template = KEYWORD_MAP[ability_str]
                 parsed_effects.append(EffectData(
                     original_text=effect_template.original_text,
                     trigger=effect_template.trigger,
                     effect_type=effect_template.effect_type,
                     target=effect_template.target,
                     parameters=effect_template.parameters.copy(), # Important: copy dict
                     cost=effect_template.cost # Cost is usually None here
                 ))
            else:
                 print(f"Warning: Unmapped keyword '{ability_str}' for card '{card.name}'")
                 # Optionally create a placeholder EffectData
                 parsed_effects.append(EffectData(original_text=ability_str, trigger=TriggerCondition.OTHER, effect_type=EffectType.OTHER))


        # 2. Parse Body Text (Basic Example)
        if card.body_text:
            # Split body text into potential multiple abilities (e.g., by newline '\n')
            ability_texts = card.body_text.split('\n')
            for text_part in ability_texts:
                text_part = text_part.strip()
                if not text_part or text_part.lower().startswith("("): # Skip empty lines or reminder text in parenthesis
                     continue

                effect = self.parse_single_text_ability(text_part, card.name)
                if effect:
                    parsed_effects.append(effect)
                # else: # Handle cases where parsing failed for a line
                #    print(f"Debug: Could not parse text part: '{text_part}' for card '{card.name}'")
                #    parsed_effects.append(EffectData(original_text=text_part, trigger=TriggerCondition.OTHER, effect_type=EffectType.OTHER))

        return parsed_effects

    def parse_single_text_ability(self, text: str, card_name_for_debug: str) -> Optional[EffectData]:
        """Parses a single line/clause of ability text."""
        original_text = text # Keep original for the EffectData

        # --- Try matching triggers ---
        trigger = TriggerCondition.CONTINUOUS # Default assumption unless specified
        cost = None
        effect_text = text # Assume the whole text is the effect initially

        # Check for Activated Ability first ({e} - ...)
        match_activated = ACTIVATED_REGEX.match(text)
        if match_activated:
            trigger = TriggerCondition.ACTIVATED
            ink_cost = int(match_activated.group(1)) if match_activated.group(1) else 0
            cost = EffectCost(ink=ink_cost, exert=True)
            effect_text = match_activated.group(2).strip() # Text after the trigger
            print(f"DEBUG PARSER ({card_name_for_debug}): Found ACTIVATED trigger. Cost: {cost}. Effect text: '{effect_text}'")

        # Add elif blocks for ON_PLAY_REGEX, ON_QUEST_REGEX, etc.
        # elif ON_PLAY_REGEX.match(text):
        #     trigger = TriggerCondition.ON_PLAY
        #     effect_text = ON_PLAY_REGEX.match(text).group(1).strip()
        #     print(f"DEBUG PARSER ({card_name_for_debug}): Found ON_PLAY trigger. Effect text: '{effect_text}'")
        # ... many more trigger patterns ...

        # --- Now parse the effect_text based on the identified trigger ---
        effect_type = EffectType.OTHER # Default
        target = TargetType.NONE
        parameters = {}

        # Example: Parse Draw Card
        match_draw = DRAW_CARD_REGEX.search(effect_text)
        if match_draw:
            effect_type = EffectType.DRAW_CARD
            amount_str = match_draw.group(1).lower()
            parameters['amount'] = 1 if amount_str == 'a' else int(amount_str)
            target = TargetType.SELF_PLAYER # Drawing usually affects self
            print(f"DEBUG PARSER ({card_name_for_debug}): Parsed DRAW_CARD. Amount: {parameters['amount']}")

        # Example: Parse Gain Lore
        match_lore = GAIN_LORE_REGEX.search(effect_text)
        elif match_lore:
            effect_type = EffectType.GAIN_LORE
            parameters['amount'] = int(match_lore.group(1))
            target = TargetType.SELF_PLAYER
            print(f"DEBUG PARSER ({card_name_for_debug}): Parsed GAIN_LORE. Amount: {parameters['amount']}")

        # Example: Parse Stat Mod
        match_stat = STAT_MOD_REGEX.search(effect_text)
        elif match_stat:
             effect_type = EffectType.MODIFY_STATS
             amount = int(match_stat.group(1))
             stat_char = match_stat.group(2).lower()
             stat_map = {'s': 'strength', 'w': 'willpower', 'l': 'lore'}
             if stat_char in stat_map:
                  parameters['stat'] = stat_map[stat_char]
                  parameters['amount'] = amount
                  # Crude target assumption - needs refinement
                  if "chosen character" in effect_text.lower():
                       target = TargetType.TARGET_CHARACTER_CHOSEN
                  elif "your other characters" in effect_text.lower():
                       target = TargetType.ALL_OWN_CHARACTERS
                  else: # Assume self? Needs better logic
                       target = TargetType.SELF_CARD
                  # TODO: Parse duration (e.g., "this turn")
                  parameters['duration'] = 'turn' # Placeholder
                  print(f"DEBUG PARSER ({card_name_for_debug}): Parsed MODIFY_STATS. Stat: {parameters['stat']}, Amount: {amount}")
             else:
                  print(f"Warning ({card_name_for_debug}): Unknown stat char '{stat_char}' in '{original_text}'")
                  effect_type = EffectType.OTHER # Fallback


        # ... Add many more effect parsing patterns ...

        # If we successfully identified an effect type other than OTHER, create the EffectData
        if effect_type != EffectType.OTHER:
            return EffectData(
                original_text=original_text,
                trigger=trigger,
                effect_type=effect_type,
                target=target,
                parameters=parameters,
                cost=cost
            )
        # If no specific effect was parsed from this text part, return None or a placeholder
        # print(f"DEBUG PARSER ({card_name_for_debug}): Could not parse effect type from: '{effect_text}'")
        return EffectData(original_text=original_text, trigger=trigger, effect_type=EffectType.OTHER) # Return placeholder


# --- Integration Point ---
# This function would ideally be called within card.py after a Card object is created,
# or perhaps within the parse_card_data function itself.

def populate_card_effects(card: Card):
    """Parses and adds EffectData to a Card object."""
    if EffectData is None: return # Skip if EffectData couldn't be imported

    parser = EffectParser()
    card.parsed_effects = parser.parse_effects(card)
    # Optional: Print parsed effects for debugging
    # if card.parsed_effects:
    #     print(f"Parsed effects for {card.name}:")
    #     for effect in card.parsed_effects:
    #         print(f"  - {effect}")
