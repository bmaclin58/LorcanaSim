from typing import Optional

from CardEffects.effects_Definitions import EffectType, TargetType, TriggerCondition
from CardEffects.ability import Effect

# Mapping of keyword names to their effect implementations
KEYWORD_MAP = {
    "Bodyguard": {
        "trigger": TriggerCondition.KEYWORD_BODYGUARD,
        "effect_type": EffectType.GRANT_KEYWORD,
        "target": TargetType.SELF_CARD,
        "parameters": {"keyword": "Bodyguard"},
    },
    "Evasive": {
        "trigger": TriggerCondition.KEYWORD_EVASIVE,
        "effect_type": EffectType.GRANT_KEYWORD,
        "target": TargetType.SELF_CARD,
        "parameters": {"keyword": "Evasive"},
    },
    "Rush": {
        "trigger": TriggerCondition.KEYWORD_RUSH,
        "effect_type": EffectType.GRANT_KEYWORD,
        "target": TargetType.SELF_CARD,
        "parameters": {"keyword": "Rush"},
    },
    "Ward": {
        "trigger": TriggerCondition.KEYWORD_WARD,
        "effect_type": EffectType.GRANT_KEYWORD,
        "target": TargetType.SELF_CARD,
        "parameters": {"keyword": "Ward"},
    },
    "Vanish": {
        "trigger": TriggerCondition.KEYWORD_VANISH,
        "effect_type": EffectType.BANISH_SELF,
        "target": TargetType.SELF_CARD,
        "parameters": {"keyword": "Vanish"},
    },
    "Reckless": {
        "trigger": TriggerCondition.KEYWORD_RECKLESS,
        "effect_type": EffectType.GRANT_KEYWORD,
        "target": TargetType.SELF_CARD,
        "parameters": {"keyword": "Reckless"},
    },
    "Support": {
        "trigger": TriggerCondition.KEYWORD_SUPPORT,
        "effect_type": EffectType.MODIFY_STATS,
        "target": TargetType.TARGET_CHARACTER_CHOSEN,
        "parameters": {"keyword": "Support", "stat": "strength", "duration": "quest"},
    },
    "Challenger": {
        "trigger": TriggerCondition.KEYWORD_CHALLENGER,
        "effect_type": EffectType.MODIFY_STATS,
        "target": TargetType.SELF_CARD,
        "parameters": {
            "keyword": "Challenger",
            "stat": "strength",
            "duration": "challenge",
        },
    },
    "Resist": {
        "trigger": TriggerCondition.KEYWORD_RESIST,
        "effect_type": EffectType.OTHER,
        "target": TargetType.SELF_CARD,
        "parameters": {"keyword": "Resist"},
    },
    "Shift": {
        "trigger": TriggerCondition.KEYWORD_SHIFT,
        "effect_type": EffectType.MODIFY_COST_TO_PLAY,
        "target": TargetType.SELF_CARD,
        "parameters": {"keyword": "Shift"},
    },
    "Singer": {
        "trigger": TriggerCondition.KEYWORD_SINGER,
        "effect_type": EffectType.MODIFY_COST_TO_PLAY,
        "target": TargetType.SELF_CARD,
        "parameters": {"keyword": "Singer"},
    },
    "Sing Together": {
        "trigger": TriggerCondition.SING_TOGETHER,
        "effect_type": EffectType.MODIFY_COST_TO_PLAY,
        "target": TargetType.SELF_CARD,
        "parameters": {"keyword": "Sing Together"},
    },
}


def create_keyword_effect(keyword: str, value: Optional[int] = None) -> Effect:
    """
    Create an Effect object for a keyword based on the mapping.

    Args:
        keyword: The keyword name (e.g., 'Rush', 'Challenger')
        value: Optional numeric value for keywords that have one (e.g., 'Challenger +2')

    Returns:
        An Effect object representing the keyword
    """
    # Check if keyword exists in map
    if keyword not in KEYWORD_MAP:
        # Return a generic keyword effect
        return Effect(
            effect_type=EffectType.GRANT_KEYWORD,
            target=TargetType.SELF_CARD,
            parameters={"keyword": keyword, "value": value},
        )

    # Get the keyword mapping
    keyword_info = KEYWORD_MAP[keyword]

    # Create parameters with value if provided
    parameters = keyword_info["parameters"].copy()
    if value is not None:
        parameters["value"] = value

    # Create the effect
    return Effect(
        effect_type=keyword_info["effect_type"],
        target=keyword_info["target"],
        parameters=parameters,
    )
