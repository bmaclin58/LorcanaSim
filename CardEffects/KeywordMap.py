from effects_Definitions import TriggerCondition, EffectType, TargetType
from effects import EffectData, EffectCost

# --- Keyword Mapping (Focusing on simple keywords first) ---
KEYWORD_MAP = {
    # Keyword: Corresponding EffectData object
    "Bodyguard": EffectData(
        original_text="Bodyguard",
        trigger=TriggerCondition.KEYWORD_BODYGUARD,
        # Bodyguard has two parts: enter exerted (replacement) & challenge restriction (static)
        # Representing this perfectly might need refinement later, maybe two effects?
        # For now, flag it as a keyword effect needing special handling in resolution.
        effect_type=EffectType.GRANT_KEYWORD,
        parameters={'keyword': 'Bodyguard'},
        target=TargetType.SELF_CARD # Affects the card itself
    ),
    "Evasive": EffectData(
        original_text="Evasive",
        trigger=TriggerCondition.KEYWORD_EVASIVE,
        effect_type=EffectType.GRANT_KEYWORD,
        parameters={'keyword': 'Evasive'},
        target=TargetType.SELF_CARD # Evasive affects who can challenge this card
    ),
    "Reckless": EffectData(
        original_text="Reckless",
        trigger=TriggerCondition.KEYWORD_RECKLESS,
        # Reckless prevents questing and forces challenge (static restrictions)
        effect_type=EffectType.GRANT_KEYWORD,
        parameters={'keyword': 'Reckless'},
        target=TargetType.SELF_CARD
    ),
    "Rush": EffectData(
        original_text="Rush",
        trigger=TriggerCondition.KEYWORD_RUSH,
        # Rush removes summoning sickness for challenging (static)
        effect_type=EffectType.GRANT_KEYWORD,
        parameters={'keyword': 'Rush'},
        target=TargetType.SELF_CARD
    ),
    "Support": EffectData(
        original_text="Support",
        trigger=TriggerCondition.KEYWORD_SUPPORT,
        # Support is a triggered ability on quest
        effect_type=EffectType.MODIFY_STATS, # Grants STR temporarily
        parameters={'keyword': 'Support'}, # Resolver needs to know source STR
        # Target is chosen during resolution
        target=TargetType.TARGET_CHARACTER_CHOSEN # Needs specific target logic
    ),
    "Ward": EffectData(
        original_text="Ward",
        trigger=TriggerCondition.KEYWORD_WARD,
        # Ward restricts opponent targeting (static)
        effect_type=EffectType.GRANT_KEYWORD,
        parameters={'keyword': 'Ward'},
        target=TargetType.SELF_CARD
    ),
    "Vanish": EffectData(
        original_text="Vanish",
        trigger=TriggerCondition.KEYWORD_VANISH, # Triggers when chosen by opponent action
        effect_type=EffectType.BANISH_SELF, # Banish this character
        parameters={'keyword': 'Vanish'},
        target=TargetType.SELF_CARD
    ),
    # Adding the remaining keywords from the rules:
    "Challenger": EffectData(
        original_text="Challenger",
        trigger=TriggerCondition.KEYWORD_CHALLENGER,
        effect_type=EffectType.MODIFY_STATS, # Adds strength during challenges
        parameters={'keyword': 'Challenger', 'stat': 'strength', 'duration': 'challenge'},
        target=TargetType.SELF_CARD
    ),
    "Resist": EffectData(
        original_text="Resist",
        trigger=TriggerCondition.KEYWORD_RESIST,
        effect_type=EffectType.OTHER, # Special damage reduction replacement effect
        parameters={'keyword': 'Resist'},
        target=TargetType.SELF_CARD
    ),
    "Shift": EffectData(
        original_text="Shift",
        trigger=TriggerCondition.KEYWORD_SHIFT,
        effect_type=EffectType.MODIFY_COST_TO_PLAY, # Alternate play cost
        parameters={'keyword': 'Shift'},
        target=TargetType.SELF_CARD
    ),
    "Singer": EffectData(
        original_text="Singer",
        trigger=TriggerCondition.KEYWORD_SINGER,
        effect_type=EffectType.MODIFY_COST_TO_PLAY, # Affects song costs
        parameters={'keyword': 'Singer'},
        target=TargetType.SELF_CARD
    ),
    "Sing Together": EffectData(
        original_text="Sing Together",
        trigger=TriggerCondition.OTHER, # Special alternate cost mechanism
        effect_type=EffectType.MODIFY_COST_TO_PLAY,
        parameters={'keyword': 'Sing Together'},
        target=TargetType.SELF_CARD
    )
    # Note: Challenger+N, Resist+N, Shift N, Singer N values are handled separately
    # during parsing in the EffectParser class
}
