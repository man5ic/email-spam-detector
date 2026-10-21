"""All spam patterns, categories, weights and example emails live here."""

# category -> {pattern: weight}   (weight 1 = low, 2 = medium, 3 = high)
PATTERN_CATEGORIES = {
    "Prize / Reward": {
        "PRIZE": 3, "WINNER": 3, "YOU HAVE WON": 3, "WIN": 2,
        "CONGRATULATIONS": 2, "REWARD": 2, "GIFT": 1,
    },
    "Urgency": {
        "URGENT": 2, "ACT NOW": 2, "LIMITED TIME": 2, "LAST CHANCE": 2,
        "EXPIRES TODAY": 2, "HURRY": 1,
    },
    "Financial": {
        "CASH": 2, "LOTTERY": 3, "MONEY BACK": 2, "EARN MONEY": 2,
        "CREDIT CARD": 1, "LOAN": 1,
    },
    "Call To Action": {
        "CLICK HERE": 2, "CLAIM NOW": 2, "CLAIM YOUR": 2, "BUY NOW": 2,
        "VERIFY YOUR ACCOUNT": 3, "SIGN UP NOW": 1,
    },
    "Promotional": {
        "FREE": 2, "OFFER": 1, "DISCOUNT": 1, "BONUS": 1,
        "NO COST": 2, "100% GUARANTEED": 3,
    },
}

# pattern -> {"category": ..., "weight": ...}
SPAM_PATTERNS = {
    pattern: {"category": category, "weight": weight}
    for category, group in PATTERN_CATEGORIES.items()
    for pattern, weight in group.items()
}

EXAMPLE_EMAILS = {
    "Spam example 1": (
        "Congratulations! You have won a FREE prize.\n"
        "Click here to claim your CASH reward!"
    ),
    "Spam example 2": (
        "URGENT! ACT NOW to claim your limited time offer.\n"
        "You are a WINNER!"
    ),
    "Normal email": (
        "Hi team,\n\n"
        "The meeting has been scheduled for tomorrow at 10 AM.\n"
        "Please bring the project documentation.\n\n"
        "Regards"
    ),
    "False-positive test": (
        "Hi all, lunch is free for everyone after tomorrow's team meeting. "
        "Please open the window before you leave."
    ),
}
