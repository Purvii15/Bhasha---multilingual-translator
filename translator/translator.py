"""
translator.py — Translation logic using two model backends:
  - MarianMT  (Helsinki-NLP) for English ↔ Hindi  [fast, ~300MB]
  - NLLB-200  (Facebook)     for all Tamil pairs   [supports 200 langs, ~1.2GB]

Models are cached with @st.cache_resource — loaded ONCE, reused forever.
"""

import torch
import streamlit as st
from transformers import MarianMTModel, MarianTokenizer
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

# ── Language pair config ──────────────────────────────────────────────────────
# Each entry: (backend, model_name, src_lang_code, tgt_lang_code)
# lang codes only needed for NLLB (flores200 format)

LANGUAGE_PAIRS = {
    "English→Hindi": ("marian", "Helsinki-NLP/opus-mt-en-hi",  None,       None),
    "Hindi→English": ("marian", "Helsinki-NLP/opus-mt-hi-en",  None,       None),
    "English→Tamil": ("nllb",   "facebook/nllb-200-distilled-600M", "eng_Latn", "tam_Taml"),
    "Tamil→English": ("nllb",   "facebook/nllb-200-distilled-600M", "tam_Taml", "eng_Latn"),
    "Hindi→Tamil":   ("nllb",   "facebook/nllb-200-distilled-600M", "hin_Deva", "tam_Taml"),
    "Tamil→Hindi":   ("nllb",   "facebook/nllb-200-distilled-600M", "tam_Taml", "hin_Deva"),
}


# ── MarianMT loader (cached) ──────────────────────────────────────────────────
@st.cache_resource(show_spinner="Loading MarianMT model... (first time only)")
def _load_marian(model_name: str):
    tokenizer = MarianTokenizer.from_pretrained(model_name)
    model = MarianMTModel.from_pretrained(model_name)
    model.eval()
    return tokenizer, model


# ── NLLB loader (cached) ──────────────────────────────────────────────────────
@st.cache_resource(show_spinner="Loading NLLB-200 model... (first time only, ~1.2GB)")
def _load_nllb(model_name: str):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    model.eval()
    return tokenizer, model


# ── Translation functions ─────────────────────────────────────────────────────
def _translate_marian(text: str, model_name: str) -> str:
    tokenizer, model = _load_marian(model_name)
    inputs = tokenizer(
        [text],
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=512
    )
    with torch.no_grad():
        ids = model.generate(**inputs, num_beams=4, max_length=512, early_stopping=True)
    return tokenizer.decode(ids[0], skip_special_tokens=True)


def _translate_nllb(text: str, model_name: str, src_lang: str, tgt_lang: str) -> str:
    tokenizer, model = _load_nllb(model_name)

    # NLLB requires setting the source language on the tokenizer
    tokenizer.src_lang = src_lang
    inputs = tokenizer(
        text,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=512
    )

    # forced_bos_token_id tells the model which language to output
    tgt_lang_id = tokenizer.convert_tokens_to_ids(tgt_lang)

    with torch.no_grad():
        ids = model.generate(
            **inputs,
            forced_bos_token_id=tgt_lang_id,
            num_beams=4,
            max_length=512,
            early_stopping=True
        )
    return tokenizer.decode(ids[0], skip_special_tokens=True)


# ── Public API ────────────────────────────────────────────────────────────────
def get_translator(pair_key: str):
    """
    Returns a callable that translates text for the given language pair.
    Usage: fn = get_translator("English→Tamil"); result = fn("Hello")
    """
    if pair_key not in LANGUAGE_PAIRS:
        raise ValueError(f"Unsupported language pair: {pair_key}")

    backend, model_name, src_lang, tgt_lang = LANGUAGE_PAIRS[pair_key]

    if backend == "marian":
        return lambda text: _translate_marian(text, model_name)
    else:
        return lambda text: _translate_nllb(text, model_name, src_lang, tgt_lang)
