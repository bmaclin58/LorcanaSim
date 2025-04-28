from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from effects_Definitions import TriggerCondition, EffectType, TargetType

# Define Effect structure first (as Ability references it)
@dataclass
class Effect:
    """Represents a single game action resulting from an ability."""
    effect_type: EffectType             # What kind of action? (e.g., DEAL_DAMAGE, DRAW_CARD)
    target: TargetType                  # Who/what does it affect by default? (e.g., TARGET_CHARACTER_CHOSEN)
    parameters: Dict[str, Any] = field(default_factory=dict) # Details (e.g., {'amount': 2}, {'keyword': 'Evasive', 'duration': 'turn'})

    def __str__(self):
        # Basic string representation for debugging
        param_str = ', '.join(f"{k}={v}" for k, v in self.parameters.items())
        return f"Effect({self.effect_type.name}, target={self.target.name}, params=[{param_str}])"

@dataclass
class AbilityCost:
    """Represents the cost required to activate an ability."""
    ink_cost: int = 0          # Ink required
    exert_self: bool = False   # Does activating require exerting the card
    discard_card: bool = False # Does activating require discarding a card
    damage_card: bool = False  # Does activating require dealing damage to your own character
    banish_card: bool = False  # Does activating require banishing your own character

    def is_free(self) -> bool:
        """Check if the ability has any cost."""
        return self.ink_cost == 0 and not self.exert_self

    def __str__(self):
        parts = []
        if self.exert_self:
            parts.append("{e}")
        if self.ink_cost > 0:
            parts.append(f"{self.ink_cost}") # Assuming {i} symbol for ink
        return ", ".join(parts) if parts else "Free"

@dataclass
class Ability:
    """
    Represents a single parsed ability or keyword effect from a card's text.
    """
    trigger: TriggerCondition           # When does this ability activate or apply?
    effects: List[Effect]               # What are the ordered effects that occur?
    cost: Optional[AbilityCost] = None  # What is the cost to use this ability (if applicable, e.g., for ACTIVATED triggers)?
    source_text: Optional[str] = None   # The original text snippet this was parsed from (for debugging/reference)

    def __str__(self):
        cost_str = f" Cost: {self.cost}" if self.cost and not self.cost.is_free() else ""
        effects_str = '; '.join(str(eff) for eff in self.effects)
        return f"Ability(Trigger: {self.trigger.name}{cost_str}, Effects: [{effects_str}])"

# --- Example Usage (Conceptual) ---
if __name__ == '__main__':
    # Example: Robin Hood - Sharpshooter's ability
    robin_hood_ability = Ability(
        trigger=TriggerCondition.ON_QUEST,
        effects=[
            Effect(effect_type=EffectType.LOOK_AT_TOP_CARDS, target=TargetType.SELF_PLAYER, parameters={'amount': 4}),
            Effect(effect_type=EffectType.PLAY_CARD, target=TargetType.SELF_PLAYER, parameters={'source_zone': 'looked_at_cards', 'card_filter': {'type': 'Action', 'max_cost': 6}, 'cost_override': 0}),
            Effect(effect_type=EffectType.MOVE_TO_ZONE, target=TargetType.LOOKED_AT_CARDS, parameters={'destination_zone': 'discard', 'filter': 'remaining'}) # 'remaining' needs defined handling
        ],
        source_text="Whenever this character quests, look at the top 4 cards of your deck..."
    )
    print(robin_hood_ability)

    # Example: Activated ability "{e}, 2{i} - Draw a card"
    draw_ability = Ability(
        trigger=TriggerCondition.ACTIVATED,
        cost=AbilityCost(ink_cost=2, exert_self=True),
        effects=[
            Effect(effect_type=EffectType.DRAW_CARD, target=TargetType.SELF_PLAYER, parameters={'amount': 1})
        ],
        source_text="{e}, 2{i} - Draw a card"
    )
    print(draw_ability)

    # Example: Static Keyword "Rush"
    rush_keyword = Ability(
        trigger=TriggerCondition.KEYWORD_RUSH,
        effects=[] # Keywords often modify rules directly, effects list might be empty unless it grants another effect
    )
    print(rush_keyword)

    # Example: Static Ability "Your other characters get +1{s}"
    strength_aura = Ability(
        trigger=TriggerCondition.CONTINUOUS,
        effects=[
            Effect(effect_type=EffectType.MODIFY_STATS, target=TargetType.ALL_OWN_CHARACTERS, parameters={'stat': 'strength', 'modifier': +1, 'filter': 'other'}) # 'other' filter needed
        ]
    )
    print(strength_aura)
