"""
tamil_postprocess.py — Natural Tamil post-processing
Converts formal/robotic model output into natural spoken Tamil.
Supports Formal and Informal tone modes.

Formal mode applies grammar corrections based on EN→TA cheat sheet rules:
  Rule 1  — "I feel…" → எனக்கு … தருகிறது  (not என்னை … உணர்கிறது)
  Rule 2  — Remove redundant time words (ஒவ்வொரு காலையிலும் … காலையில்)
  Rule 3  — Colloquial verbs → standard written Tamil
  Rule 5  — Normalise "after that" connectors
  Rule 6  — Food verb normalisation (உண்டு / சாப்பிட்டு)
  Rule 7  — Don't mix மிகவும் + ரொம்ப
  Rule 9  — Continuous tense: ensure கொண்டிருக்கிறேன் form
  Rule 10 — "I feel good" → எனக்கு நல்லா இருக்கிறது
"""

import re

# ── Common phrase overrides (exact match, checked first) ─────────────────────
# These are phrases where the model consistently gives unnatural output.
PHRASE_OVERRIDES = {
    # Formal versions
    "how are you?":         "நீங்கள் எப்படி இருக்கிறீர்கள்?",
    "how are you doing?":   "எப்படி இருக்கீங்க?",
    "are you ok?":          "நீங்கள் சரியா இருக்கீங்களா?",
    "how is your health?":  "உங்க உடம்பு எப்படி இருக்கு?",
    "what are you doing?":  "என்ன பண்ணிட்டு இருக்கீங்க?",
    "good morning":         "காலை வணக்கம்",
    "good night":           "இரவு வணக்கம்",
    "thank you":            "நன்றி",
    "thank you very much":  "மிக்க நன்றி",
    "what is your name?":   "உங்கள் பெயர் என்ன?",
    "where are you going?": "எங்கே போகிறீர்கள்?",
    "i am fine":            "நான் நலமாக இருக்கிறேன்",
    "i love you":           "நான் உன்னை காதலிக்கிறேன்",
    "how old are you?":     "உங்களுக்கு வயது என்ன?",
}

# ── Formal word replacements (applied to model output) ───────────────────────
FORMAL_TO_NATURAL = {
    "ஆரோக்கியம்":       "உடம்பு",
    "இருக்கிறது":        "இருக்கு",
    "இருக்கிறீர்கள்":   "இருக்கீங்க",
    "இருக்கிறார்கள்":   "இருக்காங்க",
    "இருக்கிறேன்":      "இருக்கேன்",
    "செய்கிறீர்கள்":    "பண்றீங்க",
    "செய்கிறேன்":       "பண்றேன்",
    "போகிறீர்கள்":      "போறீங்க",
    "போகிறேன்":         "போறேன்",
    "வருகிறீர்கள்":     "வரீங்க",
    "வருகிறேன்":        "வரேன்",
    "சாப்பிடுகிறீர்கள்": "சாப்பிடுறீங்க",
    "பார்க்கிறீர்கள்":  "பாக்கீங்க",
    "தெரியும்":         "தெரியும்",
    "என்னவென்று":       "என்னன்னு",
    "என்னவென்று":       "என்னன்னு",
}

# ── Formal grammar corrections (colloquial → standard written Tamil) ─────────
# Applied in formal mode to fix common model errors.
COLLOQUIAL_TO_FORMAL = {
    # Verb endings
    "பண்றேன்":       "செய்கிறேன்",
    "பண்றீங்க":      "செய்கிறீர்கள்",
    "பண்றாங்க":      "செய்கிறார்கள்",
    "பண்றான்":       "செய்கிறான்",
    "பண்றாள்":       "செய்கிறாள்",
    "பண்றது":        "செய்கிறது",
    "பண்ணுகிறேன்":   "செய்கிறேன்",
    "பண்ணுகிறீர்கள்": "செய்கிறீர்கள்",
    "சாப்பிடுறேன்":  "சாப்பிடுகிறேன்",
    "சாப்பிடுறீங்க": "சாப்பிடுகிறீர்கள்",
    "போறேன்":        "போகிறேன்",
    "போறீங்க":       "போகிறீர்கள்",
    "வரேன்":         "வருகிறேன்",
    "வரீங்க":        "வருகிறீர்கள்",
    "இருக்கேன்":     "இருக்கிறேன்",
    "இருக்கீங்க":    "இருக்கிறீர்கள்",
    "பாக்கீங்க":     "பார்க்கிறீர்கள்",
    "பாக்கேன்":      "பார்க்கிறேன்",
    # Pronouns
    "நீங்க":         "நீங்கள்",
    "உங்க":          "உங்கள்",
    "என்னோட":        "என்னுடைய",
    "உங்களோட":       "உங்களுடைய",
    # Particles
    "ன்னு":          "என்று",
    "ன்னா":          "என்றால்",
}

# ── Redundant time-word patterns to clean up (Rule 2) ────────────────────────
# e.g. "ஒவ்வொரு காலையிலும், நான் காலையில்" → "ஒவ்வொரு காலையிலும் நான்"
REDUNDANT_TIME_PATTERNS = [
    (r'(ஒவ்வொரு காலையிலும்)[,\s]+(நான்\s+)?காலையில்\s+',   r'\1 நான் '),
    (r'(ஒவ்வொரு மாலையிலும்)[,\s]+(நான்\s+)?மாலையில்\s+',   r'\1 நான் '),
    (r'(ஒவ்வொரு இரவிலும்)[,\s]+(நான்\s+)?இரவில்\s+',        r'\1 நான் '),
    (r'(ஒவ்வொரு நாளும்)[,\s]+(நான்\s+)?நாளில்\s+',           r'\1 நான் '),
    (r'(ஒவ்வொரு வாரமும்)[,\s]+(நான்\s+)?வாரத்தில்\s+',       r'\1 நான் '),
    # "இன்று இன்றைய" — same-day redundancy
    (r'இன்று\s+இன்றைய\s+',                                    'இன்றைய '),
]

# ── Wrong causative / "feel" structure fix (Rules 1 & 10) ────────────────────
# Rule 1:  "என்னை X-ஆக உணர்கிறது"  → "எனக்கு X தருகிறது"
# Rule 10: "நான் நல்லா உணர்கிறேன்" → "எனக்கு நல்லா இருக்கிறது"
CAUSATIVE_FIXES = [
    # Specific common phrases first (most precise → least precise)
    (r'என்னை\s+ஓய்வெடுத்து\s+மகிழ்ச்சியாக\s+உணர்கிறது',
     'எனக்கு ஓய்வும் மகிழ்ச்சியும் தருகிறது'),
    (r'என்னை\s+புத்துணர்ச்சியாக\s+உணர்கிறது',
     'எனக்கு புத்துணர்ச்சி தருகிறது'),
    (r'என்னை\s+மகிழ்ச்சியாக\s+உணர்கிறது',
     'எனக்கு மகிழ்ச்சி தருகிறது'),
    (r'என்னை\s+சோர்வாக\s+உணர்கிறது',
     'எனக்கு சோர்வு தருகிறது'),
    (r'என்னை\s+அமைதியாக\s+உணர்கிறது',
     'எனக்கு அமைதி தருகிறது'),
    (r'என்னை\s+கோபமாக\s+உணர்கிறது',
     'எனக்கு கோபம் தருகிறது'),
    # Generic: "என்னை <X>-ஆக உணர்கிறது / உணர வைக்கிறது"
    (r'என்னை\s+([\w\s]+?)ஆக\s+உணர\s+வைக்கிறது',  r'எனக்கு \1தருகிறது'),
    (r'என்னை\s+([\w\s]+?)ஆக\s+உணர்கிறது',         r'எனக்கு \1தருகிறது'),
    # Rule 10: "நான் X உணர்கிறேன்" → "எனக்கு X இருக்கிறது"
    (r'நான்\s+நல்லாக\s+உணர்கிறேன்',   'எனக்கு நல்லா இருக்கிறது'),
    (r'நான்\s+நல்லா\s+உணர்கிறேன்',    'எனக்கு நல்லா இருக்கிறது'),
    (r'நான்\s+சோர்வாக\s+உணர்கிறேன்',  'எனக்கு சோர்வாக இருக்கிறது'),
    (r'நான்\s+மகிழ்ச்சியாக\s+உணர்கிறேன்', 'எனக்கு மகிழ்ச்சியாக இருக்கிறது'),
    (r'நான்\s+கோபமாக\s+உணர்கிறேன்',   'எனக்கு கோபமாக இருக்கிறது'),
]

# ── Rule 7: Mixed "very" — don't use மிகவும் + ரொம்ப together ───────────────
VERY_FIXES = [
    (r'மிகவும்\s+ரொம்ப\s+', 'மிகவும் '),
    (r'ரொம்ப\s+மிகவும்\s+', 'மிகவும் '),
]

# ── Rule 5: Normalise "after that" connectors ─────────────────────────────────
# Model sometimes outputs inconsistent spacing/punctuation around அதன் பிறகு
CONNECTOR_FIXES = [
    (r'அதன்பிறகு',          'அதன் பிறகு'),   # missing space
    (r'அதற்குப்\s*பிறகு',   'அதன் பிறகு'),   # alternate form
    (r'அதன்\s+பின்னர்',     'அதன் பிறகு'),   # பின்னர் → பிறகு (more natural)
]

# ── Rule 6: Food verb normalisation ──────────────────────────────────────────
# "உணவை சாப்பிட்டு" → "உணவு சாப்பிட்டு"  (drop accusative -ஐ after உணவு)
FOOD_FIXES = [
    (r'உணவை\s+சாப்பிட்டு',  'உணவு சாப்பிட்டு'),
    (r'உணவை\s+சாப்பிடுகிறேன்', 'உணவு சாப்பிடுகிறேன்'),
    (r'உணவை\s+சாப்பிட்டேன்',   'உணவு சாப்பிட்டேன்'),
]

# ── Rule 9: Continuous tense normalisation ────────────────────────────────────
# Ensure "-ing" forms use கொண்டிருக்கிறேன் consistently
CONTINUOUS_FIXES = [
    # "படிக்கிறேன்" when context implies ongoing → keep as-is (model usually correct)
    # Fix malformed continuous: "படித்துக்கொண்டிருக்கிறேன்" spacing issues
    (r'([\u0B80-\u0BFF]+)க்கொண்டிருக்கிறேன்',  r'\1கொண்டிருக்கிறேன்'),
    (r'([\u0B80-\u0BFF]+)க்கொண்டிருக்கிறார்கள்', r'\1கொண்டிருக்கிறார்கள்'),
]

# ── Informal tone: replace formal pronouns/verbs ─────────────────────────────
FORMAL_TO_INFORMAL = {
    "நீங்கள்":    "நீ",
    "உங்கள்":    "உன்",
    "உங்களுக்கு": "உனக்கு",
    "இருக்கீங்க": "இருக்க",
    "போறீங்க":   "போற",
    "வரீங்க":    "வர",
    "பண்றீங்க":  "பண்ற",
    "பாக்கீங்க":  "பாக்க",
}


def postprocess(text: str, original_input: str = "", tone: str = "formal") -> str:
    """
    Main post-processing function.

    Args:
        text:           Tamil text from the translation model
        original_input: Original English input (used for phrase override lookup)
        tone:           "formal" or "informal"

    Returns:
        Cleaned, natural-sounding Tamil string
    """
    if not text or not text.strip():
        return text

    # ── Step 1: Check phrase overrides (original input first, then text itself) ─
    for lookup in (original_input, text):
        if lookup:
            key = lookup.strip().lower()
            if key in PHRASE_OVERRIDES:
                result = PHRASE_OVERRIDES[key]
                if tone == "informal":
                    result = _apply_informal(result)
                return result

    result = text.strip()

    if tone == "formal":
        # ── Step 2a: Fix redundant time expressions (Rule 2) ─────────────────
        result = _fix_redundant_time(result)

        # ── Step 2b: Fix wrong causative / "feel" structures (Rules 1 & 10) ──
        result = _fix_causative(result)

        # ── Step 2c: Fix colloquial verbs → standard written Tamil (Rule 3) ──
        result = _fix_colloquial(result)

        # ── Step 2d: Normalise "after that" connectors (Rule 5) ──────────────
        for pattern, replacement in CONNECTOR_FIXES:
            result = re.sub(pattern, replacement, result)

        # ── Step 2e: Food verb normalisation (Rule 6) ────────────────────────
        for pattern, replacement in FOOD_FIXES:
            result = re.sub(pattern, replacement, result)

        # ── Step 2f: Fix mixed "very" (Rule 7) ───────────────────────────────
        for pattern, replacement in VERY_FIXES:
            result = re.sub(pattern, replacement, result)

        # ── Step 2g: Continuous tense normalisation (Rule 9) ─────────────────
        for pattern, replacement in CONTINUOUS_FIXES:
            result = re.sub(pattern, replacement, result)

    else:
        # ── Step 2 (informal): Apply natural spoken word replacements ─────────
        for formal, natural in FORMAL_TO_NATURAL.items():
            result = result.replace(formal, natural)

        # ── Step 3: Apply informal tone ───────────────────────────────────────
        result = _apply_informal(result)

    # ── Step 4: Fix question marks ────────────────────────────────────────────
    result = _fix_question(result, original_input)

    return result.strip()


def _fix_redundant_time(text: str) -> str:
    """Remove redundant time expressions like 'ஒவ்வொரு காலையிலும் … காலையில்'."""
    for pattern, replacement in REDUNDANT_TIME_PATTERNS:
        text = re.sub(pattern, replacement, text)
    return text


def _fix_causative(text: str) -> str:
    """
    Fix wrong causative structure.
    'என்னை X-ஆக உணர்கிறது' → 'எனக்கு X தருகிறது'
    """
    for pattern, replacement in CAUSATIVE_FIXES:
        text = re.sub(pattern, replacement, text)
    return text


def _fix_colloquial(text: str) -> str:
    """Replace colloquial spoken-Tamil words with standard written Tamil."""
    for colloquial, formal in COLLOQUIAL_TO_FORMAL.items():
        text = text.replace(colloquial, formal)
    return text


def _apply_informal(text: str) -> str:
    """Replace formal pronouns/verb endings with informal equivalents."""
    for formal, informal in FORMAL_TO_INFORMAL.items():
        text = text.replace(formal, informal)
    return text


def _fix_question(tamil: str, original: str) -> str:
    """
    If the original input was a question, ensure Tamil output ends with '?'.
    Also adds 'ஆ?' suffix if the sentence doesn't already end with a question marker.
    """
    if not original.strip().endswith("?"):
        return tamil

    # Already ends with question mark — fine
    if tamil.endswith("?"):
        return tamil

    # Ends with common question words — just add ?
    question_endings = ["ஆ", "ஆ", "என்ன", "எப்படி", "எங்கே", "யார்", "எது", "ஏன்"]
    for ending in question_endings:
        if tamil.rstrip(".,!").endswith(ending):
            return tamil.rstrip(".,!") + "?"

    # Generic: append ஆ?
    return tamil.rstrip(".,!") + "?"
