import streamlit as st
import json
import hashlib
import os, time
from openai import OpenAI

# --- Função auxiliar ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# --- LOGIN ---
def login():
    st.set_page_config(
        page_title="AI Social Automator — Starter",
        layout="centered",
        initial_sidebar_state="collapsed"
    )

    st.markdown("""
        <style>
        [data-testid="stSidebar"] { display: none; }
        header { visibility: hidden; }
        .block-container { padding-top: 3rem; }

        body, .stApp {
            background: linear-gradient(135deg, #1f1f1f 0%, #2a2a2a 100%) !important;
            color: white !important;
            font-family: 'Inter', sans-serif;
        }
        .fade-in {
            animation: fadeIn 1s ease-in;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .login-box {
            background-color: #fff;
            border-radius: 20px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.3);
            padding: 2.5rem 3rem;
            text-align: center;
            color: #333;
            max-width: 400px;
            width: 100%;
            margin: auto;
        }
        .login-title {
            font-size: 1.8rem;
            font-weight: 700;
            color: #ff7b00;
            margin-top: 1rem;
        }
        .subtitle {
            color: #777;
            font-size: 0.9rem;
            margin-bottom: 1.5rem;
        }
        </style>
    """, unsafe_allow_html=True)

    # Lê utilizadores
    users = load_users()

    # Layout central
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        st.markdown('<div class="fade-in login-box">', unsafe_allow_html=True)
        st.image("https://cdn-icons-png.flaticon.com/512/4712/4712109.png", width=80)
        st.markdown('<div class="login-title">AI Social Automator</div>', unsafe_allow_html=True)
        st.markdown('<p class="subtitle">Acede ao teu assistente de IA personalizado 🤖</p>', unsafe_allow_html=True)

        with st.form("login_form"):
            username = st.text_input("👤 Utilizador")
            password = st.text_input("🔑 Palavra-passe", type="password")
            submit = st.form_submit_button("Entrar", use_container_width=True)

        if submit:
            if username in users and users[username].get("password") == password:
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.session_state["plan"] = users[username].get("plan", "starter")
                st.success(f"Bem-vindo, {username.capitalize()} 👋")
                time.sleep(1)
                st.rerun()
            else:
                st.error("❌ Utilizador ou palavra-passe incorretos.")

        st.markdown("</div>", unsafe_allow_html=True)

# --- LOGOUT ---
def logout():
    if st.button("🚪 Sair"):
        for key in ["logged_in", "username", "plan"]:
            st.session_state.pop(key, None)
        st.rerun()

# --- SISTEMA DE LOGIN ---
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    login()
    st.stop()

# --- CONTEÚDO PRINCIPAL (Starter) ---
st.title("🤖 AI Social Automator — Starter")
st.caption("Cria legendas e hashtags em segundos com IA 🚀")

logout()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.warning("⚠️ Adiciona a tua chave API do OpenAI em Settings → Secrets.")
    st.stop()

client = OpenAI(api_key=api_key)

tema = st.text_area("✍️ Escreve o tema do post:", placeholder="Ex.: Novo casaco de outono, foco em elegância e conforto.")

st.markdown("🎯 Ajuste de tom disponível a partir do **plano PRO**  🔒")
nicho = st.selectbox("📌 Nicho", ["Geral", "Moda", "Fitness", "Restaurantes", "Beleza", "Tecnologia"])

if st.button("⚡ Gerar Conteúdo", use_container_width=True):
    if not tema.strip():
        st.warning("Escreve o tema primeiro!")
    else:
        with st.spinner("A criar o teu conteúdo..."):
            prompt = f"Cria uma legenda curta e criativa em PT-PT sobre: {tema}. Nicho: {nicho}. Inclui 3 hashtags no fim."
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            )
            texto = response.choices[0].message.content
        st.subheader("🧠 Resultado")
        st.write(texto)
        st.success("Feito! 🎉")

st.caption("Plano Starter · Modelo: GPT-4o-mini · © 2025 AI Social Automator")
