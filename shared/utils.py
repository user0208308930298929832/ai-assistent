import os, json, base64, uuid, time, random
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components
from openai import OpenAI

# -------------------- PATHS --------------------
BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "history"
DATA.mkdir(exist_ok=True)
USERS_PATH = os.path.join(BASE, "starter", "users.json")

# -------------------- CSS GLOBAL --------------------
def inject_css():
    st.markdown("""
    <style>
    html, body, [class*="block-container"] {
        background-color: #f7f9fb !important;
        color: #1a1d24;
        font-family: 'Inter', system-ui, sans-serif;
    }
    .app-container {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100vh;
        padding: 0;
        margin: 0;
    }
    .card {
        background: #ffffff;
        border: 1px solid #e1e4e8;
        border-radius: 12px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.06);
        padding: 32px;
        width: 380px;
        text-align: center;
        transition: all 0.2s ease;
    }
    .card:hover { box-shadow: 0 6px 20px rgba(0,0,0,0.08); }

    h1, h2, h3 {
        color: #0044ff;
        font-weight: 700;
        margin-bottom: 6px;
    }
    p {
        color: #5b6573;
        font-size: 14px;
        margin-bottom: 22px;
    }

    input[type="text"], input[type="password"] {
        width: 100%;
        border: 1px solid #d1d5db;
        border-radius: 10px;
        padding: 10px 14px;
        margin: 8px 0 14px 0;
        font-size: 15px;
        background-color: #fafbfc;
    }

    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg,#0044ff,#007bff);
        color: white;
        border: none;
        padding: 10px 0;
        border-radius: 10px;
        font-weight: 600;
        font-size: 15px;
        cursor: pointer;
        transition: 0.2s ease-in-out;
    }
    .stButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,85,255,0.3);
    }
    </style>
    """, unsafe_allow_html=True)

# -------------------- LOGIN CARD --------------------
def load_users():
    try:
        with open(USERS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def login_card(title="AI Social Automator"):
    inject_css()
    st.markdown('<div class="app-container"><div class="card">', unsafe_allow_html=True)
    st.markdown(f"<h2>{title}</h2>", unsafe_allow_html=True)
    st.markdown("<p>Entra na tua conta para continuar</p>", unsafe_allow_html=True)

    u = st.text_input("Utilizador", placeholder="O teu nome de utilizador")
    p = st.text_input("Palavra-passe", type="password", placeholder="••••••••")
    users = load_users()

    if st.button("Entrar"):
        if u in users and users[u].get("password") == p:
            st.session_state["logged_in"] = True
            st.session_state["username"] = u
            st.success("Bem-vindo 👋")
            time.sleep(0.5)
            st.rerun()
        else:
            st.error("Credenciais incorretas.")

    st.markdown("</div></div>", unsafe_allow_html=True)

# -------------------- LOGOUT PILL --------------------
def logout_pill():
    with st.sidebar:
        st.markdown(f"**👋 Logado como {st.session_state.get('username','')}**")
        if st.button("Terminar sessão"):
            for k in ["logged_in","username"]:
                st.session_state.pop(k, None)
            st.rerun()

# -------------------- CLIENT OPENAI --------------------
def get_client():
    api = os.getenv("OPENAI_API_KEY")
    if not api:
        st.warning("⚠️ Adiciona a tua chave em Settings → Secrets → OPENAI_API_KEY")
        st.stop()
    return OpenAI(api_key=api)
# ============================================================
# Função engagement_and_time (placeholder funcional)
# ============================================================
def engagement_and_time(prompt: str) -> dict:
    """
    Gera dados fictícios de engagement e hora ideal de publicação.
    (Pode ser adaptado para cálculo real com IA futuramente)
    """
    import random, datetime
    best_hour = random.choice(["09:00", "12:30", "18:45", "21:00"])
    engagement_score = random.randint(60, 98)
    return {
        "prompt": prompt,
        "best_hour": best_hour,
        "engagement_score": engagement_score
    }
