"""
transliteration.py — Clean Tanglish / Hinglish generation
Uses aksharamukha for base romanization, then applies smart post-processing
to produce human-readable phonetic output (not raw academic transliteration).
"""

from aksharamukha import transliterate as aksha


def to_roman(text: str, language: str) -> str:
    """
    Convert Tamil or Hindi script to clean readable romanization.
    language: "Tamil" → Tanglish  |  "Hindi" → Hinglish
    """
    if not text or not text.strip():
        return ""
    try:
        if language == "Tamil":
            raw = aksha.process("Tamil", "ISO", text)
            return _clean_tanglish(raw)
        elif language == "Hindi":
            raw = aksha.process("Devanagari", "ISO", text)
            return _clean_hinglish(raw)
        return ""
    except Exception as e:
        return f"(error: {e})"


# ── Tamil → Tanglish ──────────────────────────────────────────────────────────

def _clean_tanglish(text: str) -> str:
    """
    Convert ISO 15919 Tamil romanization to natural Tanglish.
    Goal: output should read like how a Tamil speaker would type in English.
    """
    import unicodedata

    # Step 1: Replace diacritics with readable equivalents
    replacements = {
        # Long vowels → doubled for readability
        "ā": "aa", "Ā": "aa",
        "ī": "ee", "Ī": "ee",   # ii → ee (more natural)
        "ū": "oo", "Ū": "oo",   # uu → oo
        "ē": "e",  "Ē": "e",
        "ō": "o",  "Ō": "o",
        # Retroflex consonants
        "ṭ": "t",  "Ṭ": "t",
        "ḍ": "d",  "Ḍ": "d",
        "ṇ": "n",  "Ṇ": "n",
        "ṅ": "ng", "Ṅ": "ng",
        "ñ": "ny",
        "ś": "sh", "Ś": "sh",
        "ṣ": "sh", "Ṣ": "sh",
        "ḥ": "h",  "Ḥ": "h",
        "ṁ": "m",  "Ṁ": "m",
        "ṃ": "m",  "Ṃ": "m",
        "ḷ": "l",  "Ḷ": "l",
        "ḻ": "zh", "Ḻ": "zh",   # unique Tamil sound
        "ṟ": "r",  "Ṟ": "r",
        "ṉ": "n",  "Ṉ": "n",
        "ḵ": "k",
        # Nasalization
        "m̐": "n",
        "ṃ": "m",
    }
    for src, dst in replacements.items():
        text = text.replace(src, dst)

    # Step 2: Remove remaining combining diacritics
    text = "".join(
        c for c in text
        if unicodedata.category(c) != "Mn"
    )

    # Step 3: Common word-level fixes for natural Tanglish
    word_fixes = {
        "irukkiingka":  "irukkinga",
        "irukkiingkal": "irukkinga",
        "irukkeenga":   "irukkinga",
        "eppati":       "eppadi",
        "eppadee":      "eppadi",
        "neengal":      "neenga",
        "neengkal":     "neenga",
        "niingkal":     "neenga",
        "niingka":      "neenga",
        "vanakkam":     "vanakkam",
        "nanri":        "nandri",
        "mikka":        "romba",
        "sariyaa":      "sariya",
        "pannittiru":   "pannittu iru",
        "paarkkireenga": "paakinga",
        "theriyum":     "theriyum",
        "sollungal":    "sollunga",
        "vaanga":       "vaanga",
        "poonga":       "pooinga",
    }
    for wrong, right in word_fixes.items():
        text = text.replace(wrong, right)

    # Step 4: Normalize double-vowel artifacts
    text = text.replace("aai", "ai")
    text = text.replace("ooi", "oi")

    return text.strip()


# ── Hindi → Hinglish ──────────────────────────────────────────────────────────

def _clean_hinglish(text: str) -> str:
    """
    Convert ISO 15919 Hindi romanization to natural Hinglish.
    Goal: output should read like how a Hindi speaker would type in English.
    """
    import unicodedata

    replacements = {
        "ā": "aa", "Ā": "aa",
        "ī": "ee", "Ī": "ee",
        "ū": "oo", "Ū": "oo",
        "ē": "e",  "Ē": "e",
        "ō": "o",  "Ō": "o",
        "ṭ": "t",  "Ṭ": "t",
        "ḍ": "d",  "Ḍ": "d",
        "ṇ": "n",  "Ṇ": "n",
        "ṅ": "ng",
        "ñ": "ny",
        "ś": "sh", "Ś": "sh",
        "ṣ": "sh", "Ṣ": "sh",
        "ḥ": "h",  "Ḥ": "h",
        "ṁ": "n",  "Ṁ": "n",
        "ṃ": "n",  "Ṃ": "n",
        "ḷ": "l",
        "ṟ": "r",
        "m̐": "n",
        "ṛ": "ri",
    }
    for src, dst in replacements.items():
        text = text.replace(src, dst)

    # Remove remaining combining marks
    text = "".join(
        c for c in text
        if unicodedata.category(c) != "Mn"
    )

    # Common Hinglish word fixes
    word_fixes = {
        "aapa":      "aap",
        "haim":      "hain",
        "hoom":      "hoon",
        "maim":      "main",
        "thieka":    "theek",
        "thiika":    "theek",
        "kaise":     "kaisa",
        "namaste":   "namaste",
        "suprabhaata": "suprabhat",
        "dhanyavaada": "dhanyavaad",
        "acchaa":    "achha",
        "kyaa":      "kya",
        "naheen":    "nahi",
        "bahut":     "bahut",
        "shukriyaa": "shukriya",
    }
    for wrong, right in word_fixes.items():
        text = text.replace(wrong, right)

    return text.strip()
