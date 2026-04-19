# Bhāsha  🌿

A beautiful neural translation engine supporting English, Hindi, and Tamil with pronunciation guides and grammar correction.

## Features

✨ **Multi-language Translation**
- English ↔ Hindi
- English ↔ Tamil  
- Hindi ↔ Tamil

🎯 **Smart Post-processing**
- Natural Tamil grammar correction
- Formal/Informal tone modes
- Pronunciation guides (Tanglish/Hinglish)

🎨 **Beautiful UI**
- Interactive particle text animation
- Gradient backgrounds
- Clean, modern design
- Real-time character counter

📊 **Translation History**
- Automatic history tracking
- Sample phrases reference
- Translation metrics

## Tech Stack

- **Frontend**: Streamlit
- **Models**: 
  - MarianMT (Helsinki-NLP) for English ↔ Hindi
  - NLLB-200 (Facebook) for Tamil translations
- **Libraries**: PyTorch, Transformers, Aksharamukha

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Purvii15/Bhasha-AI.git
cd Bhasha-AI
```

2. Create virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r translator/requirements.txt
```

## Usage

Run the Streamlit app:
```bash
streamlit run translator/app.py
```

The app will open in your browser at `http://localhost:8501`

**Note**: First run will download models (~300 MB for MarianMT, ~1.2 GB for NLLB-200)

## Project Structure

```
Bhasha-AI/
├── translator/
│   ├── app.py                    # Main Streamlit application
│   ├── translator.py             # Translation engine
│   ├── history.py                # History management
│   ├── transliteration.py        # Romanization (Tanglish/Hinglish)
│   ├── tamil_postprocess.py      # Tamil grammar correction
│   └── requirements.txt          # Python dependencies
├── .gitignore
└── README.md
```

## Features in Detail

### Translation Engine
- Uses state-of-the-art neural machine translation models
- Cached models for fast subsequent translations
- Supports up to 512 characters per translation

### Tamil Post-processing
- Converts formal/robotic output to natural spoken Tamil
- Grammar correction based on linguistic rules
- Tone switching (formal/informal)

### Pronunciation Guide
- Tanglish for Tamil text
- Hinglish for Hindi text
- Clean, readable romanization

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

## License

MIT License

## Author

Purvi - [GitHub](https://github.com/Purvii15)

---

Made with ❤️ using Streamlit and HuggingFace Transformers
