"""Turn the list of matches into a risk score and a Spam / Not Spam verdict."""
from collections import Counter

from data.spam_patterns import SPAM_PATTERNS

SPAM_THRESHOLD = 4  # total weight of DISTINCT patterns needed to say "spam"
RISK_LABELS = {1: "Low", 2: "Medium", 3: "High"}


def evaluate(matches):
    counts = Counter(m.pattern for m in matches)
    total_weight = sum(SPAM_PATTERNS[p]["weight"] for p in counts)
    rows = [{
        "Pattern": pattern,
        "Category": SPAM_PATTERNS[pattern]["category"],
        "Occurrences": count,
        "Risk": RISK_LABELS[SPAM_PATTERNS[pattern]["weight"]],
    } for pattern, count in sorted(counts.items(),
                                   key=lambda kv: -SPAM_PATTERNS[kv[0]]["weight"])]
    return {
        "rows": rows,
        "total_weight": total_weight,
        "risk_score": min(5, (total_weight + 1) // 2),  # scale 0..5
        "is_spam": total_weight >= SPAM_THRESHOLD,
        "total_matches": len(matches),
    }
