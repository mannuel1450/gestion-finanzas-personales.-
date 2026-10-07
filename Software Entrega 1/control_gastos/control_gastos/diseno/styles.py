"""Estilos visuales (CSS) de la app."""
import streamlit as st


# UI: todos los estilos visuales (colores, vidrio, botones, tarjetas...).
# Para cambiar la paleta, edita las variables dentro de ':root'.
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

:root {
    --texto: #F2F6FA;
    --muted: rgba(242,246,250,0.68);
    --menta: #5EEAD4;
    --menta-osc: #14B8A6;
    --ambar: #F2A83B;
    --coral: #FF6B57;
    --vidrio: rgba(255,255,255,0.08);
    --vidrio-fuerte: rgba(255,255,255,0.14);
    --borde: rgba(255,255,255,0.18);
}

html, body, .stApp {
    font-family: 'Plus Jakarta Sans', system-ui, sans-serif;
    color: var(--texto);
}

/* ---------- Fondo con destellos de color ---------- */
.stApp {
    background:
        radial-gradient(900px 600px at 8% 0%, rgba(94,234,212,0.28), transparent 60%),
        radial-gradient(800px 600px at 95% 15%, rgba(139,92,246,0.30), transparent 60%),
        radial-gradient(900px 700px at 60% 100%, rgba(242,168,59,0.18), transparent 60%),
        #0B1220;
    background-attachment: fixed;
}

#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }

.block-container { padding-top: 2rem; padding-bottom: 4rem; max-width: 1180px; }

/* ---------- Texto: siempre legible sobre el vidrio ---------- */
.stApp h1, .stApp h2, .stApp h3, .stApp h4,
.stApp p, .stApp label, .stApp li, .stApp span,
.stApp [data-testid="stMarkdownContainer"],
.stApp [data-testid="stWidgetLabel"] p {
    color: var(--texto);
}
h1, h2, h3 { letter-spacing: -0.02em; }

/* ---------- Efecto vidrio (contenedores) ---------- */
[class*="st-key-glass"] {
    background: var(--vidrio);
    backdrop-filter: blur(18px) saturate(140%);
    -webkit-backdrop-filter: blur(18px) saturate(140%);
    border: 1px solid var(--borde);
    border-radius: 22px;
    padding: 20px 22px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.28), inset 0 1px 0 rgba(255,255,255,0.15);
}

/* ---------- Sidebar ---------- */
section[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(22px);
    -webkit-backdrop-filter: blur(22px);
    border-right: 1px solid var(--borde);
}
section[data-testid="stSidebar"] * { color: var(--texto); }

.perfil {
    display: flex; align-items: center; gap: 12px;
    padding: 14px; margin: 6px 0 18px 0;
    background: var(--vidrio);
    border: 1px solid var(--borde);
    border-radius: 16px;
}
.perfil .avatar {
    width: 42px; height: 42px; border-radius: 50%;
    background: linear-gradient(135deg, var(--menta), var(--menta-osc));
    display: flex; align-items: center; justify-content: center;
    font-weight: 800; font-size: 1.1rem;
    color: #06231F !important;
}
.perfil .nombre { font-weight: 700; font-size: 1rem; line-height: 1.1; }
.perfil .rol { font-size: 0.75rem; color: var(--muted) !important; }

/* ---------- Encabezado ---------- */
.hero {
    background: var(--vidrio-fuerte);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid var(--borde);
    border-radius: 26px;
    padding: 30px 34px;
    margin-bottom: 22px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 10px 40px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.2);
}
.hero::after {
    content: "";
    position: absolute; right: -50px; top: -70px;
    width: 240px; height: 240px; border-radius: 50%;
    background: radial-gradient(circle, rgba(242,168,59,0.55), transparent 70%);
}
.hero h1 { margin: 0 0 4px 0; font-size: 1.9rem; font-weight: 800; color: var(--texto); }
.hero p { margin: 0; color: var(--muted); font-size: 0.98rem; }

/* ---------- Tarjetas de métricas ---------- */
.kpi {
    background: var(--vidrio);
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    border: 1px solid var(--borde);
    border-radius: 20px;
    padding: 20px 22px;
    height: 100%;
    box-shadow: 0 8px 28px rgba(0,0,0,0.25), inset 0 1px 0 rgba(255,255,255,0.15);
}
.kpi .etiqueta { font-size: 0.82rem; color: var(--muted); font-weight: 600; }
.kpi .valor { font-size: 1.85rem; font-weight: 800; letter-spacing: -0.03em; margin-top: 4px; color: var(--texto); }
.kpi.destacada {
    background: linear-gradient(135deg, rgba(94,234,212,0.32), rgba(20,184,166,0.12));
    border-color: rgba(94,234,212,0.5);
}
.kpi.destacada .valor { color: var(--menta); }

/* ---------- Títulos de sección ---------- */
.titulo-seccion { font-size: 1.15rem; font-weight: 800; margin: 6px 0 4px 0; color: var(--texto); }
.sub-seccion { color: var(--muted); font-size: 0.9rem; margin-bottom: 14px; }

/* ---------- Pestañas ---------- */
.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    background: var(--vidrio);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    padding: 6px;
    border-radius: 16px;
    border: 1px solid var(--borde);
}
.stTabs [data-baseweb="tab"] {
    height: 44px; border-radius: 11px; padding: 0 18px;
    font-weight: 600; background: transparent;
}
.stTabs [data-baseweb="tab"] p { color: var(--muted); }
.stTabs [aria-selected="true"] { background: rgba(94,234,212,0.18) !important; }
.stTabs [aria-selected="true"] p { color: var(--menta) !important; }
.stTabs [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-border"] { display: none; }

/* ---------- Campos ---------- */
.stTextInput input,
.stNumberInput input,
.stDateInput input,
.stSelectbox div[data-baseweb="select"] > div,
.stNumberInput div[data-baseweb="input"],
.stDateInput div[data-baseweb="input"],
.stTextInput div[data-baseweb="input"] {
    background: rgba(255,255,255,0.07) !important;
    color: var(--texto) !important;
    -webkit-text-fill-color: var(--texto) !important;
    border-radius: 12px !important;
    border: 1px solid var(--borde) !important;
}
.stSelectbox div[data-baseweb="select"] * { color: var(--texto) !important; }
.stTextInput input::placeholder { color: rgba(242,246,250,0.45) !important; -webkit-text-fill-color: rgba(242,246,250,0.45) !important; }
.stTextInput input:focus, .stNumberInput input:focus, .stDateInput input:focus {
    border-color: var(--menta) !important;
    box-shadow: 0 0 0 3px rgba(94,234,212,0.22) !important;
}
.stNumberInput button { background: rgba(255,255,255,0.08) !important; color: var(--texto) !important; border: none !important; }
.stCheckbox span, .stRadio label, .stRadio p { color: var(--texto) !important; }

/* ---------- Botones ---------- */
.stButton > button, .stDownloadButton > button {
    border-radius: 12px;
    font-weight: 700;
    padding: 0.6rem 1.3rem;
    border: 1px solid rgba(94,234,212,0.6);
    background: linear-gradient(135deg, var(--menta), var(--menta-osc));
    transition: transform .12s ease, box-shadow .12s ease;
}
.stButton > button p, .stDownloadButton > button p,
.stButton > button span, .stDownloadButton > button span { color: #06231F !important; font-weight: 700; }
.stButton > button:hover, .stDownloadButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 8px 24px rgba(94,234,212,0.35);
    border-color: var(--menta);
}
.stButton > button:focus-visible { outline: 3px solid var(--ambar); }

section[data-testid="stSidebar"] .stButton > button {
    background: var(--vidrio-fuerte);
    border: 1px solid var(--borde);
}
section[data-testid="stSidebar"] .stButton > button p { color: var(--texto) !important; }

/* ---------- Tabla ---------- */
div[data-testid="stDataFrame"] {
    border: 1px solid var(--borde);
    border-radius: 16px;
    overflow: hidden;
}

/* ---------- Menús desplegables y calendario (siempre oscuros) ---------- */
div[data-baseweb="popover"] > div,
div[data-baseweb="popover"] ul,
div[data-baseweb="calendar"] {
    background: #16203A !important;
    color: var(--texto) !important;
}
div[data-baseweb="popover"] li,
div[data-baseweb="popover"] li * ,
div[data-baseweb="calendar"] *,
div[data-baseweb="popover"] [role="option"] { color: var(--texto) !important; }
div[data-baseweb="popover"] li:hover,
div[data-baseweb="popover"] [aria-selected="true"] { background: rgba(94,234,212,0.18) !important; }
div[data-baseweb="calendar"] [aria-selected="true"] { background: var(--menta-osc) !important; }
div[data-baseweb="calendar"] [aria-selected="true"] * { color: #06231F !important; }

/* ---------- Barra superior de Streamlit ---------- */
[data-testid="stToolbar"], [data-testid="stToolbar"] *,
[data-testid="stSidebarCollapseButton"] * { color: var(--texto) !important; }

/* ---------- Alertas ---------- */
div[data-testid="stAlert"] {
    background: rgba(255,255,255,0.10) !important;
    border-radius: 16px;
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border: 1px solid var(--borde);
    border-left: 5px solid var(--menta);
}
div[data-testid="stAlert"] * { color: var(--texto) !important; }
div[data-testid="stAlert"]:has([data-testid="stAlertContentSuccess"]) { border-left-color: var(--menta); }
div[data-testid="stAlert"]:has([data-testid="stAlertContentWarning"]) { border-left-color: var(--ambar); }
div[data-testid="stAlert"]:has([data-testid="stAlertContentError"]) { border-left-color: var(--coral); }
div[data-testid="stAlert"]:has([data-testid="stAlertContentInfo"]) { border-left-color: #7DB7FF; }

/* ---------- Barra de presupuesto ---------- */
.barra-fondo { background: rgba(255,255,255,0.12); border-radius: 999px; height: 14px; overflow: hidden; }
.barra-relleno { height: 100%; border-radius: 999px; }
.barra-datos {
    display: flex; justify-content: space-between;
    font-size: 0.85rem; color: var(--muted); margin-top: 8px; font-weight: 600;
}

/* ---------- Logros ---------- */
.logro {
    border-radius: 20px; padding: 18px; height: 100%;
    background: var(--vidrio);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid var(--borde);
}
.logro .sello {
    width: 46px; height: 46px; border-radius: 14px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.4rem; margin-bottom: 12px;
    background: rgba(255,255,255,0.10);
}
.logro .nombre { font-weight: 800; font-size: 1rem; color: var(--texto); }
.logro .desc { color: var(--muted); font-size: 0.85rem; margin-top: 4px; }
.logro .estado { font-size: 0.78rem; font-weight: 700; margin-top: 10px; }
.logro.ganado {
    background: linear-gradient(160deg, rgba(242,168,59,0.28), rgba(255,255,255,0.06));
    border-color: rgba(242,168,59,0.7);
    box-shadow: 0 0 28px rgba(242,168,59,0.25);
}
.logro.ganado .sello { background: var(--ambar); }
.logro.ganado .estado { color: var(--ambar); }
.logro.bloqueado { opacity: 0.6; }
.logro.bloqueado .sello { filter: grayscale(1); }
.logro.bloqueado .estado { color: var(--muted); }

/* ---------- Login ---------- */
.login-marca { text-align: center; margin: 4vh 0 18px 0; }
.login-marca .logo {
    width: 68px; height: 68px; border-radius: 22px; margin: 0 auto 12px auto;
    background: var(--vidrio-fuerte);
    border: 1px solid var(--borde);
    backdrop-filter: blur(16px);
    display: flex; align-items: center; justify-content: center; font-size: 2rem;
    box-shadow: 0 10px 30px rgba(94,234,212,0.25);
}
.login-marca h1 { font-size: 1.8rem; font-weight: 800; margin: 0; color: var(--texto); }
.login-marca p { color: var(--muted); margin: 6px 0 0 0; }

@media (prefers-reduced-motion: reduce) { * { transition: none !important; } }
</style>
"""


# UI: inyecta el CSS de arriba en la página.
def aplicar_estilos() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
