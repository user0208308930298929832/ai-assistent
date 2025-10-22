import streamlit as st
import json
import hashlib

# --- Funções de apoio ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    import os
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def login():
    import os
    import json

    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(135deg, #1c1c1c 0%, #2c2c2c 100%);
        }
        .login-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 90vh;
        }
        .login-box {
            background: #fff;
            padding: 3rem 4rem;
            border-radius: 20px;
            box-shadow: 0 6px 25px rgba(0,0,0,0.3);
            max-width: 400px;
            width: 90%;
            text-align: center;
            color: #333;
        }
        .login-title {
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 1rem;
            color: #ff7b00;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # --- Load users
    path = os.path.join(os.path.dirname(__file__), "users.json")
    with open(path, "r") as f:
        users = json.load(f)

    # --- Central login box
    st.markdown('<div class="login-container"><div class="login-box">', unsafe_allow_html=True)
    st.markdown('<div class="login-title">🔐 Login</div>', unsafe_allow_html=True)

    username = st.text_input("👤 Utilizador")
    password = st.text_input("🔑 Palavra-passe", type="password")

    if st.button("Entrar", use_container_width=True):
        if username in users and users[username]["password"] == password:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.session_state["plan"] = users[username].get("plan", "starter")
            st.success(f"Bem-vindo, {username.capitalize()} 👋")
            st.rerun()
        else:
            st.error("Utilizador ou palavra-passe incorretos ❌")

    st.markdown("</div></div>", unsafe_allow_html=True)

    if st.sidebar.button("Entrar"):
        if username in users and users[username]["password"] == password:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.session_state["plan"] = users[username]["plan"]
            st.sidebar.success(f"Bem-vindo, {username}!")
            st.rerun()
        else:
            st.sidebar.error("❌ Credenciais incorretas.")

def logout():
    if st.sidebar.button("🚪 Sair"):
        for key in ["logged_in", "username", "plan"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

# --- Verificação de login ---
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    login()
    st.stop()
else:
    logout()
import streamlit as st
from openai import OpenAI
import os

st.set_page_config(page_title="AI Social Automator - Starter", page_icon="🤖")

st.title("🤖 AI Social Automator — Starter")
st.caption("Cria legendas e hashtags em segundos com IA 🚀")

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.warning("⚠️ Adiciona a tua chave API do OpenAI em Settings → Secrets.")
    st.stop()

client = OpenAI(api_key=api_key)

tema = st.text_area("✍️ Escreve o tema do post:", placeholder="Ex.: Novo casaco de outono, foco em elegância e conforto.")

st.markdown("🎯 **Ajuste de tom disponível a partir do plano PRO** 🔒")
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
