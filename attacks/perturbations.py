# attacks/perturbations.py
import random

SYN_DICT = {
    "ignore": ["disregard", "omit", "skip"],
    "instructions": ["rules", "directives", "orders"],
    "provide": ["give", "reveal", "return"],
    "API_KEY": ["SECRET_KEY", "TOKEN"],
}

def paraphrase_simple(text):
    # very small synonym swap heuristic
    for k, vals in SYN_DICT.items():
        if k in text:
            text = text.replace(k, random.choice(vals))
    return text

def whitespace_obfuscate(text, rate=0.05):
    # insert occasional double spaces
    out_chars = []
    for ch in text:
        out_chars.append(ch)
        if ch.isalpha() and random.random() < rate:
            out_chars.append(" ")
    return "".join(out_chars)

def char_inject(text, n=3):
    # inject random punctuation in n positions
    import string
    chars = list(text)
    for _ in range(n):
        i = random.randrange(len(chars))
        chars[i] = chars[i] + random.choice(["#", "@", "%"])
    return "".join(chars)
