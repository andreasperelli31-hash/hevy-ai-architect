import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import google.genai as genai
import os
import json
from typing import Optional

# File per salvare le preferenze utente
PREFS_FILE = os.path.join(os.path.dirname(__file__), "user_preferences.json")

def load_preferences():
    """Carica le preferenze salvate dall'ultimo uso."""
    defaults = {
        "goals": ["Ipertrofia (Massa)"],
        "days": 4,
        "split_type": "Full Body",
        "focus_area": [],
        "equipment_pref": "Con attrezzi",
        "sex_pref": "Maschio",
        "age": 30,
        "training_level": "Beginner",
        "duration": 60
    }
    try:
        if os.path.exists(PREFS_FILE):
            with open(PREFS_FILE, "r") as f:
                saved = json.load(f)
                defaults.update(saved)
    except Exception:
        pass
    return defaults

def save_preferences(prefs: dict):
    """Salva le preferenze correnti su file."""
    try:
        with open(PREFS_FILE, "w") as f:
            json.dump(prefs, f)
    except Exception:
        pass

def get_api_key():
    """Ottiene la API key da Streamlit secrets o variabile d'ambiente."""
    # Prima prova Streamlit secrets (per Streamlit Cloud)
    try:
        return st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass
    # Poi prova variabile d'ambiente
    env_key = os.environ.get("GEMINI_API_KEY")
    if env_key:
        return env_key
    # Nessuna chiave trovata
    return None

# Carica preferenze all'avvio
saved_prefs = load_preferences()

# --- CONFIGURAZIONE ---
st.set_page_config(
    page_title="Hevy AI Architect", 
    page_icon="🏋️‍♂️", 
    layout="wide",
    initial_sidebar_state="collapsed"  # Migliore per mobile
)

# --- CSS PERSONALIZZATO PER MOBILE E DESIGN PROFESSIONALE ---
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Font globale */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Background principale */
    .stApp {
        background: #1a1a2e;
    }
    
    /* Header principale */
    .main-header {
        background: linear-gradient(135deg, #FF4B4B 0%, #FF6B6B 50%, #FF8E53 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 2.8rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    
    .sub-header {
        text-align: center;
        color: #E0E0E0;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    /* ===== SIDEBAR ===== */
    [data-testid="stSidebar"] {
        background: #16213e !important;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        background: #16213e !important;
    }
    
    /* Titoli sidebar */
    [data-testid="stSidebar"] h3 {
        color: #FFFFFF !important;
        font-size: 1.2rem !important;
        font-weight: 600 !important;
    }
    
    [data-testid="stSidebar"] .stMarkdown h2 {
        color: #FF6B6B !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        margin-top: 1rem !important;
        margin-bottom: 0.8rem !important;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid rgba(255,107,107,0.4);
    }
    
    /* LABEL dei campi - ALTA VISIBILITÀ */
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stMultiSelect label,
    [data-testid="stSidebar"] .stSlider label {
        color: #FFFFFF !important;
        font-weight: 500 !important;
        font-size: 0.95rem !important;
    }
    
    /* Testo generale sidebar */
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span {
        color: #E8E8E8 !important;
    }
    
    /* Selectbox styling */
    [data-testid="stSidebar"] .stSelectbox > div > div {
        background-color: #1f2b47 !important;
        border: 1px solid #3d5a80 !important;
        color: #FFFFFF !important;
    }
    
    /* Multiselect styling */
    [data-testid="stSidebar"] .stMultiSelect > div > div {
        background-color: #1f2b47 !important;
        border: 1px solid #3d5a80 !important;
    }
    
    [data-testid="stSidebar"] .stMultiSelect span {
        color: #FFFFFF !important;
    }
    
    /* Slider value */
    [data-testid="stSidebar"] .stSlider [data-testid="stTickBarMin"],
    [data-testid="stSidebar"] .stSlider [data-testid="stTickBarMax"] {
        color: #FFFFFF !important;
    }
    
    /* ===== METRICHE ===== */
    [data-testid="stMetric"] {
        background: linear-gradient(145deg, #1f2b47 0%, #16213e 100%);
        padding: 1rem 1.5rem;
        border-radius: 12px;
        border: 1px solid rgba(255, 107, 107, 0.2);
    }
    
    [data-testid="stMetric"] label {
        color: #FF8E8E !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
    }
    
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #FFFFFF !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
    }
    
    /* ===== BOTTONI ===== */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #FF4B4B 0%, #FF6B6B 100%);
        color: white !important;
        border: none;
        border-radius: 12px;
        padding: 0.8rem 1.5rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(255,75,75,0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255,75,75,0.5);
        background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%);
    }
    
    /* Download button */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #00C853 0%, #00E676 100%);
        color: white !important;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(0,200,83,0.3);
    }
    
    .stDownloadButton > button:hover {
        box-shadow: 0 6px 20px rgba(0,200,83,0.5);
    }
    
    /* ===== SLIDER ===== */
    .stSlider > div > div > div {
        background-color: #FF6B6B !important;
        border-radius: 10px !important;
    }
    
    .stSlider [data-baseweb="slider"] {
        background-color: rgba(255,107,107,0.3) !important;
        border-radius: 10px !important;
    }
    
    .stSlider [data-baseweb="slider"] > div {
        border-radius: 10px !important;
    }
    
    .stSlider [data-baseweb="slider"] > div > div {
        border-radius: 10px !important;
    }
    
    /* ===== TABELLE ===== */
    .stMarkdown table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        border-radius: 12px;
        overflow: hidden;
        margin: 1rem 0;
        background: #1f2b47;
    }
    
    .stMarkdown th {
        background: linear-gradient(135deg, #FF4B4B 0%, #FF6B6B 100%);
        color: white !important;
        padding: 12px 8px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    
    .stMarkdown td {
        padding: 10px 8px;
        border-bottom: 1px solid rgba(255,255,255,0.1);
        font-size: 0.9rem;
        color: #E8E8E8 !important;
    }
    
    .stMarkdown tr:hover td {
        background: rgba(255,107,107,0.15);
    }
    
    /* ===== DATAFRAME ===== */
    [data-testid="stDataFrame"] {
        background: #1f2b47;
        border-radius: 12px;
        padding: 0.5rem;
    }
    
    /* ===== EXPANDER ===== */
    .streamlit-expanderHeader {
        background: #1f2b47 !important;
        border-radius: 8px;
        color: #FFFFFF !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
    }
    
    .streamlit-expanderHeader p, .streamlit-expanderHeader span {
        color: #FFB347 !important;
        font-weight: 600 !important;
    }
    
    .streamlit-expanderContent {
        background: #16213e;
        border-radius: 0 0 8px 8px;
    }
    
    /* ===== SUCCESS/ERROR MESSAGES ===== */
    .stSuccess {
        background-color: rgba(0, 200, 83, 0.15) !important;
        color: #00E676 !important;
    }
    
    .stError {
        background-color: rgba(255, 75, 75, 0.15) !important;
    }
    
    /* ===== SPINNER / LOADING ===== */
    .stSpinner > div {
        color: #FFFFFF !important;
    }
    
    .stSpinner > div > span {
        color: #FFFFFF !important;
        font-size: 1.1rem !important;
        font-weight: 500 !important;
    }
    
    /* Testo generico nell'area principale */
    .stMarkdown, .stMarkdown p, .stMarkdown span {
        color: #E8E8E8 !important;
    }
    
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {
        color: #FFFFFF !important;
    }
    
    /* Alert/Info boxes */
    .stAlert, [data-testid="stNotification"] {
        color: #FFFFFF !important;
    }
    
    .stAlert p, [data-testid="stNotification"] p {
        color: #FFFFFF !important;
    }
    
    /* ===== RISULTATI ===== */
    .result-card {
        background: linear-gradient(145deg, #1f2b47 0%, #16213e 100%);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid rgba(255,107,107,0.2);
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        overflow-x: auto;
    }
    
    /* Tabelle scrollabili su mobile */
    .result-card table {
        width: 100%;
        min-width: 500px;
    }
    
    /* ===== MOBILE ===== */
    @media (max-width: 768px) {
        .main-header {
            font-size: 1.6rem;
            padding: 0 10px;
        }
        
        .sub-header {
            font-size: 0.85rem;
            padding: 0 10px;
        }
        
        [data-testid="stSidebar"] {
            width: 100% !important;
        }
        
        .stButton > button {
            padding: 0.8rem;
            font-size: 1rem;
        }
        
        /* Tabelle più leggibili su mobile */
        .stMarkdown table {
            display: block;
            overflow-x: auto;
            white-space: nowrap;
            -webkit-overflow-scrolling: touch;
        }
        
        .stMarkdown th, .stMarkdown td {
            padding: 6px 4px;
            font-size: 0.7rem;
            min-width: 60px;
        }
        
        .stMarkdown th:first-child, .stMarkdown td:first-child {
            min-width: 100px;
        }
        
        [data-testid="stMetric"] {
            padding: 0.6rem;
        }
        
        [data-testid="stMetric"] [data-testid="stMetricValue"] {
            font-size: 1.3rem !important;
        }
        
        [data-testid="stMetric"] label {
            font-size: 0.75rem !important;
        }
        
        /* Result card mobile */
        .result-card {
            padding: 1rem;
            margin: 0.5rem 0;
            border-radius: 12px;
        }
        
        /* Columns su mobile */
        [data-testid="column"] {
            padding: 0 5px !important;
        }
        
        /* Download button mobile */
        .stDownloadButton > button {
            padding: 0.8rem;
            font-size: 0.95rem;
        }
    }
    
    /* Extra small devices */
    @media (max-width: 480px) {
        .main-header {
            font-size: 1.4rem;
        }
        
        .sub-header {
            font-size: 0.8rem;
        }
        
        [data-testid="stMetric"] [data-testid="stMetricValue"] {
            font-size: 1.1rem !important;
        }
        
        .stMarkdown th, .stMarkdown td {
            font-size: 0.65rem;
            padding: 4px 2px;
        }
    }
    
    /* ===== FOOTER ===== */
    .footer {
        text-align: center;
        padding: 2rem;
        color: #D0D0D0;
        font-size: 0.9rem;
        margin-top: 3rem;
        border-top: 1px solid rgba(255,255,255,0.15);
    }
    
    .footer p {
        color: #D0D0D0 !important;
        margin: 0.3rem 0;
    }
    
    .footer strong {
        color: #FF6B6B;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Divider */
    hr {
        border-color: rgba(255,107,107,0.3) !important;
    }
    
    /* ===== GALLERY IMAGES ===== */
    .gallery-container {
        display: flex;
        justify-content: center;
        align-items: stretch;
        gap: 20px;
        margin: 2rem auto;
        padding: 20px;
        width: 100%;
        max-width: 1400px;
    }
    
    .gallery-image {
        position: relative;
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 8px 32px rgba(255, 75, 75, 0.3);
        border: 3px solid transparent;
        background: linear-gradient(145deg, #1f2b47, #16213e) padding-box,
                    linear-gradient(135deg, #FF4B4B 0%, #FF6B6B 50%, #FF8E53 100%) border-box;
        animation: fadeInUp 1s ease-out forwards;
        opacity: 0;
        transform: translateY(20px);
        flex: 1;
        max-width: 48%;
    }
    
    .gallery-image:nth-child(1) {
        animation-delay: 0.2s;
    }
    
    .gallery-image:nth-child(2) {
        animation-delay: 0.5s;
    }
    
    .gallery-image img {
        display: block;
        width: 100%;
        height: auto;
        border-radius: 13px;
        transition: transform 0.4s ease;
    }
    
    .gallery-image:hover img {
        transform: scale(1.03);
    }
    
    .gallery-image::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(135deg, rgba(255,75,75,0.1) 0%, transparent 50%);
        pointer-events: none;
        z-index: 1;
        border-radius: 13px;
    }
    
    @keyframes fadeInUp {
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @media (max-width: 768px) {
        .gallery-container {
            flex-direction: row;
            gap: 10px;
            padding: 10px;
        }
        
        .gallery-image {
            max-width: 48%;
        }
        
        .gallery-image img {
            max-width: 100%;
            max-height: 200px;
            object-fit: cover;
        }
    }
    
    @media (max-width: 480px) {
        .gallery-container {
            gap: 8px;
            padding: 8px;
        }
        
        .gallery-image img {
            max-height: 150px;
        }
    }
    
    /* ===== GALLERY FOOTER (dopo generazione scheda) ===== */
    .gallery-footer {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 15px;
        margin: 1rem auto;
        padding: 15px;
        max-width: 600px;
        animation: slideDownFade 0.8s ease-out forwards;
    }
    
    .gallery-footer .gallery-image {
        flex: 1;
        max-width: 280px;
        animation: none;
        opacity: 1;
        transform: none;
    }
    
    .gallery-footer .gallery-image img {
        max-height: 180px;
        object-fit: cover;
    }
    
    @keyframes slideDownFade {
        from {
            opacity: 0;
            transform: translateY(-30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @media (max-width: 768px) {
        .gallery-footer {
            flex-direction: row;
            gap: 8px;
            padding: 10px;
            max-width: 100%;
        }
        
        .gallery-footer .gallery-image {
            max-width: 48%;
        }
        
        .gallery-footer .gallery-image img {
            max-height: 100px;
        }
    }
    
    @media (max-width: 480px) {
        .gallery-footer .gallery-image img {
            max-height: 80px;
        }
    }
</style>
""", unsafe_allow_html=True)

# Ottieni API key
GOOGLE_API_KEY = get_api_key()

# Verifica che la chiave sia configurata
if not GOOGLE_API_KEY:
    st.error("⚠️ API Key non configurata! Aggiungi GEMINI_API_KEY nei secrets di Streamlit Cloud o come variabile d'ambiente.")
    st.stop()

# Configura il modello
try:
    client = genai.Client(api_key=GOOGLE_API_KEY)
except Exception as e:
    st.error(f"Errore configurazione API: {e}")
    st.stop()

# Stato iniziale per la scheda generata
if "plan_md" not in st.session_state:
    st.session_state["plan_md"] = ""


def build_pdf_from_markdown(md_text: str) -> Optional[bytes]:
    """Crea un PDF dal markdown con supporto migliorato alle tabelle."""
    try:
        from fpdf import FPDF
    except ImportError:
        st.error("Installa il pacchetto fpdf: pip install fpdf==1.7.2")
        return None

    def sanitize_text(text):
        """Rimuove o sostituisce caratteri non supportati da latin-1."""
        # Mappa emoji e caratteri speciali a testo ASCII
        replacements = {
            '✅': '[OK]', '❌': '[X]', '⚠️': '[!]', '💪': '', '🎯': '', 
            '🤖': '', '📅': '', '📋': '', '🏠': '', '⚧': '', '🎂': '',
            '📊': '', '⏱️': '', '🚀': '', '📥': '', '📚': '', '🏋️': '',
            '❤️': '', '→': '->', '←': '<-', '↔': '<->', '•': '-',
            '–': '-', '—': '-', '"': '"', '"': '"', ''': "'", ''': "'",
            '…': '...', '°': 'deg', '×': 'x', '÷': '/', '≤': '<=',
            '≥': '>=', '≠': '!=', '±': '+/-', '€': 'EUR', '£': 'GBP',
            '¥': 'YEN', '©': '(c)', '®': '(R)', '™': '(TM)',
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        # Rimuovi tutti i caratteri non latin-1
        try:
            return text.encode('latin-1', errors='ignore').decode('latin-1')
        except Exception:
            # Fallback: rimuovi tutti i caratteri non ASCII
            return ''.join(c if ord(c) < 128 else '' for c in text)

    # Pulisci il testo markdown all'inizio
    md_text = sanitize_text(md_text)

    pdf = FPDF(orientation='L', format='A4')  # Landscape per tabelle più larghe
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=10)
    
    page_width = pdf.w - pdf.l_margin - pdf.r_margin
    page_height = pdf.h - pdf.t_margin - pdf.b_margin
    
    def clean_markdown(text):
        """Rimuove i marcatori markdown dal testo."""
        return text.replace("**", "").replace("*", "").replace("__", "").replace("_", "")
    
    def is_bold_text(text):
        """Controlla se il testo è in grassetto markdown."""
        return text.strip().startswith("**") and text.strip().endswith("**")

    def estimate_table_height(rows, row_height):
        """Stima l'altezza totale della tabella."""
        return len(rows) * row_height + 5

    def render_table(table_lines):
        # Parse table lines
        rows = []
        for line in table_lines:
            stripped = line.strip()
            if stripped.startswith("|") and stripped.endswith("|"):
                cells = stripped.split("|")[1:-1]
                cells = [cell.strip() for cell in cells]
                rows.append(cells)
            elif "|" in stripped:
                cells = [cell.strip() for cell in stripped.strip("|").split("|")]
                rows.append(cells)
        
        if not rows:
            return
        
        # Remove separator row (dashes like |---|---|)
        cleaned_rows = []
        for r in rows:
            is_separator = all(
                set(c.replace(" ", "").replace(":", "")) <= set("-") 
                for c in r if c
            )
            if not is_separator:
                cleaned_rows.append(r)
        
        rows = cleaned_rows
        if not rows:
            return
        
        # Determine column count from header
        col_count = len(rows[0]) if rows else 5
        
        # Fixed column widths for workout tables (5 columns)
        # Esercizio: 55mm, Serie: 12mm, Ripetizioni: 18mm, Recupero: 16mm, Note: resto (ampia)
        if col_count == 5:
            # Esercizio | Serie | Ripetizioni | Recupero | Note Tecniche
            col_widths = [55, 12, 18, 16, page_width - 101]
        elif col_count == 4:
            col_widths = [50, 20, 25, page_width - 95]
        else:
            col_widths = [page_width / col_count] * col_count
        
        total_width = sum(col_widths)
        if total_width > page_width:
            scale = page_width / total_width
            col_widths = [w * scale for w in col_widths]
        
        base_row_height = 5
        
        def calc_row_height(row_cells, widths, font_size=6):
            """Calcola l'altezza necessaria per una riga basata sul testo più lungo."""
            max_lines = 1
            for i, cell_text in enumerate(row_cells[:len(widths)]):
                clean_text = clean_markdown(cell_text)
                # Stima caratteri per linea basata sulla larghezza colonna
                chars_per_line = max(1, int(widths[i] / (font_size * 0.4)))
                if clean_text:
                    lines_needed = max(1, (len(clean_text) + chars_per_line - 1) // chars_per_line)
                    max_lines = max(max_lines, lines_needed)
            return max(base_row_height, max_lines * base_row_height)
        
        # Stima altezza tabella
        table_height = sum(calc_row_height(r, col_widths) for r in rows) + 10
        space_left = pdf.h - pdf.b_margin - pdf.get_y()
        
        # Se la tabella non entra, vai a nuova pagina
        if table_height > space_left and space_left < page_height * 0.5:
            pdf.add_page()
        
        # Render header
        pdf.set_font("Arial", "B", 7)
        pdf.set_fill_color(220, 220, 220)
        
        if rows:
            header = rows[0]
            while len(header) < len(col_widths):
                header.append("")
            for i, cell_text in enumerate(header[:len(col_widths)]):
                clean_text = clean_markdown(cell_text)
                pdf.cell(col_widths[i], base_row_height, clean_text, border=1, ln=0, align="C", fill=True)
            pdf.ln(base_row_height)
        
        # Render data rows con supporto multi-linea
        pdf.set_font("Arial", "", 6)
        for r in rows[1:]:
            while len(r) < len(col_widths):
                r.append("")
            
            first_cell = r[0] if r else ""
            is_section_row = is_bold_text(first_cell)
            
            # Calcola altezza riga necessaria
            row_h = calc_row_height(r, col_widths)
            
            # Check if we need a new page for this row
            if pdf.get_y() + row_h > pdf.h - pdf.b_margin:
                pdf.add_page()
                # Reprint header on new page
                pdf.set_font("Arial", "B", 7)
                pdf.set_fill_color(220, 220, 220)
                header = rows[0]
                for i, cell_text in enumerate(header[:len(col_widths)]):
                    clean_text = clean_markdown(cell_text)
                    pdf.cell(col_widths[i], base_row_height, clean_text, border=1, ln=0, align="C", fill=True)
                pdf.ln(base_row_height)
                pdf.set_font("Arial", "", 6)
            
            # Salva posizione Y iniziale della riga
            y_start = pdf.get_y()
            x_start = pdf.l_margin
            
            # Prima passa: disegna le celle con bordi e testo
            for i, cell_text in enumerate(r[:len(col_widths)]):
                clean_text = clean_markdown(cell_text)
                
                if is_section_row and i == 0:
                    pdf.set_font("Arial", "B", 6)
                else:
                    pdf.set_font("Arial", "", 6)
                
                # Posiziona alla colonna corretta
                x_pos = x_start + sum(col_widths[:i])
                pdf.set_xy(x_pos, y_start)
                
                # Disegna bordo cella
                pdf.rect(x_pos, y_start, col_widths[i], row_h)
                
                # Per l'ultima colonna (Note), usa multi_cell per testo lungo
                if i == len(col_widths) - 1 and len(clean_text) > 30:
                    pdf.set_xy(x_pos + 1, y_start + 0.5)
                    # Multi_cell senza bordo, il bordo è già disegnato
                    old_l_margin = pdf.l_margin
                    old_r_margin = pdf.r_margin
                    pdf.set_left_margin(x_pos + 1)
                    pdf.set_right_margin(pdf.w - x_pos - col_widths[i] + 1)
                    pdf.multi_cell(col_widths[i] - 2, base_row_height - 1, clean_text, border=0, align="L")
                    pdf.set_left_margin(old_l_margin)
                    pdf.set_right_margin(old_r_margin)
                else:
                    # Celle normali: tronca se necessario
                    chars_per_line = max(1, int(col_widths[i] / 2.5))
                    display_text = clean_text[:chars_per_line] if len(clean_text) > chars_per_line else clean_text
                    pdf.set_xy(x_pos + 0.5, y_start + (row_h - base_row_height) / 2 + 0.5)
                    pdf.cell(col_widths[i] - 1, base_row_height, display_text, border=0, ln=0, align="L")
            
            # Muovi alla prossima riga
            pdf.set_y(y_start + row_h)
        
        pdf.ln(3)

    # Process markdown
    pdf.set_font("Arial", "", 10)
    lines = md_text.splitlines()
    buffer_table = []
    
    for line in lines:
        stripped = line.strip()
        
        # Detect table lines
        if stripped.startswith("|"):
            buffer_table.append(line)
            continue
        
        # Flush table buffer if we were in a table
        if buffer_table:
            render_table(buffer_table)
            buffer_table = []
        
        # Handle headers
        if stripped.startswith("###"):
            pdf.set_font("Arial", "B", 11)
            clean_text = clean_markdown(stripped.replace("#", "").strip())
            pdf.multi_cell(0, 6, txt=clean_text)
            pdf.set_font("Arial", "", 10)
        elif stripped.startswith("##"):
            pdf.set_font("Arial", "B", 12)
            clean_header = clean_markdown(stripped.replace("#", "").strip())
            pdf.multi_cell(0, 7, txt=clean_header)
            pdf.set_font("Arial", "", 10)
        elif stripped.startswith("#"):
            pdf.set_font("Arial", "B", 14)
            clean_header = clean_markdown(stripped.replace("#", "").strip())
            pdf.multi_cell(0, 8, txt=clean_header)
            pdf.set_font("Arial", "", 10)
        elif stripped.startswith("---"):
            pdf.ln(2)
            pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
            pdf.ln(2)
        elif stripped:
            # Check if text is bold
            if is_bold_text(stripped):
                pdf.set_font("Arial", "B", 10)
                clean_text = clean_markdown(stripped)
                pdf.multi_cell(0, 5, txt=clean_text)
                pdf.set_font("Arial", "", 10)
            else:
                clean_text = clean_markdown(stripped)
                pdf.multi_cell(0, 5, txt=clean_text)
        else:
            pdf.ln(2)
    
    # Flush any remaining table
    if buffer_table:
        render_table(buffer_table)

    return pdf.output(dest="S").encode("latin-1")

# --- CARICAMENTO DATABASE ---
import os

# Funzione per ottenere il primo modello che supporta generateContent
@st.cache_data
def get_available_model():
    try:
        models = list(client.models.list())
        for model in models:
            actions = getattr(model, "supported_actions", [])
            if "generateContent" in actions:
                return model.name.split("/")[-1]
        # Fallback a un modello generico
        return "gemini-2.5-flash"
    except Exception as e:
        st.warning(f"Impossibile listare i modelli: {e}")
        return "gemini-2.5-flash"

@st.cache_data
def load_data():
    try:
        # Usa il percorso assoluto del file
        csv_path = os.path.join(os.path.dirname(__file__), "exercises_db.csv")
        return pd.read_csv(csv_path)
    except Exception as e:
        st.error(f"Errore nel caricamento del CSV: {e}")
        return pd.DataFrame()

df_exercises = load_data()

# --- INTERFACCIA UTENTE ---

# Indicatore mobile per aprire il menu (solo su mobile) - SOPRA IL TITOLO
st.markdown("""
<style>
    .mobile-hint {
        display: none;
    }
    
    @media (max-width: 768px) {
        .mobile-hint {
            display: flex;
            align-items: center;
            gap: 10px;
            background: linear-gradient(135deg, rgba(255,75,75,0.2) 0%, rgba(255,107,107,0.15) 100%);
            border: 2px solid #FF4B4B;
            border-radius: 12px;
            padding: 14px 18px;
            margin: 0 0 15px 0;
            animation: pulse-border 2s infinite;
        }
        
        .mobile-hint-arrow {
            font-size: 1.6rem;
            color: #FF4B4B;
            animation: bounce-left 1s infinite;
        }
        
        .mobile-hint-text {
            color: #FFFFFF;
            font-size: 0.95rem;
            font-weight: 500;
        }
        
        .mobile-hint-text strong {
            color: #FF6B6B;
            font-size: 1.1rem;
        }
        
        @keyframes bounce-left {
            0%, 100% { transform: translateX(0); }
            50% { transform: translateX(-5px); }
        }
        
        @keyframes pulse-border {
            0%, 100% { border-color: #FF4B4B; }
            50% { border-color: #FF8E53; }
        }
    }
</style>

<div class="mobile-hint">
    <span class="mobile-hint-arrow">↖️</span>
    <span class="mobile-hint-text">Tocca <strong>>></strong> in alto a sinistra per iniziare!</span>
</div>
""", unsafe_allow_html=True)

# Header professionale
st.markdown('<h1 class="main-header">🏋️ Hevy AI Architect</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Genera schede di allenamento personalizzate con l\'intelligenza artificiale</p>', unsafe_allow_html=True)

# Statistiche database
# (mobile hint già inserito sopra)
# Statistiche database
col_stat1, col_stat2, col_stat3 = st.columns(3)
with col_stat1:
    st.metric("💪 Esercizi", f"{len(df_exercises)}+")
with col_stat2:
    if not df_exercises.empty and 'muscle_group' in df_exercises.columns:
        st.metric("🎯 Gruppi Muscolari", len(df_exercises['muscle_group'].unique()))
    else:
        st.metric("🎯 Gruppi Muscolari", "N/A")
with col_stat3:
    st.metric("🤖 Modello AI", "Gemini Pro")

# Placeholder per lo spinner (apparirà SOPRA le foto)
spinner_placeholder = st.empty()

# Galleria immagini centrale con dissolvenza
import base64

def get_image_base64(image_path):
    """Converte un'immagine in base64 per embedding HTML."""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception:
        return None

photo_dir = os.path.join(os.path.dirname(__file__), "photo")
photo30_path = os.path.join(photo_dir, "photo30.jpg")
photo31_path = os.path.join(photo_dir, "photo31.jpg")

# Prova anche estensioni alternative
if not os.path.exists(photo30_path):
    photo30_path = os.path.join(photo_dir, "photo30.png")
if not os.path.exists(photo31_path):
    photo31_path = os.path.join(photo_dir, "photo31.png")

photo30_b64 = get_image_base64(photo30_path)
photo31_b64 = get_image_base64(photo31_path)

# Determina il tipo MIME in base all'estensione
ext30 = "png" if photo30_path.endswith(".png") else "jpeg"
ext31 = "png" if photo31_path.endswith(".png") else "jpeg"

# Mostra galleria grande solo se NON c'è una scheda generata
if photo30_b64 and photo31_b64 and not st.session_state.get("plan_md"):
    st.markdown(f'''
    <div class="gallery-container">
        <div class="gallery-image">
            <img src="data:image/{ext30};base64,{photo30_b64}" alt="Fitness Training">
        </div>
        <div class="gallery-image">
            <img src="data:image/{ext31};base64,{photo31_b64}" alt="Workout">
        </div>
    </div>
    ''', unsafe_allow_html=True)

st.markdown("---")

# Liste opzioni
GOALS_OPTIONS = ["Ipertrofia (Massa)", "Dimagrimento (Cutting)", "Forza Pura", "Miglioramento Posturale", "Tonificazione"]
SPLIT_OPTIONS = ["Full Body", "Alto/Basso", "Spinta/Tirata/Gambe", "Split per Gruppo Muscolare"]
EQUIPMENT_OPTIONS = ["Con attrezzi", "Senza attrezzi"]
SEX_OPTIONS = ["Maschio", "Femmina"]
LEVEL_OPTIONS = ["Principiante", "Esperto", "Super Esperto"]

# Traduzione gruppi muscolari inglese -> italiano
MUSCLE_TRANSLATION = {
    "Chest": "Petto",
    "Back": "Schiena",
    "Middle Back": "Dorsali",
    "Shoulders": "Spalle",
    "Biceps": "Bicipiti",
    "Triceps": "Tricipiti",
    "Legs": "Gambe",
    "Quadriceps": "Quadricipiti",
    "Hamstrings": "Femorali",
    "Glutes": "Glutei",
    "Calves": "Polpacci",
    "Abs": "Addominali",
    "Abdominals": "Addominali",
    "Core": "Core",
    "Forearms": "Avambracci",
    "Traps": "Trapezio",
    "Lats": "Dorsali",
    "Lower Back": "Lombari",
    "Full Body": "Tutto il Corpo",
    "Cardio": "Cardio",
    "Neck": "Collo",
    "Abductors": "Abduttori",
    "Adductors": "Adduttori",
    "Other": "Altro"
}

def translate_muscle(muscle):
    """Traduce il nome del gruppo muscolare in italiano."""
    return MUSCLE_TRANSLATION.get(muscle, muscle)

with st.sidebar:
    # Logo/Brand
    st.markdown("### 🏋️ Configura il tuo Allenamento")
    
    # Info box in alto
    with st.expander("ℹ️ Come funziona", expanded=False):
        st.markdown("""
        1. **Configura** i tuoi obiettivi e preferenze
        2. **Genera** la scheda con l'AI
        3. **Scarica** il PDF personalizzato
        
        L'AI analizza oltre 800 esercizi per creare 
        il programma perfetto per te!
        """)
    
    st.markdown("---")
    
    st.markdown("## 🎯 Obiettivi")
    
    # Filtra goals salvati che sono ancora validi
    default_goals = [g for g in saved_prefs.get("goals", []) if g in GOALS_OPTIONS]
    if not default_goals:
        default_goals = ["Ipertrofia (Massa)"]
    
    goals = st.multiselect(
        "Seleziona uno o più obiettivi",
        GOALS_OPTIONS,
        default=default_goals,
        help="Puoi selezionare più obiettivi contemporaneamente"
    )
    if not goals:
        goals = ["Equilibrato"]
    
    days = st.slider("📅 Giorni a settimana", 2, 6, saved_prefs.get("days", 4))
    
    split_idx = SPLIT_OPTIONS.index(saved_prefs.get("split_type", "Full Body")) if saved_prefs.get("split_type") in SPLIT_OPTIONS else 0
    split_type = st.selectbox("📋 Divisione lavoro giornaliero", SPLIT_OPTIONS, index=split_idx)
    
    st.markdown("---")
    st.markdown("## 👤 Profilo Personale")
    
    if not df_exercises.empty and 'muscle_group' in df_exercises.columns:
        muscle_options_raw = list(df_exercises['muscle_group'].unique())
        # Traduci i nomi dei muscoli in italiano
        muscle_options_translated = [translate_muscle(m) for m in muscle_options_raw]
        # Mappa italiano -> inglese per il filtro
        muscle_map_it_to_en = {translate_muscle(m): m for m in muscle_options_raw}
        default_focus = [translate_muscle(f) for f in saved_prefs.get("focus_area", []) if f in muscle_options_raw or translate_muscle(f) in muscle_options_translated]
        focus_area_it = st.multiselect("🎯 Focus Muscolare (Opzionale)", sorted(set(muscle_options_translated)), default=default_focus, help="Lascia vuoto per un allenamento bilanciato")
        # Riconverti in inglese per il prompt
        focus_area = [muscle_map_it_to_en.get(f, f) for f in focus_area_it]
    else:
        focus_area = []
        st.warning("Nessun dato disponibile per il filtro muscolare")
    
    # Due colonne per sesso e attrezzatura
    col1, col2 = st.columns(2)
    with col1:
        sex_idx = SEX_OPTIONS.index(saved_prefs.get("sex_pref", "Maschio")) if saved_prefs.get("sex_pref") in SEX_OPTIONS else 0
        sex_pref = st.selectbox("⚧ Sesso", SEX_OPTIONS, index=sex_idx)
    with col2:
        equip_idx = EQUIPMENT_OPTIONS.index(saved_prefs.get("equipment_pref", "Con attrezzi")) if saved_prefs.get("equipment_pref") in EQUIPMENT_OPTIONS else 0
        equipment_pref = st.selectbox("🏠 Attrezzi", EQUIPMENT_OPTIONS, index=equip_idx)
    
    age = st.slider("🎂 Età", 16, 80, saved_prefs.get("age", 30))
    
    # Mappa vecchi valori ai nuovi per retrocompatibilità
    old_level_map = {"Beginner": "Principiante", "Intermediate": "Esperto", "Pro": "Super Esperto"}
    saved_level = saved_prefs.get("training_level", "Principiante")
    if saved_level in old_level_map:
        saved_level = old_level_map[saved_level]
    level_idx = LEVEL_OPTIONS.index(saved_level) if saved_level in LEVEL_OPTIONS else 0
    training_level = st.selectbox("📊 Livello Esperienza", LEVEL_OPTIONS, index=level_idx)
    
    duration = st.slider("⏱️ Durata seduta (min)", 30, 90, saved_prefs.get("duration", 60))
    
    st.markdown("---")
    
    generate_btn = st.button("🚀 Genera Scheda AI", type="primary", use_container_width=True)

# Funzione per chiudere la sidebar via JavaScript
def collapse_sidebar():
    """Inietta JavaScript per chiudere la sidebar."""
    js = """
    <script>
        // Cerca il pulsante di chiusura sidebar e cliccalo
        var sidebar = window.parent.document.querySelector('[data-testid="stSidebar"]');
        if (sidebar) {
            sidebar.setAttribute('aria-expanded', 'false');
        }
        
        // Metodo alternativo: trova e clicca il pulsante collapse
        var collapseBtn = window.parent.document.querySelector('[data-testid="stSidebarCollapseButton"]');
        if (collapseBtn) {
            collapseBtn.click();
        }
        
        // Forza la chiusura aggiungendo classe CSS
        var sidebarContent = window.parent.document.querySelector('[data-testid="stSidebarContent"]');
        if (sidebarContent) {
            sidebarContent.closest('section').style.transform = 'translateX(-100%)';
        }
    </script>
    """
    components.html(js, height=0)

# --- LOGICA AI ---
if generate_btn:
    # Chiudi la sidebar per dare spazio ai risultati
    collapse_sidebar()
    
    # Salva le preferenze correnti
    current_prefs = {
        "goals": goals if goals != ["Equilibrato"] else ["Ipertrofia (Massa)"],
        "days": days,
        "split_type": split_type,
        "focus_area": focus_area,
        "equipment_pref": equipment_pref,
        "sex_pref": sex_pref,
        "age": age,
        "training_level": training_level,
        "duration": duration
    }
    save_preferences(current_prefs)
    
    if df_exercises.empty:
        st.error("Errore: Il file 'exercises_db.csv' non è stato trovato!")
    else:
        with spinner_placeholder:
            with st.spinner("L'IA sta analizzando la biomeccanica e costruendo il programma..."):
                
                # 1. Creiamo il contesto per l'IA (Prompt Engineering Avanzato)
                # Trasformiamo il dataframe in una stringa di testo per darlo in pasto all'IA
                exercises_list_str = df_exercises.to_string(index=False)
                
                prompt = f"""
            Agisci come un Coach Esperto di biomeccanica e fisiologia sportiva.
            Il tuo compito è creare una scheda di allenamento di {days} giorni a settimana.
            
            OBIETTIVI UTENTE: {", ".join(goals)}
            TIPO DI SPLIT: {split_type}
            DURATA MEDIA: {duration} minuti
            FOCUS MUSCOLARE RICHIESTO: {", ".join(focus_area) if focus_area else "Equilibrato"}
            ATTREZZATURA: {equipment_pref} (Con attrezzi → prediligi bilancieri, manubri, macchine; Senza attrezzi → prediligi corpo libero / elastici / varianti home)
            SESSO: {sex_pref} (seleziona varianti ed esercizi adeguati a comfort articolare e preferenze tipiche)
            ETA': {age} (adatta volume e intensità con progressioni adeguate all'età, cura mobilità e gestione carichi)
            LIVELLO: {training_level} (Principiante: esercizi facili e stabili; Esperto: esercizi intermedi con varianti controllate; Super Esperto: esercizi complessi, carichi più alti, maggior densità)
            
            VINCOLO FONDAMENTALE:
            Devi usare SOLO ed ESCLUSIVAMENTE gli esercizi presenti nel seguente database CSV. 
            Non inventare esercizi che non sono in questa lista.
            
            DATABASE ESERCIZI DISPONIBILI:
            {exercises_list_str}
            
            FORMATO OUTPUT RICHIESTO:
            Restituisci una risposta strutturata in Markdown.
            Per ogni Giorno (Giorno 1, Giorno 2...), elenca gli esercizi in una tabella con queste colonne:
            | Esercizio | Serie | Ripetizioni | Recupero | Note Tecniche |
            
            Logica da applicare:
            - Se l'obiettivo è Dimagrimento: Ripetizioni alte (12-15), recuperi brevi (60s).
            - Se l'obiettivo è Ipertrofia: Ripetizioni medie (8-12), recuperi medi (90s).
            - Se l'obiettivo è Forza: Ripetizioni basse (3-5), recuperi lunghi (120s+).
            - Includi note sulla postura o l'esecuzione corretta.

            Ordine fisiologicamente corretto degli esercizi per ogni giorno:
            1) Warm-up / attivazione specifica
            2) Multarticolari pesanti (bilanciere / macchina) su pattern principali del giorno
            3) Unilaterali / stabilità
            4) Complementari / isolamento mirato
            5) Core / finisher metabolico (facoltativo)

            Adatta la difficoltà in base al livello:
            - Beginner: versioni stabili (macchine / bilanciere guidato), range moderato di carico, tecnica semplice, progressioni lineari.
            - Intermediate: introduci varianti con maggiore ROM o instabilità controllata, gestione RIR 1-3, carichi moderati-alti.
            - Pro: esercizi complessi (bilanciere libero, varianti avanzate), superset opzionali, RIR 0-2 su esercizi principali.

            Adatta gli esercizi in base all'attrezzatura:
            - Con attrezzi: priorità a bilancieri, manubri, macchine; corpo libero solo come complemento.
            - Senza attrezzi: priorità a corpo libero, elastici, isometrie, varianti plyo controllate; evita macchine/pesi se non disponibili.

            Adatta in base al sesso:
            - Maschio: non serve modificare i carichi target, ma cura la progressione su pattern principali (spinta/tiro/gambe) senza trascurare mobilità.
            - Femmina: includi focus su catena posteriore e glutei se coerente con gli obiettivi, prediligi varianti che riducano stress articolare su spalle/lombare.

            Restituisci output conciso, solo Markdown.
                """
                
                try:
                    # 2. Chiamata all'IA - Usa il modello disponibile
                    model_to_use = get_available_model()
                    response = client.models.generate_content(
                        model=model_to_use,
                        contents=prompt
                    )
                    
                    # 3. Estrai il testo dalla risposta (gestisce diversi formati API)
                    result_text = None
                    if hasattr(response, 'text') and response.text:
                        result_text = response.text
                    elif hasattr(response, 'candidates') and response.candidates:
                        candidate = response.candidates[0]
                        if hasattr(candidate, 'content') and candidate.content:
                            if hasattr(candidate.content, 'parts') and candidate.content.parts:
                                result_text = candidate.content.parts[0].text
                    
                    if result_text:
                        st.success("✅ Scheda generata con successo!")
                        
                        # Card risultato
                        st.markdown('<div class="result-card">', unsafe_allow_html=True)
                        st.markdown(result_text)
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        # salva per esportazione
                        st.session_state["plan_md"] = result_text
                    else:
                        st.error("❌ La risposta dell'AI è vuota. Riprova.")
                        st.write("Debug response:", response)
                    
                except Exception as e:
                    st.error(f"❌ Errore durante la generazione: {e}")

# --- ESPORTAZIONE PDF ---
if st.session_state.get("plan_md"):
    # Mostra la scheda generata
    st.markdown("---")
    st.markdown("## 📋 La Tua Scheda di Allenamento")
    st.markdown('<div class="result-card">', unsafe_allow_html=True)
    st.markdown(st.session_state["plan_md"])
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Pulsante download PDF
    st.markdown("---")
    col_pdf1, col_pdf2, col_pdf3 = st.columns([1, 2, 1])
    with col_pdf2:
        pdf_bytes = build_pdf_from_markdown(st.session_state["plan_md"])
        if pdf_bytes:
            st.download_button(
                "📥 Scarica Scheda PDF",
                data=pdf_bytes,
                file_name="scheda_allenamento.pdf",
                mime="application/pdf",
                use_container_width=True
            )
    
    # Galleria immagini spostata a piè pagina con animazione
    if photo30_b64 and photo31_b64:
        st.markdown(f'''
        <div class="gallery-footer">
            <div class="gallery-image">
                <img src="data:image/{ext30};base64,{photo30_b64}" alt="Fitness Training">
            </div>
            <div class="gallery-image">
                <img src="data:image/{ext31};base64,{photo31_b64}" alt="Workout">
            </div>
        </div>
        ''', unsafe_allow_html=True)

# --- VISUALIZZAZIONE DATABASE (Opzionale) ---
with st.expander("📚 Vedi Database Esercizi"):
    st.dataframe(df_exercises, use_container_width=True)

# --- FOOTER ---
st.markdown("---")
st.markdown("""
<div class="footer">
    <p>🏋️ <strong>Hevy AI Architect</strong> • Powered by Google Gemini AI</p>
    <p>Creato con ❤️ da Stefano Pisani</p>
</div>
""", unsafe_allow_html=True)