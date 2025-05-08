from enum import Enum, auto


# ==============================================================================
# Trigger Condition Enum
# ==============================================================================
class TriggerCondition(Enum):
    """Defines *when* an ability might trigger or be active."""

    # --- Meta-Trigger Types (Used for dynamic pattern matching) ---
    DYNAMIC_PREVENTION = auto() # For dynamic preventions
    DYNAMIC_TRIGGER = auto()  # For dynamic "When/Whenever" triggers that map to specific conditions
    DYNAMIC_TURN_TRIGGER = auto()  # For turn-based triggers (start/end)
    DYNAMIC_CONDITION = auto()  # For "During/While" conditions
    DYNAMIC_KEYWORD = auto()  # For single or multiple keywords
    DYNAMIC_BONUS = auto()  # For character stat bonuses
    DYNAMIC_CHARACTER_STATE = auto()  # For character state effects

    # --- Static / Continuous Conditions ---
    CONTINUOUS = auto()  # Effect is always active while the card is in the correct state/zone
    STATIC_COST_MODIFIER = auto()# Modifies the cost to play the card itself (checked during play action)
    WHILE_AT_LOCATION = auto()# Effect is active while the character is at any location
    ON_YOUR_TURN = auto()  # Effect is active only during your turn (passive)

    # --- Event-Based Triggers ---
    ON_PLAY = auto()  # When you play this card/character/item/location
    ON_BANISH = auto()  # When this card is banished (from challenge or effect)
    ON_QUEST = auto()  # When this character quests
    ON_CHALLENGE = auto()  # When this character initiates a challenge
    ON_BEING_CHALLENGED = auto()  # When this character is challenged by an opponent
    ON_EXERT = auto()# When this character exerts (for any reason: quest, challenge, sing, ability cost)
    ON_READY = auto()  # When this character becomes ready (e.g., at start of turn)
    ON_DISCARD = auto()  # When this card is discarded from hand
    ON_OPPONENT_PLAYS_CARD = auto()# When an opponent plays a card (can be filtered by type)
    ON_OPPONENT_PLAYS_SONG = auto()  # When an opponent plays a song
    ON_CHARACTER_ENTERS_PLAY = auto()# When any character enters play (own or opponent's, can be filtered)
    ON_CHARACTER_LEAVES_PLAY = auto()# When any character leaves play (own or opponent's, banished or returned)
    ON_MOVE_TO_LOCATION = auto()# When a character moves to this location (for location abilities)
    ON_CHARACTER_MOVES_FROM_LOCATION = auto()# When a character moves away from this location
    ON_SING = auto()  # When this character sings a song
    START_OF_TURN = auto()  # At the beginning of your turn
    END_OF_TURN = auto()  # At the end of your turn
    PREVENT_PLAY = auto() # Can't play such as can't play actions

    # --- Additional Features ----
    KEYWORD_ONLY = auto()  # Single keyword ability (like "Evasive" or "Support")
    MULTIPLE_KEYWORDS = auto()  # Multiple keywords in sequence without other effects
    STATIC_BONUS = auto()  # "Your other characters get +X stat"
    SELF_BONUS = auto()  # "This character gets +X stat"
    PROTECTION_CHALLENGE = auto()  # "This character can't be challenged"
    CONDITIONAL_EFFECT = auto()  # "If/While you have X, Y happens"
    ENTERS_PLAY_EFFECT = auto()  # "This character enters play..."
    GENERAL_WHENEVER = auto()  # Other "Whenever X happens" triggers not covered
    COST_REDUCTION = auto()  # "For each X, you pay Y less"
    SELF_CONDITIONAL = auto()  # "While this character has/is X, Y happens"
    STAT_VALUE = auto()  # Just a numerical stat value like "3 strength this turn"
    CHARACTER_TYPE_EFFECT = auto()  # "Your X characters gain/get Y"
    DURING_TURN = auto()  # "During your/an opponent's turn"
    ONCE_PER_TURN = auto()  # "Once during your turn"
    WIN_CONDITION_MODIFIER = auto()  # Effects that change win conditions
    NAMED_CHARACTER_EFFECT = auto()  # "Your characters named X gain/get Y"
    SIMPLE_ACTION_EFFECT = auto()  # Simple action card effects
    SING_TOGETHER = auto()  # For the Sing Together cost reduction keyword

    # --- Activated Ability Trigger ---
    ACTIVATED = auto()# Requires manual activation by the player (often with {e} or ink cost)

    # --- Keyword-Related Triggers/Identifiers ---
    # These might trigger specific game rule interactions or checks
    KEYWORD_BODYGUARD = auto()  # Must be challenged if possible
    KEYWORD_CHALLENGER = auto()  # Gets +X Strength when challenging
    KEYWORD_EVASIVE = auto()  # Can only be challenged by characters with Evasive
    KEYWORD_RECKLESS = auto()  # Must challenge if able
    KEYWORD_RESIST = auto()  # Takes X less damage from challenges/effects
    KEYWORD_RUSH = auto()  # Can challenge the turn it's played
    KEYWORD_SHIFT = auto()  # Can be played for alternate cost on another character
    KEYWORD_SINGER = auto()  # Can exert to sing songs of cost X or less
    KEYWORD_SUPPORT = auto()  # When questing, adds Strength to another chosen character
    KEYWORD_VANISH = auto()# Can be banished to opponent's inkwell (if targeted by opponent's action effect)
    KEYWORD_WARD = auto()  # Cannot be chosen by opponent's effects (except challenges)

    # --- Catch-all ---
    OTHER = auto()  # For triggers not fitting standard categories (use sparingly)


# ==============================================================================
# Effect Type Enum
# ==============================================================================
class EffectType(Enum):
    """Defines *what* an ability does."""

    # --- Player State Changes ---
    DRAW_CARD = auto()
    GAIN_LORE = auto()
    LOSE_LORE = auto()
    DISCARD_CARD_RANDOM = auto()
    DISCARD_CARD_CHOSEN = auto()  # Player chooses which card(s) to discard
    LOOK_AT_HAND = auto()  # Look at opponent's hand
    SHUFFLE_DECK = auto()

    # --- Card Manipulation / Movement ---
    MOVE_TO_ZONE = auto()# Move card(s) between zones (hand, deck, discard, inkwell, play)
    REVEAL_CARD = auto()  # Reveal card(s) from hand or deck
    LOOK_AT_TOP_CARDS = auto()  # Look at top N cards of a deck
    PLAY_CARD = auto()# Play a card (often from non-hand zone, potentially ignoring cost)
    BANISH_SELF = auto()  # Banish this card (for Vanish keyword)
    PUT_ON_BOTTOM = auto()  # Put cards on the bottom of a deck
    BANISH_TARGET = auto() # Banish target(s)

    # --- In-Play Card State Changes ---
    DEAL_DAMAGE = auto()
    HEAL_DAMAGE = auto()  # Remove damage counters
    MODIFY_STATS = auto()  # Change Strength, Willpower, Lore value
    MODIFY_LOCATION_STATS = auto()  # Change Location Willpower or Move Cost
    EXERT_CARD = auto()
    READY_CARD = auto()
    GRANT_KEYWORD = auto()  # Give a card a keyword (e.g., Evasive, Rush)
    REMOVE_KEYWORD = auto()  # Remove a keyword
    SET_ATTRIBUTE = auto()  # Set a specific attribute (e.g., cannot be challenged)
    PREVENT_ACTION = auto()  # Prevent a character from performing an action
    PREVENT_PLAY = auto()  # Prevent playing certain card types

    # --- Cost Modification ---
    MODIFY_COST_TO_PLAY = auto()  # Modify the ink cost to play a card

    # --- Targeting / Choice ---
    CHOOSE_TARGET = auto()  # Player controlling effect chooses target(s)
    OPPONENT_CHOOSES = auto()  # Opponent chooses target(s) for an effect

    # --- Meta / Control Flow ---
    CHOOSE_EFFECT = auto()  # Player chooses one effect from a list to resolve
    CONDITIONAL = auto()  # Effect only happens if a condition is met
    REPEAT_EFFECT = auto()  # Repeat an effect N times or for each X

    # --- Catch-all ---
    OTHER = auto()  # For effects not fitting standard categories (use sparingly)


# ==============================================================================
# Target Type Enum
# ==============================================================================
class TargetType(Enum):
    """Defines *who* or *what* an effect applies to, often used with parameters for filtering."""

    # --- Player Targets ---
    SELF_PLAYER = auto()  # The player controlling the effect
    OPPONENT_PLAYER = auto()  # The opponent(s) of the player controlling the effect

    # --- Card Targets (Usually requires player choice unless specified) ---
    SELF_CARD = auto()  # The card source of the effect

    # Generic Targets (Player chooses ONE unless specified otherwise)
    TARGET_CHARACTER_CHOSEN = auto()  # Player chooses one character in play
    TARGET_ITEM_CHOSEN = auto()  # Player chooses one item in play
    TARGET_LOCATION_CHOSEN = auto()  # Player chooses one location in play
    TARGET_CARD_IN_PLAY_CHOSEN = auto()  # Player chooses any card type in play
    TARGET_CARD_IN_HAND_CHOSEN = auto()  # Player chooses card(s) from a specific hand
    TARGET_CARD_IN_DISCARD_CHOSEN = auto()# Player chooses card(s) from a specific discard pile
    TARGET_CARD_IN_INKWELL_CHOSEN = auto()# Player chooses card(s) from a specific inkwell

    # Opponent Choice Targets
    OPPONENT_CHOOSES_CHARACTER = auto()  # Opponent chooses one of their characters
    OPPONENT_CHOOSES_ITEM = auto()  # Opponent chooses one of their items
    OPPONENT_CHOOSES_LOCATION = auto()  # Opponent chooses one of their locations
    OPPONENT_CHOOSES_CARD_IN_PLAY = auto()# Opponent chooses one of their cards in play
    OPPONENT_CHOOSES_CARD_IN_HAND = auto()  # Opponent chooses card(s) from their hand
    OPPONENT_CHOOSES_CARD_IN_DISCARD = auto()# Opponent chooses card(s) from their discard

    # Group Targets (Affects all matching cards without choice)
    ALL_OWN_CHARACTERS = auto()
    ALL_OWN_ITEMS = auto()
    ALL_OWN_LOCATIONS = auto()
    ALL_OWN_CARDS_IN_PLAY = auto()
    ALL_OPPONENT_CHARACTERS = auto()
    ALL_OPPONENT_ITEMS = auto()
    ALL_OPPONENT_LOCATIONS = auto()
    ALL_OPPONENT_CARDS_IN_PLAY = auto()
    ALL_CHARACTERS = auto()  # All characters in play (own and opponent's)
    ALL_ITEMS = auto()
    ALL_LOCATIONS = auto()
    ALL_CARDS_IN_PLAY = auto()

    # Location-Relative Targets
    CHARACTER_AT_THIS_LOCATION = auto()# A character at the location generating the effect
    CHARACTER_AT_OTHER_LOCATION = auto()  # A character at a different location
    ALL_CHARACTERS_AT_LOCATION = auto()  # All characters at a specific location

    # Zone/Position Targets
    TOP_CARD_OF_DECK = auto()
    BOTTOM_CARD_OF_DECK = auto()

    # Contextual Targets (depend on the current game action)
    CARD_BEING_PLAYED = auto()  # The card currently being resolved/played
    LOOKED_AT_CARDS = auto()  # Cards revealed by a LOOK_AT_TOP_CARDS effect
    CHALLENGING_CHARACTER = auto()  # The character initiating the current challenge
    DEFENDING_CHARACTER = auto()  # The character being challenged

    # --- No specific target (effect applies globally or to the game state) ---
    NONE = auto()
    OTHER = auto()  # Catch-all
