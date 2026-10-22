from check_grammar import get_grammar_errors

def evaluate_speech(text: str, filler_count: int) -> dict:
    # check_grammar.py හරහා errors ලබා ගැනීම
    matches = get_grammar_errors(text)
    
    # ලකුණු අඩු කිරීමේ නීති
    penalties = {
        "GRAMMAR": 1.5,        # Tense, verb agreement
        "TYPOS": 0.5,          # Spelling
        "CASING": 0.25,        # Capitalization
        "PUNCTUATION": 0.25,   # Comma/period
        "OTHER": 0.5
    }
    
    total_deduction = 0.0
    categorized_errors = {
        "GRAMMAR": [],
        "TYPOS": [],
        "CASING": [],
        "PUNCTUATION": [],
        "OTHER": []
    }

    for match in matches:
        category = match.category if match.category in penalties else "OTHER"
        categorized_errors[category].append({
            "message": match.message,
            "rule": getattr(match, 'rule_id', getattr(match, 'ruleId', 'UNKNOWN')),
            "context": match.context
        })
        total_deduction += penalties[category]

    # Fillers සඳහා දඩ ලකුණු (එකකට 0.25 බැගින්)
    filler_penalty = filler_count * 0.25
    total_deduction += filler_penalty

    # ලකුණු 10න් අවසන් ලකුණ
    final_score = max(0.0, 10.0 - total_deduction)

    return {
        "score": round(final_score, 2),
        "total_grammar_errors": len(matches),
        "filler_count": filler_count,
        "filler_deduction": round(filler_penalty, 2),
        "details": categorized_errors
    }