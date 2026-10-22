import re

FILLERS = [r"\bum\b", r"\buh\b", r"\bah\b", r"\ber\b", r"\bhmm\b", r"\blike\b"]

def count_fillers(text: str) -> int:
    total_fillers = 0
    for filler in FILLERS:
        matches = re.findall(filler, text, flags=re.IGNORECASE)
        total_fillers += len(matches)
    return total_fillers