# Search configuration

## Keywords
KEYWORDS = [
    "Prabowo",
    # "Gibran"
]

# Date range for search
SINCE = "2025-06-01"
UNTIL = "2025-06-18"

# Language filter (empty for all languages)
LANGUAGE = "id"  # Indonesian

# Scrolling behavior
MAX_SCROLLS = 5  # Maximum scrolls per keyword
SCROLL_DELAY = 3  # Seconds between scrolls
NO_NEW_TWEETS_LIMIT = 3  # Stop after this many scrolls with no new tweets

# Browser options [DONT CHANGE IF YOU DONT UNDERTAND, SAL]
HEADLESS = False  # Set to True to run browser in headless mode
MAXIMIZED = True  # Start browser maximized

# Output settings [YOU CAN CHANGE THIS IF YOU WANT]
OUTPUT_FILENAME = "twitter_data"  # Base filename (timestamp will be added)
OUTPUT_FORMAT = "csv"  # Options: "csv", "json", "excel"