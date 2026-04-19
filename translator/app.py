"""
app.py — Bhāsha Translator
Design: Vivid gradient BG · solid white cards · high contrast
"""

import time
import streamlit as st
from translator import get_translator, LANGUAGE_PAIRS
from history import load_history, save_to_history, clear_history
from transliteration import to_roman
from tamil_postprocess import postprocess

import streamlit.components.v1 as components

st.set_page_config(page_title="Bhāsha", page_icon="🌿", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:ital,wght@0,400;0,500;1,400&display=swap');

*, *::before, *::after { box-sizing: border-box; }
#MainMenu, footer, header { visibility: hidden; }

html, body, [class*="css"] {
    font-family: 'Inter', system-ui, sans-serif !important;
    color: #1a0533 !important;
}

/* gradient only on the outer container, nothing else touched */
[data-testid="stAppViewContainer"] > div:first-child {
    background:
        radial-gradient(ellipse 80% 60% at 70% 20%, rgba(175,109,255,0.85), transparent 68%),
        radial-gradient(ellipse 70% 60% at 20% 80%, rgba(255,100,180,0.75), transparent 68%),
        radial-gradient(ellipse 60% 50% at 60% 65%, rgba(255,235,170,0.98), transparent 68%),
        radial-gradient(ellipse 65% 40% at 50% 60%, rgba(120,190,255,0.30), transparent 68%),
        linear-gradient(180deg, #f7eaff 0%, #fde2ea 100%) !important;
}

.stApp, [data-testid="stAppViewContainer"] {
    background:
        radial-gradient(ellipse 80% 60% at 70% 20%, rgba(175,109,255,0.85), transparent 68%),
        radial-gradient(ellipse 70% 60% at 20% 80%, rgba(255,100,180,0.75), transparent 68%),
        radial-gradient(ellipse 60% 50% at 60% 65%, rgba(255,235,170,0.98), transparent 68%),
        radial-gradient(ellipse 65% 40% at 50% 60%, rgba(120,190,255,0.30), transparent 68%),
        linear-gradient(180deg, #f7eaff 0%, #fde2ea 100%) !important;
}

/* make sure inner layers don't paint over the gradient */
section.main, .main .block-container,
[data-testid="stHeader"], [data-testid="stToolbar"],
[data-testid="stDecoration"], [data-testid="stBottomBlockContainer"] {
    background: transparent !important;
}

.block-container { padding: 2.5rem 3rem 6rem !important; max-width: 1040px !important; }

.page-header { padding: 2.8rem 0 2rem; margin-bottom: 1.4rem; }
.page-eyebrow { font-family: 'JetBrains Mono', monospace; font-size: 0.62rem; letter-spacing: 0.28em; text-transform: uppercase; color: #5b21b6; font-weight: 700; margin-bottom: 14px; text-shadow: 0 1px 2px rgba(255,255,255,0.6); }
.page-title { font-size: 6rem; font-weight: 900; letter-spacing: -5px; line-height: 1; margin-bottom: 16px; color: #1a0533; }
.page-title .grad {
    background: linear-gradient(135deg, #ff6b6b 0%, #feca57 25%, #48dbfb 60%, #1dd1a1 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.page-tagline { font-size: 1.05rem; font-weight: 500; color: #1f2937; line-height: 1.65; max-width: 500px; text-shadow: 0 1px 4px rgba(255,255,255,0.5); }
.lang-pills { display: flex; gap: 8px; margin-top: 22px; flex-wrap: wrap; }
.lang-pill { font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; padding: 5px 16px; border-radius: 100px; border: 2px solid rgba(91,33,182,0.5); color: #4c1d95; background: rgba(255,255,255,0.85); letter-spacing: 0.04em; font-weight: 700; backdrop-filter: blur(4px); }

.card { background: transparent; border: none; border-radius: 0; padding: 0; box-shadow: none; margin-bottom: 16px; }
.card-panel { background: #ffffff; border: 2px solid rgba(255,255,255,0.9); border-radius: 20px; padding: 20px 22px 16px; box-shadow: 0 8px 32px rgba(91,33,182,0.18), 0 2px 8px rgba(0,0,0,0.08); }
.card-panel.output { background: #fdf4ff; border-color: rgba(221,214,254,0.8); }

.stSelectbox > label { font-family: 'JetBrains Mono', monospace !important; font-size: 0.58rem !important; letter-spacing: 0.22em !important; text-transform: uppercase !important; color: #6b7280 !important; font-weight: 600 !important; margin-bottom: 6px !important; }
.stSelectbox > div > div { background: #f9fafb !important; border: 1.5px solid #d1d5db !important; border-radius: 12px !important; color: #111827 !important; font-family: 'Inter', sans-serif !important; font-size: 0.96rem !important; font-weight: 600 !important; box-shadow: 0 1px 3px rgba(0,0,0,0.06) !important; transition: border-color 0.18s !important; }
.stSelectbox > div > div:hover { border-color: #7c3aed !important; box-shadow: 0 0 0 3px rgba(124,58,237,0.12) !important; }
[data-baseweb="popover"] { background: #ffffff !important; border: 1.5px solid #e5e7eb !important; border-radius: 14px !important; box-shadow: 0 16px 48px rgba(0,0,0,0.14) !important; }
[role="option"] { background: #ffffff !important; color: #111827 !important; font-family: 'Inter', sans-serif !important; font-size: 0.92rem !important; font-weight: 500 !important; }
[role="option"]:hover, [aria-selected="true"] { background: #f5f3ff !important; color: #7c3aed !important; }

.stButton > button { background: #ffffff !important; border: 1.5px solid #d1d5db !important; border-radius: 12px !important; color: #374151 !important; font-family: 'Inter', sans-serif !important; font-size: 1.1rem !important; font-weight: 600 !important; width: 100% !important; padding: 10px !important; transition: all 0.18s !important; box-shadow: 0 1px 3px rgba(0,0,0,0.06) !important; }
.stButton > button:hover { border-color: #7c3aed !important; color: #7c3aed !important; background: #f5f3ff !important; box-shadow: 0 4px 12px rgba(124,58,237,0.15) !important; transform: translateY(-1px) !important; }

.sec-label { font-family: 'JetBrains Mono', monospace; font-size: 0.58rem; letter-spacing: 0.24em; text-transform: uppercase; color: #7c3aed; font-weight: 700; margin-bottom: 12px; display: flex; align-items: center; gap: 8px; }
.sec-label::after { content: ''; flex: 1; height: 1.5px; background: linear-gradient(90deg, #ddd6fe, transparent); }

.stTextArea textarea { background: #ffffff !important; border: 1.5px solid #e5e7eb !important; border-radius: 14px !important; color: #111827 !important; font-family: 'Inter', sans-serif !important; font-size: 1.06rem !important; font-weight: 400 !important; line-height: 1.8 !important; padding: 16px 18px !important; resize: none !important; caret-color: #7c3aed !important; box-shadow: 0 1px 4px rgba(0,0,0,0.05) !important; transition: border-color 0.18s !important; }
.stTextArea textarea:focus { border-color: #7c3aed !important; box-shadow: 0 0 0 3px rgba(124,58,237,0.12), 0 1px 4px rgba(0,0,0,0.05) !important; outline: none !important; }
.stTextArea textarea::placeholder { color: #c4b5fd !important; font-style: italic; }
.stTextArea > div { background: transparent !important; border: none !important; box-shadow: none !important; }
.stTextArea > label { display: none !important; }

.out-box { background: #faf5ff; border: 1.5px solid #ddd6fe; border-radius: 14px; padding: 16px 18px; min-height: 172px; box-shadow: 0 1px 4px rgba(124,58,237,0.06); }
.out-text { font-family: 'JetBrains Mono', monospace; font-size: 1.02rem; line-height: 1.95; color: #1e1b4b; word-break: break-word; }
.out-empty { font-family: 'Inter', sans-serif; font-size: 0.92rem; color: #c4b5fd; font-style: italic; }

.char-row { display: flex; align-items: center; gap: 10px; margin-top: 8px; }
.char-track { flex: 1; height: 3px; background: rgba(124,58,237,0.12); border-radius: 3px; overflow: hidden; }
.char-fill { height: 100%; border-radius: 3px; transition: width 0.3s, background 0.3s; }
.char-num { font-family: 'JetBrains Mono', monospace; font-size: 0.58rem; color: #9ca3af; white-space: nowrap; font-weight: 500; }

.primary-wrap .stButton > button { background: linear-gradient(135deg, #6d28d9 0%, #7c3aed 40%, #a855f7 75%, #ec4899 100%) !important; border: none !important; border-radius: 14px !important; color: #ffffff !important; font-family: 'Inter', sans-serif !important; font-size: 1rem !important; font-weight: 700 !important; letter-spacing: 0.02em !important; padding: 14px !important; box-shadow: 0 4px 20px rgba(109,40,217,0.45), 0 1px 4px rgba(0,0,0,0.1) !important; transition: all 0.2s !important; }
.primary-wrap .stButton > button:hover { box-shadow: 0 8px 28px rgba(109,40,217,0.55), 0 2px 8px rgba(0,0,0,0.12) !important; transform: translateY(-2px) !important; filter: brightness(1.06) !important; color: #ffffff !important; }

.stDownloadButton > button { background: #ffffff !important; border: 1.5px solid #d1d5db !important; border-radius: 12px !important; color: #374151 !important; font-family: 'Inter', sans-serif !important; font-size: 0.88rem !important; font-weight: 600 !important; width: 100% !important; transition: all 0.18s !important; box-shadow: 0 1px 3px rgba(0,0,0,0.06) !important; }
.stDownloadButton > button:hover { border-color: #7c3aed !important; color: #7c3aed !important; background: #f5f3ff !important; box-shadow: 0 4px 12px rgba(124,58,237,0.15) !important; transform: translateY(-1px) !important; }

.pronun-box { background: #faf5ff; border: 1.5px solid #ddd6fe; border-left: 3px solid #a855f7; border-radius: 14px; padding: 16px 20px; margin-top: 12px; box-shadow: 0 2px 10px rgba(168,85,247,0.08); }
.pronun-label { font-family: 'JetBrains Mono', monospace; font-size: 0.56rem; letter-spacing: 0.24em; text-transform: uppercase; color: #7c3aed; font-weight: 700; margin-bottom: 10px; }
.pronun-text { font-family: 'JetBrains Mono', monospace; font-size: 0.96rem; color: #4c1d95; font-style: italic; line-height: 1.9; }

.metrics-strip { display: flex; gap: 12px; margin: 1.6rem 0 0.8rem; }
.metric-cell { flex: 1; background: #ffffff; border: 1.5px solid #e5e7eb; border-radius: 18px; padding: 18px 16px; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.05); transition: transform 0.2s, box-shadow 0.2s, border-color 0.2s; }
.metric-cell:hover { transform: translateY(-3px); box-shadow: 0 8px 24px rgba(124,58,237,0.12); border-color: #c4b5fd; }
.metric-val { font-size: 2.1rem; font-weight: 800; letter-spacing: -1.5px; line-height: 1; color: #7c3aed; }
.metric-lbl { font-family: 'JetBrains Mono', monospace; font-size: 0.54rem; letter-spacing: 0.2em; text-transform: uppercase; color: #9ca3af; margin-top: 7px; font-weight: 500; }

.msg-err { background: #faf5ff; border: 1.5px solid #ddd6fe; border-left: 3px solid #7c3aed; border-radius: 12px; padding: 13px 18px; color: #4c1d95; font-family: 'Inter', sans-serif; font-size: 0.9rem; font-weight: 500; margin-top: 10px; }

.hist-item { background: #ffffff; border: 1.5px solid #e5e7eb; border-radius: 16px; padding: 15px 20px; margin-bottom: 10px; transition: border-color 0.2s, transform 0.18s, box-shadow 0.2s; box-shadow: 0 2px 8px rgba(0,0,0,0.04); }
.hist-item:hover { border-color: #a78bfa; transform: translateX(5px); box-shadow: 0 6px 20px rgba(124,58,237,0.1); }
.hist-badge { font-family: 'JetBrains Mono', monospace; font-size: 0.6rem; letter-spacing: 0.1em; color: #7c3aed; background: #f5f3ff; border: 1.5px solid #ddd6fe; border-radius: 100px; padding: 3px 12px; display: inline-block; margin-bottom: 8px; font-weight: 600; }
.hist-time { color: #d1d5db; font-size: 0.68rem; margin-left: 8px; font-family: 'JetBrains Mono', monospace; }
.hist-src { color: #9ca3af; font-size: 0.87rem; font-style: italic; margin-bottom: 5px; }
.hist-tgt { color: #1e1b4b; font-size: 0.93rem; font-family: 'JetBrains Mono', monospace; font-weight: 500; }

.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 2px solid #e5e7eb !important;
    gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.62rem !important;
    letter-spacing: 0.18em !important;
    text-transform: uppercase !important;
    color: #9ca3af !important;
    background: transparent !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    margin-bottom: -2px !important;
    padding: 12px 26px !important;
    font-weight: 600 !important;
    transition: color 0.15s !important;
}
.stTabs [data-baseweb="tab"]:hover { color: #7c3aed !important; }
.stTabs [aria-selected="true"] {
    color: #7c3aed !important;
    border-bottom: 2px solid #7c3aed !important;
}
/* kill Streamlit's internal red/default highlight bar */
.stTabs [data-baseweb="tab-highlight"] {
    background-color: #7c3aed !important;
    height: 2px !important;
}
.stTabs [data-baseweb="tab-border"] {
    background-color: #e5e7eb !important;
    height: 2px !important;
}

.stCheckbox > label { font-family: 'Inter', sans-serif !important; font-size: 0.9rem !important; font-weight: 500 !important; color: #374151 !important; }
.stRadio > label { font-family: 'JetBrains Mono', monospace !important; font-size: 0.58rem !important; font-weight: 700 !important; color: #6b7280 !important; letter-spacing: 0.18em !important; text-transform: uppercase !important; }
.stInfo { background: #f5f3ff !important; border: 1.5px solid #ddd6fe !important; border-radius: 14px !important; color: #4c1d95 !important; }

table { border-collapse: collapse; width: 100%; }
th { background: #f5f3ff !important; color: #7c3aed !important; font-family: 'JetBrains Mono', monospace !important; font-size: 0.6rem !important; letter-spacing: 0.16em !important; text-transform: uppercase !important; padding: 12px 16px !important; border-bottom: 2px solid #ddd6fe !important; font-weight: 700 !important; }
td { background: #ffffff !important; color: #374151 !important; padding: 11px 16px !important; border-bottom: 1px solid #f3f4f6 !important; font-family: 'Inter', sans-serif !important; font-size: 0.88rem !important; }
tr:hover td { background: #faf5ff !important; }

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #f9fafb; }
::-webkit-scrollbar-thumb { background: #ddd6fe; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #7c3aed; }

.stSpinner > div { border-top-color: #7c3aed !important; }
hr { border-color: #e5e7eb !important; }
</style>
""", unsafe_allow_html=True)

if "result"      not in st.session_state: st.session_state.result      = ""
if "elapsed"     not in st.session_state: st.session_state.elapsed     = 0.0
if "total_count" not in st.session_state: st.session_state.total_count = len(load_history())
if "raw_input"   not in st.session_state: st.session_state.raw_input   = ""
if "tone"        not in st.session_state: st.session_state.tone        = "formal"

st.markdown("""
<div class="page-header">
  <div class="page-eyebrow" style="text-align:center;">neural translation engine</div>
</div>
""", unsafe_allow_html=True)

# ── Particle title ─────────────────────────────────────────────────────────────
components.html("""
<!DOCTYPE html>
<html>
<head>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  html, body { background: transparent; overflow: hidden; width: 100%; height: 100%; }
  body { display: flex; justify-content: center; align-items: center; }
  canvas { display: block; cursor: none; background: transparent; max-width: 100%; }
</style>
</head>
<body>
<canvas id="c"></canvas>
<script>
const TEXT    = "Bh\u0101sha";
const COLORS  = ['c0392b','e67e22','8e44ad','1a5276','117a65','b7950b','6c3483'];
const DENSITY = 3;
const FORCE   = 90;
const W       = 820;
const H       = 140;

const canvas  = document.getElementById('c');
const ctx     = canvas.getContext('2d');
canvas.width  = W;
canvas.height = H;

let particles = [];
let pointer   = {};
let hasPtr    = false;
let rafId     = null;
let iRadius   = 120;

function rand(max=1, min=0) { return min + Math.random() * (max - min); }

function hexToRgb(hex) {
  const n = parseInt(hex, 16);
  return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
}

class Particle {
  constructor(x, y, rgb) {
    this.ox = x; this.oy = y;
    this.cx = x; this.cy = y;
    this.r  = rand(4, 1.5);
    this.f  = rand(FORCE + 15, FORCE - 15);
    this.rgb = rgb.map(c => Math.max(0, Math.min(255, c + rand(20, -20))));
  }
  draw() {
    ctx.fillStyle = `rgb(${this.rgb.join(',')})`;
    ctx.beginPath();
    ctx.arc(this.cx, this.cy, this.r, 0, Math.PI * 2);
    ctx.fill();
  }
  move() {
    if (hasPtr && pointer.x != null) {
      const dx = this.cx - pointer.x;
      const dy = this.cy - pointer.y;
      const d  = Math.hypot(dx, dy);
      if (d < iRadius && d > 0) {
        const force = Math.min(this.f, (iRadius - d) / d * 2.5);
        this.cx += (dx / d) * force;
        this.cy += (dy / d) * force;
      }
    }
    const odx = this.ox - this.cx;
    const ody = this.oy - this.cy;
    const od  = Math.hypot(odx, ody);
    if (od > 0.5) {
      const restore = Math.min(od * 0.12, 4);
      this.cx += (odx / od) * restore;
      this.cy += (ody / od) * restore;
    }
    this.draw();
  }
}

function build() {
  ctx.clearRect(0, 0, W, H);

  const fontSize = 108;
  ctx.font = `900 ${fontSize}px "Inter", "Verdana", sans-serif`;
  ctx.textAlign    = 'left';
  ctx.textBaseline = 'middle';

  const tw = ctx.measureText(TEXT).width;
  const tx = (W - tw) / 2;
  const ty = H / 2;

  // draw gradient text
  const grad = ctx.createLinearGradient(tx, ty - fontSize/2, tx + tw, ty + fontSize/2);
  const N = COLORS.length - 1;
  COLORS.forEach((c, i) => grad.addColorStop(i / N, '#' + c));
  ctx.fillStyle = grad;
  ctx.fillText(TEXT, tx, ty);

  // sample pixels → particles
  const imgData = ctx.getImageData(0, 0, W, H).data;
  ctx.clearRect(0, 0, W, H);
  particles = [];

  for (let y = 0; y < H; y += DENSITY) {
    for (let x = 0; x < W; x += DENSITY) {
      const i = (y * W + x) * 4;
      if (imgData[i + 3] > 128) {
        const rgb = [imgData[i], imgData[i+1], imgData[i+2]];
        particles.push(new Particle(x, y, rgb));
      }
    }
  }
}

function animate() {
  ctx.clearRect(0, 0, W, H);
  particles.forEach(p => p.move());
  rafId = requestAnimationFrame(animate);
}

build();
animate();

canvas.addEventListener('pointermove', e => {
  const rect = canvas.getBoundingClientRect();
  const sx = W / rect.width;
  const sy = H / rect.height;
  pointer.x = (e.clientX - rect.left) * sx;
  pointer.y = (e.clientY - rect.top)  * sy;
  hasPtr = true;
});
canvas.addEventListener('pointerleave', () => {
  hasPtr = false;
  pointer.x = pointer.y = undefined;
});
</script>
</body>
</html>
""", height=150, scrolling=False)

st.markdown("""
<div style="margin-top:-8px; margin-bottom:1.6rem;">
  <p class="page-tagline">Translate between English, Hindi &amp; Tamil — with pronunciation guide and grammar correction.</p>
  <div class="lang-pills">
    <span class="lang-pill">EN · English</span>
    <span class="lang-pill">HI · हिन्दी</span>
    <span class="lang-pill">TA · தமிழ்</span>
  </div>
</div>
""", unsafe_allow_html=True)

LANGUAGES = ["English", "Hindi", "Tamil"]

# apply pending swap before widgets render
if "_swap_src" in st.session_state:
    st.session_state["src"] = st.session_state.pop("_swap_src")
if "_swap_tgt" in st.session_state:
    st.session_state["tgt"] = st.session_state.pop("_swap_tgt")

col_src, col_swap, col_tgt = st.columns([5, 1, 5])
with col_src:
    src = st.selectbox("From", LANGUAGES, index=0, key="src")
with col_swap:
    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
    swap = st.button("⇄", help="Swap languages")
with col_tgt:
    tgt_opts = [l for l in LANGUAGES if l != src]
    saved_tgt = st.session_state.get("tgt", tgt_opts[0])
    tgt_index = tgt_opts.index(saved_tgt) if saved_tgt in tgt_opts else 0
    tgt = st.selectbox("To", tgt_opts, index=tgt_index, key="tgt")

if swap:
    st.session_state["_swap_src"] = tgt
    st.session_state["_swap_tgt"] = src
    st.rerun()

pair_key = f"{src}→{tgt}"

col_in, col_out = st.columns(2, gap="large")

with col_in:
    st.markdown(f'<div class="sec-label">{src}</div>', unsafe_allow_html=True)
    input_text = st.text_area(label="src_input", label_visibility="collapsed", height=190, placeholder=f"Type {src} text here…", key="input_text")
    char_count = len(input_text) if input_text else 0
    pct = min(char_count / 512 * 100, 100)
    bar_color = "#7c3aed" if char_count < 450 else ("#f59e0b" if char_count < 512 else "#ef4444")
    st.markdown(f'<div class="char-row"><div class="char-track"><div class="char-fill" style="width:{pct:.1f}%;background:{bar_color};"></div></div><span class="char-num">{char_count} / 512</span></div>', unsafe_allow_html=True)

with col_out:
    st.markdown(f'<div class="sec-label">{tgt}</div>', unsafe_allow_html=True)
    if st.session_state.result:
        st.markdown(f'<div class="out-box"><div class="out-text">{st.session_state.result}</div></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="out-box"><div class="out-empty">Translation will appear here…</div></div>', unsafe_allow_html=True)

st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

if pair_key not in LANGUAGE_PAIRS:
    st.markdown(f'<div class="msg-err">⚠ Unsupported pair: <strong>{src} → {tgt}</strong>. Please choose a different combination.</div>', unsafe_allow_html=True)
else:
    btn_c, dl_c = st.columns([6, 1])
    with btn_c:
        st.markdown('<div class="primary-wrap">', unsafe_allow_html=True)
        clicked = st.button("Translate →", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with dl_c:
        if st.session_state.result:
            st.download_button("↓ Save", data=st.session_state.result, file_name="translation.txt", use_container_width=True, help="Save translation")

    if clicked:
        if not input_text or not input_text.strip():
            st.markdown('<div class="msg-err">Please enter some text to translate.</div>', unsafe_allow_html=True)
        else:
            with st.spinner("Translating…"):
                try:
                    t0 = time.time()
                    result = get_translator(pair_key)(input_text.strip())
                    if tgt == "Tamil":
                        result = postprocess(result, original_input=input_text.strip(), tone=st.session_state.get("tone", "formal"))
                    elapsed = round(time.time() - t0, 2)
                    st.session_state.result = result
                    st.session_state.raw_input = input_text.strip()
                    st.session_state.elapsed = elapsed
                    st.session_state.total_count += 1
                    save_to_history(src, tgt, input_text.strip(), result)
                    st.rerun()
                except Exception as e:
                    st.markdown(f'<div class="msg-err">{e}</div>', unsafe_allow_html=True)

if tgt == "Tamil" and st.session_state.result:
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    tone_col, _ = st.columns([3, 7])
    with tone_col:
        tone = st.radio("Tone", options=["formal", "informal"], format_func=lambda x: "🎩 Formal" if x == "formal" else "😊 Informal", horizontal=True, key="tone")
    if st.session_state.raw_input:
        live = postprocess(st.session_state.result, original_input=st.session_state.raw_input, tone=tone)
        if live != st.session_state.result:
            st.session_state.result = live
            st.rerun()

if st.session_state.result and tgt in ("Tamil", "Hindi"):
    label = "Tanglish" if tgt == "Tamil" else "Hinglish"
    show = st.checkbox(f"Show {label} pronunciation", key="show_pronun")
    if show:
        roman = to_roman(st.session_state.result, tgt)
        if roman:
            st.markdown(f'<div class="pronun-box"><div class="pronun-label">✦ {label} pronunciation</div><div class="pronun-text">{roman}</div></div>', unsafe_allow_html=True)

if st.session_state.result:
    wc = len(input_text.split()) if input_text else 0
    st.markdown(f'<div class="metrics-strip"><div class="metric-cell"><div class="metric-val">{st.session_state.elapsed}s</div><div class="metric-lbl">Response time</div></div><div class="metric-cell"><div class="metric-val">{wc}</div><div class="metric-lbl">Words</div></div><div class="metric-cell"><div class="metric-val">{st.session_state.total_count}</div><div class="metric-lbl">Total translations</div></div></div>', unsafe_allow_html=True)

st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
tab1, tab2 = st.tabs(["  History  ", "  Sample Phrases  "])

with tab1:
    history = load_history()
    if not history:
        st.info("No translations yet. Try translating something above.")
    else:
        hc1, hc2 = st.columns([9, 1])
        with hc2:
            if st.button("Clear", help="Clear all history"):
                clear_history()
                st.session_state.total_count = 0
                st.rerun()
        for item in reversed(history[-12:]):
            st.markdown(
                f'<div class="hist-item">'
                f'<span class="hist-badge">{item["src"]} → {item["tgt"]}</span>'
                f'<span class="hist-time">{item["time"]}</span><br>'
                f'<div class="hist-src">"{item["input"]}"</div>'
                f'<div class="hist-tgt">{item["output"]}</div>'
                f'</div>',
                unsafe_allow_html=True
            )

with tab2:
    st.markdown("""
| Pair | Input | Output | Pronunciation |
|------|-------|--------|---------------|
| EN → HI | Hello, how are you? | नमस्ते, आप कैसे हैं? | namaste, aap kaise hain? |
| EN → HI | Good morning | सुप्रभात | suprabhat |
| EN → TA | How are you? | நீங்கள் எப்படி இருக்கிறீர்கள்? | neenga eppadi irukkinga? |
| EN → TA | Thank you | மிக்க நன்றி | mikka nandri |
| HI → EN | मैं ठीक हूँ | I am fine | — |
| TA → EN | வணக்கம் | Greetings | — |
| HI → TA | नमस्ते | வணக்கம் | vanakkam |
""")

st.markdown("""
<div style="margin-top:3.5rem; padding-top:1.6rem; border-top:1px solid #e5e7eb; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px; font-family:'JetBrains Mono',monospace; font-size:0.56rem; letter-spacing:0.18em; text-transform:uppercase; color:#9ca3af;">
  <span>HuggingFace · MarianMT · NLLB-200 · Streamlit</span>
  <span style="color:#a78bfa;">✦ First run downloads models (~300 MB)</span>
</div>
""", unsafe_allow_html=True)
