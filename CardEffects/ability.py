from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from CardEffects.effects_Definitions import TriggerCondition, EffectType, TargetType


@dataclass
class Effect:
    """Represents a single game action resulting from an ability."""

    effect_type: EffectType  # What kind of action? (e.g., DEAL_DAMAGE, DRAW_CARD)
    target: TargetType  # Who/what does it affect by default?
    parameters: Dict[str, Any] = field(default_factory=dict)  # Details for the effect

    def __str__(self):
        param_str = ", ".join(f"{k}={v}" for k, v in self.parameters.items())
        return f"Effect({self.effect_type.name}, target={self.target.name}, params=[{param_str}])"

    def get_param(self, key: str, default=None):
        """Safely get a parameter value with a default if not present."""
        return self.parameters.get(key, default)


@dataclass
class AbilityCost:
    """Represents the cost required to activate an ability."""

    ink_cost: int = 0  # Ink required
    exert_self: bool = False  # Does activating require exerting the card
    discard_card: bool = False  # Does activating require discarding a card
    damage_card: bool = (
        False  # Does activating require dealing damage to your own character
    )
    banish_card: bool = False  # Does activating require banishing your own character

    def is_free(self) -> bool:
        """Check if the ability has any cost."""
        return (
            self.ink_cost == 0
            and not self.exert_self
            and not self.discard_card
            and not self.damage_card
            and not self.banish_card
        )

    def __str__(self):
        parts = []
        if self.exert_self:
            parts.append("{e}")
        if self.ink_cost > 0:
            parts.append(f"{self.ink_cost}{{i}}")
        if self.discard_card:
            parts.append("discard a card")
        if self.damage_card:
            parts.append("damage this character")
        if self.banish_card:
            parts.append("banish a character")
        return ", ".join(parts) if parts else "Free"


@dataclass
class Ability:
    """
    Represents a single parsed ability or keyword effect from a card's text.
    """

    trigger: TriggerCondition  # When does this ability activate or apply?
    effects: List[Effect]  # What are the ordered effects that occur?
    cost: Optional[AbilityCost] = (
        None  # What is the cost to use this ability (if applicable)?
    )
    source_text: Optional[str] = None  # The original text snippet this was parsed from
    is_dynamic: bool = False  # Flag for abilities that need additional processing

    def __str__(self):
        cost_str = (
            f" Cost: {self.cost}" if self.cost and not self.cost.is_free() else ""
        )
        effects_str = "; ".join(str(eff) for eff in self.effects)
        return (
            f"Ability(Trigger: {self.trigger.name}{cost_str}, Effects: [{effects_str}])"
        )

    def get_effects_by_type(self, effect_type: EffectType) -> List[Effect]:
        """Get all effects of a specific type."""
        return [effect for effect in self.effects if effect.effect_type == effect_type]

    def has_effect_type(self, effect_type: EffectType) -> bool:
        """Check if this ability has any effect of a specific type."""
        return any(effect.effect_type == effect_type for effect in self.effects)

    def is_keyword(self) -> bool:
        """
        Check if this ability represents a keyword.
        """
        return any(
            self.trigger == trigger
            for trigger in [
                TriggerCondition.KEYWORD_RUSH,
                TriggerCondition.KEYWORD_BODYGUARD,
                TriggerCondition.KEYWORD_EVASIVE,
                TriggerCondition.KEYWORD_RECKLESS,
                TriggerCondition.KEYWORD_RESIST,
                TriggerCondition.KEYWORD_CHALLENGER,
                TriggerCondition.KEYWORD_SHIFT,
                TriggerCondition.KEYWORD_SINGER,
                TriggerCondition.KEYWORD_SUPPORT,
                TriggerCondition.KEYWORD_VANISH,
                TriggerCondition.KEYWORD_WARD,
                TriggerCondition.SING_TOGETHER,
            ]
        )
