"""Utilitários de UI — estilos e helpers reutilizáveis para o Ponte Nexus."""
import streamlit as st


# Paleta dark mode
DARK_BG         = "#0A192F"
DARK_CARD       = "#112240"
DARK_BORDER     = "#1E3A5F"
DARK_TEXT       = "#CCD6F6"
DARK_MUTED      = "#8892B0"
ACCENT_TEAL     = "#64FFDA"
ACCENT_TEAL_DIM = "#3FC8A8"

# Paleta light mode
LIGHT_BG        = "#FFFFFF"
LIGHT_CARD      = "#F8FAFC"
LIGHT_BORDER    = "#E2E8F0"
LIGHT_TEXT      = "#0A192F"
LIGHT_MUTED     = "#64748B"
ACCENT_PETROL   = "#0D7A7A"

# Paleta de tipos de transação
TYPE_COLORS: dict[str, str] = {
    "receita":             "#64FFDA",
    "despesa":             "#FF6B6B",
    "pro_labore":          "#4FC3F7",
    "dividendos":          "#81C784",
    "aporte_pf_pj":        "#FFB74D",
    "emprestimo_pf_pj":    "#CE93D8",
    "transferencia_pf_pj": "#FFF176",
    "transferencia_pj_pf": "#80DEEA",
}

# Mapa legível para exibição
TIPO_LABEL: dict[str, str] = {
    "receita":             "Receita",
    "despesa":             "Despesa",
    "pro_labore":          "Pró-Labore",
    "dividendos":          "Dividendos",
    "aporte_pf_pj":        "Aporte PF→PJ",
    "emprestimo_pf_pj":    "Empréstimo PF→PJ",
    "transferencia_pf_pj": "Transferência PF→PJ",
    "transferencia_pj_pf": "Transferência PJ→PF",
}


# â”€â”€â”€ CSS base (dark mode fintech) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
_CSS_BASE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
}
.main .block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
    max-width: 1400px;
}
h1 {
    font-size: 1.75rem !important;
    font-weight: 700 !important;
    color: #CCD6F6 !important;
    letter-spacing: -0.02em;
    margin-bottom: 0.1rem !important;
}
h2, h3 {
    font-weight: 600 !important;
    color: #CCD6F6 !important;
    letter-spacing: -0.01em;
}
.stCaption, [data-testid="stCaptionContainer"] p {
    color: #8892B0 !important;
    font-size: 0.82rem !important;
    letter-spacing: 0.01em;
}
[data-testid="stMetric"] {
    background: #112240;
    border: 1px solid #1E3A5F;
    border-radius: 12px;
    padding: 1.1rem 1.3rem !important;
    transition: border-color 0.2s ease;
}
[data-testid="stMetric"]:hover { border-color: #64FFDA55; }
[data-testid="stMetricLabel"] p {
    font-size: 0.72rem !important;
    font-weight: 500 !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #8892B0 !important;
}
[data-testid="stMetricValue"] {
    font-size: 1.6rem !important;
    font-weight: 700 !important;
    color: #CCD6F6 !important;
}
[data-testid="stMetricDelta"] { font-size: 0.78rem !important; font-weight: 500 !important; }
hr { border-color: #1E3A5F !important; margin: 1.2rem 0 !important; }
[data-testid="stDataFrame"] {
    border: 1px solid #1E3A5F !important;
    border-radius: 10px;
    overflow: hidden;
}
[data-testid="stSidebar"] {
    background-color: #0D1B2E !important;
    border-right: 1px solid #1E3A5F;
}
[data-testid="stSidebar"] .stMarkdown p { color: #8892B0 !important; font-size: 0.78rem; }
.js-plotly-plot .plotly .main-svg { border-radius: 10px; }
.stButton button[kind="primary"] {
    background: #64FFDA !important;
    color: #0A192F !important;
    font-weight: 600 !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.45rem 1.4rem !important;
    transition: opacity 0.2s;
}
.stButton button[kind="primary"]:hover { opacity: 0.88; }
[data-testid="stSelectbox"] > div,
[data-testid="stMultiSelect"] > div,
[data-testid="stDateInput"] > div {
    border-color: #1E3A5F !important;
    background: #112240 !important;
    border-radius: 8px !important;
}
.stAlert { border-radius: 10px !important; border-left-width: 3px !important; }
.stSpinner > div { border-top-color: #64FFDA !important; }
.nx-section-label {
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #64FFDA;
    margin-bottom: 0.6rem;
    display: block;
}
.nx-kpi-accent {
    width: 32px;
    height: 3px;
    background: #64FFDA;
    border-radius: 2px;
    margin-bottom: 0.5rem;
}
</style>
"""

# â”€â”€â”€ Overrides para light mode (Cinza Gelo / Marinho / Azul Petróleo) â”€â”€â”€â”€â”€â”€â”€â”€â”€
_CSS_LIGHT_OVERRIDES = """
<style>
.stApp, .main, section.main, [data-testid="stAppViewContainer"] {
    background-color: #FFFFFF !important;
}
[data-testid="stSidebar"] {
    background-color: #F8FAFC !important;
    border-right: 1px solid #E2E8F0 !important;
}
[data-testid="stSidebar"] .stMarkdown p { color: #64748B !important; }
h1 { color: #0A192F !important; }
h2, h3 { color: #0A192F !important; }
p, li { color: #0A192F; }
.stCaption, [data-testid="stCaptionContainer"] p { color: #64748B !important; }
[data-testid="stMetric"] {
    background: #F8FAFC !important;
    border-color: #E2E8F0 !important;
}
[data-testid="stMetricLabel"] p { color: #64748B !important; }
[data-testid="stMetricValue"] { color: #0A192F !important; }
hr { border-color: #E2E8F0 !important; }
[data-testid="stDataFrame"] { border-color: #E2E8F0 !important; }
[data-testid="stSelectbox"] > div,
[data-testid="stMultiSelect"] > div,
[data-testid="stDateInput"] > div {
    border-color: #E2E8F0 !important;
    background: #F8FAFC !important;
}
.nx-section-label { color: #0D7A7A !important; }
.nx-kpi-accent { background: #0D7A7A !important; }
.stButton button[kind="primary"] {
    background: #0D7A7A !important;
    color: #FFFFFF !important;
}
.stSpinner > div { border-top-color: #0D7A7A !important; }
</style>
"""


def theme_selector() -> bool:
    """Renderiza o toggle de tema na sidebar. Retorna True para dark mode."""
    with st.sidebar:
        st.markdown(
            '<p style="font-size:0.68rem;font-weight:600;letter-spacing:0.1em;'
            'text-transform:uppercase;margin:0.8rem 0 0.3rem;opacity:0.55">Aparência</p>',
            unsafe_allow_html=True,
        )
        is_dark: bool = st.toggle(
            "Dark Mode",
            value=st.session_state.get("dark_mode", True),
            key="_nx_dark_mode",
        )
        st.session_state["dark_mode"] = is_dark
    return is_dark


def apply_theme(is_dark: bool = True) -> None:
    """Injeta o CSS fintech (dark + overrides light se necessário)."""
    st.markdown(_CSS_BASE, unsafe_allow_html=True)
    if not is_dark:
        st.markdown(_CSS_LIGHT_OVERRIDES, unsafe_allow_html=True)


def plotly_layout(is_dark: bool = True) -> dict:
    """Retorna o dict de layout Plotly adequado ao tema atual."""
    if is_dark:
        return {
            "paper_bgcolor": "rgba(0,0,0,0)",
            "plot_bgcolor":  "rgba(0,0,0,0)",
            "font":          {"color": "#CCD6F6", "family": "Plus Jakarta Sans"},
            "margin":        {"t": 16, "b": 16, "l": 16, "r": 16},
            "xaxis":         {"gridcolor": "#1E3A5F", "linecolor": "#1E3A5F"},
            "yaxis":         {"gridcolor": "#1E3A5F", "linecolor": "#1E3A5F"},
        }
    return {
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor":  "rgba(0,0,0,0)",
        "font":          {"color": "#0A192F", "family": "Plus Jakarta Sans"},
        "margin":        {"t": 16, "b": 16, "l": 16, "r": 16},
        "xaxis":         {"gridcolor": "#E2E8F0", "linecolor": "#E2E8F0"},
        "yaxis":         {"gridcolor": "#E2E8F0", "linecolor": "#E2E8F0"},
    }


def page_header(title: str, subtitle: str = "") -> bool:
    """Renderiza cabeçalho padronizado + aplica tema. Retorna is_dark."""
    is_dark = theme_selector()
    apply_theme(is_dark)
    st.markdown('<div class="nx-kpi-accent"></div>', unsafe_allow_html=True)
    st.title(title)
    if subtitle:
        st.caption(subtitle)
    return is_dark
