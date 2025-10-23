import os, json, random, datetime
import streamlit as st
from pathlib import Path

# ===================== Caminhos =====================
BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "history"
DATA.mkdir(exist_ok=True)
USERS_PATH = BASE / "users.json"


# ===================== Estilo global (tema branco clean) =====================
def inject_css():
    st.markdown("""
    <style>
        body { background-color: #f9fafb; color: #111827; font-family: 'Inter', sans-serif; }
        .block-container { max-width: 700px; margin: auto; padding: 2rem; }
        .stTextInput>div>div>input {
            border-radius: 10px;
            border: 1px solid #d1d5db;
            padding: 10px;
        }
        .stButton>button {
            background: linear-gradient(90deg,#007aff,#00c6ff);
            border: none;
            border-radius: 10px;
            color: white;
            font-weight: 600;
            padding: 10px 20px;
            transition: 0.3s;
        }
        .stButton>button:hover {
            transform: scale(1.02);
            box-shadow: 0 0 10px rgba(0,122,255,0.3);
        }
    </style>
    """, unsafe_allow_html=True)


# ===================== Gestão de utilizadores =====================
def load_users():
    if not USERS_PATH.exists():
        return {}
    with open(USERS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_users(users):
    with open(USERS_PATH, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4)


# ===================== Autenticação =====================
def login_card(app_name="AI Automator"):
    st.title(app_name)
    username = st.text_input("Utilizador")
    password = st.text_input("Palavra-passe", type="password")
    if st.button("Entrar"):
        users = load_users()
        if username in users and users[username] == password:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.rerun()
        else:
            st.error("Credenciais inválidas.")


def logout_pill():
    if st.session_state.get("logged_in"):
        if st.button("🔒 Terminar sessão"):
            st.session_state.clear()
            st.experimental_rerun()


# ===================== Funções auxiliares =====================
def get_client():
    return st.session_state.get("username", "anónimo")


def engagement_and_time(prompt: str) -> dict:
    """Simula cálculo de melhor hora e score."""
    best_hour = random.choice(["08:00", "12:00", "18:00", "21:00"])
    engagement_score = random.randint(60, 99)
    return {"best_hour": best_hour, "engagement_score": engagement_score}


def add_history(username: str, prompt: str, result: str):
    """Guarda histórico local de prompts e respostas."""
    file = DATA / f"{username}.json"
    history = []
    if file.exists():
        with open(file, "r", encoding="utf-8") as f:
            history = json.load(f)
    entry = {"timestamp": str(datetime.datetime.now()), "prompt": prompt, "result": result}
    history.append(entry)
    with open(file, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4)


def get_history(username: str):
    """Obtém histórico do utilizador."""
    file = DATA / f"{username}.json"
    if not file.exists():
        return []
    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)


def copy_button(text: str):
    """Botão para copiar texto para clipboard."""
    st.code(text)
    st.button("📋 Copiar texto", on_click=lambda: st.session_state.update({"copied": text}))
