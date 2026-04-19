# 🌐 Multilingual Translator — English ↔ Hindi ↔ Tamil

A Streamlit web app that translates text between English, Hindi, and Tamil using
HuggingFace MarianMT transformer models.

---

## Project Structure

```
translator/
├── app.py           # Streamlit UI
├── translator.py    # Model loading + translation logic
├── history.py       # Save/load translation history
├── requirements.txt
└── README.md
```

---

## Run Locally

### 1. Install dependencies
```bash
cd translator
pip install -r requirements.txt
```

### 2. Start the app
```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`

> First run downloads the MarianMT models (~300MB each). They are cached locally after that.

---

## Supported Language Pairs

| Pair | Model |
|------|-------|
| English → Hindi | Helsinki-NLP/opus-mt-en-hi |
| Hindi → English | Helsinki-NLP/opus-mt-hi-en |
| English → Tamil | Helsinki-NLP/opus-mt-en-ta |
| Tamil → English | Helsinki-NLP/opus-mt-ta-en |
| Hindi → Tamil   | Helsinki-NLP/opus-mt-hi-ta |
| Tamil → Hindi   | Helsinki-NLP/opus-mt-ta-hi |

---

## Deploy on Streamlit Cloud

1. Push this folder to a GitHub repo
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repo, set `app.py` as the entry point
4. Deploy — Streamlit Cloud installs requirements automatically

## Deploy on HuggingFace Spaces

1. Create a new Space at [huggingface.co/spaces](https://huggingface.co/spaces)
2. Choose **Streamlit** as the SDK
3. Upload all files
4. HuggingFace will install `requirements.txt` and launch the app

---

## Architecture

```
User Input (Streamlit UI)
        ↓
  translator.py
        ↓
  @st.cache_resource  ← loads model ONCE, reuses on every request
        ↓
  MarianTokenizer → MarianMTModel.generate() → decode
        ↓
  Translated Text (Streamlit UI)
        ↓
  history.py → translation_history.json
```

## Model Choice — Why MarianMT?

- **Lightweight**: ~300MB per model vs multi-GB for GPT-style models
- **Fast**: runs on CPU in 1–3 seconds
- **No API key needed**: fully local
- **Good quality**: trained on OPUS parallel corpus (millions of sentence pairs)

## Limitations

- Idiomatic expressions may not translate perfectly
- Very long texts (>512 tokens) are truncated
- Tamil script rendering depends on your system fonts
- Hindi/Tamil → Hindi/Tamil requires a pivot through English if direct model unavailable
