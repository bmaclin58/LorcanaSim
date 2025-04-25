from enum import Enum, auto

class TriggerCondition(Enum):
    # --- Keywords / Static Abilities ---
    ON_SING = auto()
    KEYWORD_VANISH = auto()
    KEYWORD_RECKLESS = auto()
    KEYWORD_EVASIVE = auto()
    KEYWORD_RUSH = auto()
    KEYWORD_BODYGUARD = auto()
    KEYWORD_SUPPORT = auto()
    KEYWORD_CHALLENGER = auto() # e.g., Challenger +X
    KEYWORD_RESIST = auto() # e.g., Resist +X
    KEYWORD_WARD = auto()
    KEYWORD_SHIFT = auto()
    KEYWORD_SINGER = auto() # e.g., Singer X

    # --- Event-Based Triggers ---
    ON_PLAY = auto()            # When you play this card
    ON_BANISH = auto()          # When this card is banished (in challenge, or by effect)
    ON_QUEST = auto()           # When this character quests
    ON_CHALLENGE = auto()       # When this character challenges
    ON_BEING_CHALLENGED = auto()# When this character is challenged
    ON_EXERT = auto()           # When this character exerts (for any reason)
    ON_READY = auto()           # When this character becomes ready
    ON_DISCARD = auto()         # When this card is discarded
    ON_OPPONENT_PLAYS_CARD = auto() # e.g., "Whenever an opponent plays an action..."
    ON_CHARACTER_ENTERS_PLAY = auto() # e.g., "Whenever one of your other characters..."
    ON_CHARACTER_LEAVES_PLAY = auto() # e.g., "Whenever one of your characters is banished..."

    # --- Turn Phased Triggers ---
    START_OF_TURN = auto()
    END_OF_TURN = auto()
    ON_YOUR_TURN = auto()       # Generic passive effect active only on your turn
    ON_OPPONENTS_TURN = auto()  # Generic passive effect active only on opponent's turn

    # --- Activated Abilities ---
    ACTIVATED = auto()          # Requires explicit player activation (usually cost involved)

    # --- Continuous / Passive Effects ---
    CONTINUOUS = auto()         # Always active while the card is in play (e.g., static stat buffs)

    # --- Location Specific ---
    ON_MOVE_TO_LOCATION = auto() # When a character moves here
    WHILE_AT_LOCATION = auto()   # Effect active while conditions met at location

    OTHER = auto()              # Catch-all for complex/unique triggers

class EffectType(Enum):
    # --- Player State Modification ---
    BANISH_CARD = auto()
    BANISH_SELF = auto()
    DRAW_CARD = auto()
    GAIN_LORE = auto()
    LOSE_LORE = auto()          # For opponent
    DISCARD_CARD_RANDOM = auto()
    DISCARD_CARD_CHOSEN = auto()
    ADD_INK_FROM_HAND = auto()

    # --- Character/Item State Modification ---
    DEAL_DAMAGE = auto()
    HEAL_DAMAGE = auto()        # Remove damage tokens
    MODIFY_STATS = auto()       # Change Strength/Willpower/Cost/Lore value
    GRANT_KEYWORD = auto()      # Give temporary or permanent keyword (Evasive, Rush etc)
    REMOVE_KEYWORD = auto()
    EXERT_CARD = auto()
    READY_CARD = auto()
    CANNOT_QUEST = auto()       # Apply restriction
    CANNOT_CHALLENGE = auto()   # Apply restriction
    CANNOT_BE_CHALLENGED = auto() # Apply protection

    # --- Card Manipulation ---
    RETURN_TO_HAND = auto()
    PUT_IN_INKWELL = auto()     # Own or opponent's card
    PUT_INTO_PLAY = auto()      # From hand or discard pile
    LOOK_AT_TOP_CARDS = auto()
    REVEAL_CARD = auto()
    SHUFFLE_INTO_DECK = auto()

    # --- Targeting/Selection ---
    CHOOSE_CARD = auto()        # Used when an effect requires a player choice before proceeding

    # --- Game State ---
    TAKE_EXTRA_TURN = auto()

    # --- Meta Effects ---
    MODIFY_COST_TO_PLAY = auto() # Modify cost of cards in hand/deck
    CONDITIONAL = auto()        # Effect only happens if a condition is met
    OTHER = auto()              # Catch-all

class TargetType(Enum):
    # --- Targets based on player ---
    SELF_PLAYER = auto()
    OPPONENT_PLAYER = auto()

    # --- Targets based on cards/characters ---
    SELF_CARD = auto()          # The card generating the effect
    TARGET_CHARACTER_CHOSEN = auto() # Player chooses one character
    TARGET_ITEM_CHOSEN = auto()
    TARGET_LOCATION_CHOSEN = auto()
    TARGET_CARD_IN_PLAY_CHOSEN = auto() # Any type
    TARGET_CARD_IN_HAND_CHOSEN = auto()
    TARGET_CARD_IN_DISCARD_CHOSEN = auto()
    ALL_OWN_CHARACTERS = auto()
    ALL_OWN_ITEMS = auto()
    ALL_OPPONENT_CHARACTERS = auto()
    ALL_OPPONENT_ITEMS = auto()
    ALL_CHARACTERS = auto()     # All characters in play (own and opponent's)
    ALL_ITEMS = auto()

    # --- Special Targets ---
    DAMAGED_CHARACTER = auto()  # Often used with specific effects like healing
    CHARACTER_WITH_KEYWORD = auto() # Filter target selection
    EXERTED_CHARACTER = auto()
    READY_CHARACTER = auto()
    CARD_TYPE = auto()          # e.g., Target an Action card

    # --- Meta ---
    EFFECT_GENERATOR = auto() # Targets the source of the effect (e.g., for costs)
    NONE = auto()               # Effect doesn't target anything specific (e.g. Draw Card)
    OTHER = auto()
