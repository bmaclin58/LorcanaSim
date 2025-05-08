# Ability Parser Implementation

## Overview
This project implements an ability parser for Lorcana cards that processes each card's Body_Text and Abilities fields to create structured Ability objects. These objects represent the card's abilities and effects in a way that can be used by the game logic.

## Components

### 1. Ability Data Structures
- `Ability`: Represents a single card ability with a trigger condition, effects, and optional cost
- `Effect`: Represents a single game action resulting from an ability
- `AbilityCost`: Represents the cost required to activate an ability

### 2. Ability Parser
- `parse_abilities()`: Main function that parses Body_Text and Abilities fields into Ability objects
- `parse_effects()`: Parses effect text into Effect objects
- `parse_Keyword_ability()`: Parses a single keyword ability

### 3. Card Integration
- Added `parsed_abilities` field to Card class
- Added `parse_abilities()` method to Card class for lazy parsing
- Added `get_abilities()` method to Card class to retrieve parsed abilities

## Implementation Details

### Pattern Matching
The parser uses regular expressions to match different ability patterns:
- Keyword abilities (Rush, Bodyguard, etc.)
- Triggered abilities (When you play this character, At the start of your turn, etc.)
- Activated abilities with costs (1{i}, {e}, etc.)
- Conditional effects (If X, then Y)

### Effect Processing
Effects are processed based on their type:
- Draw cards
- Gain/lose lore
- Deal/heal damage
- Modify stats
- Grant keywords
- Prevent actions
- etc.

### Integration with Card Class
The Card class now supports lazy parsing of abilities:
- Abilities are parsed only when needed
- Parsing is done once and cached
- Circular imports are avoided by importing the parser only when needed

## Testing
The implementation has been tested with:
- Sample cards with different ability types
- Cards with complex abilities
- Cards with keyword abilities

## Future Improvements

1. **More Specific Patterns**: Add more specific patterns to reduce the number of abilities parsed as "OTHER"
2. **Better Conditional Handling**: Improve handling of complex conditional effects
3. **Parameter Extraction**: Extract more parameters from ability text (e.g., duration, targets)
4. **Error Handling**: Add better error handling for malformed ability text
5. **Performance Optimization**: Optimize pattern matching for better performance with large card sets
6. **Documentation**: Add more detailed documentation for each pattern and effect type
7. **Unit Tests**: Add unit tests for each pattern and edge case

## Conclusion
The ability parser successfully processes card abilities from the Body_Text and Abilities fields, creating structured Ability objects that can be used by the game logic. It handles a wide range of ability types and integrates well with the existing Card class.
