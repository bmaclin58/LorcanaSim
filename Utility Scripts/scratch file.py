text = "Shift: Discard 2 cards (You may discard 2 cards to play this on top of one of your characters named Flotsam or Jetsam.)\n(This character counts as being named both Flotsam and Jetsam.)"
import re

# Keyword pattern with ^ to match at the beginning of lines
keyword_pattern = (
	r"^(?:Evasive|Bodyguard|Rush|Ward|Vanish|Support|Reckless|Shift: |"  # single word keywords
	r"Challenger \+\d+|Resist \+\d+|Challenger\+\d+|"  # + Keywords
	r"Singer \d+|Sing Together \d+|"  # singing
	r"Puppy Shift \d+:?|Shift \d+:?|Universal Shift \d+:? )"
)

# Compile the pattern
pattern = re.compile(keyword_pattern)

# Split the text
text_parts = text.split('\n')

# Filter out lines that START WITH any of the keywords (notice the NOT operator)
filtered_parts = [line for line in text_parts if not pattern.match(line)]
print("Filtered parts:", filtered_parts)
