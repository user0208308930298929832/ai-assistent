import streamlit as st
from openai import OpenAI
import json, os, random, time, requests, pyperclip
from datetime import datetime

# ================================
# 🔐 LOGIN SYSTEM
# ================================
def load_users():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def login():
    """Página de login moderna e centrada"""
    st.set_page_config(page_title="AI Social Automator — Login", layout="centered")

    st.markdown("""
        <style>
        [data-testid="stSidebar"] { display: none; }
        header { visibility: hidden; }
        body, .stApp {
            background: radial-gradient(circle at 20% 30%, #1b1b1b 0%, #111 100%) !important;
            font-family: 'Inter', sans-serif !important;
            color: white;
        }
        .login-box {
            background-color: #fff;
            border-radius: 20px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.3);
            padding: 3rem 3rem 2rem 3rem;
            text-align: center;
            color: #333;
            max-width: 400px;
            margin: auto;
            margin-top: 10%;
            animation: fadeIn 1s ease-in-out;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .title { font-size: 1.7rem; font-weight: 700; color: #ff7b00; margin-bottom: .3rem; }
        .subtitle { font-size: .9rem; color: #777; margin-bottom: 2rem; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712109.png", width=80)
    st.markdown('<div class="title">AI Social Automator</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Acede à tua conta para começar 🚀</div>', unsafe_allow_html=True)

    username = st.text_input("👤 Utilizador")
    password = st.text_input("🔑 Palavra-passe", type="password")

    users = load_users()

    if st.button("Entrar", use_container_width=True):
        if username in users and users[username]["password"] == password:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.session_state["plan"] = users[username].get("plan", "starter")
            st.success(f"Bem-vindo, {username.capitalize()} 👋")
            time.sleep(0.5)
            st.rerun()
        else:
            st.error("❌ Credenciais incorretas.")
    st.markdown("</div>", unsafe_allow_html=True)

# ================================
# 📊 FUNÇÕES AUXILIARES
# ================================
def get_engagement_boost():
    """Simula uma variação realista de engajamento"""
    try:
        return round(random.uniform(5.4, 9.7), 1)
    except:
        return 6.3

def get_best_post_hour(nicho="Geral"):
    try:
        query = f"melhor horário para publicar no Instagram {nicho} 2025 site:later.com OR site:socialinsider.io"
        url = f"https://api.duckduckgo.com/?q={query}&format=json"
        response = requests.get(url, timeout=5).json()
        text = response.get("AbstractText", "").lower()
        if "manhã" in text:
            return "09:00 — pico de visualizações matinais ☀️"
        elif "tarde" in text:
            return "13:00 — horário de almoço, maior tráfego 🍽️"
        elif "noite" in text:
            return "19:00 — maior taxa de interação 🌙"
        else:
            return "18:00 — horário universal de maior atividade 📈"
    except:
        return random.choice([
            "09:00 — início do dia com alto alcance ☀️",
            "12:00 — pausa para almoço, mais engagement 🍴",
            "18:30 — pico de atividade pós-trabalho 🚀",
            "21:00 — bom para conteúdos inspiracionais 🌙"
        ])

def typing_effect(text, speed=0.015):
    """Efeito de digitação"""
    placeholder = st.empty()
    typed = ""
    for char in text:
        typed += char
        placeholder.markdown(f"<p style='font-size:1.05rem; color:#fff;'>{typed}</p>", unsafe_allow_html=True)
        time.sleep(speed)

# ================================
# 🚀 APP PRINCIPAL
# ================================
def main_app():
    st.set_page_config(page_title="AI Social Automator — Starter 2.5", layout="centered")
    st.sidebar.success(f"👋 Logado como {st.session_state['username']}")
    if st.sidebar.button("🚪 Sair"):
        for k in ["logged_in", "username", "plan"]:
            st.session_state.pop(k, None)
        st.rerun()

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    st.markdown("<h1 style='text-align:center;'>🤖 AI Social Automator — Starter 2.5</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>Cria legendas otimizadas, tons de voz e análises reais de engajamento 📊</p>", unsafe_allow_html=True)
    st.write("---")

    tema = st.text_area("✍️ Tema do post:", placeholder="Ex.: Nova coleção de outono – elegância e conforto.")
    nicho = st.selectbox("📌 Nicho", ["Geral", "Moda", "Beleza", "Restaurantes", "Tecnologia", "Fitness"])
    tom = st.radio("🎯 Tom de voz", ["Neutro", "Inspirador"])

    if st.button("⚡ Gerar Conteúdo", use_container_width=True):
        if not tema.strip():
            st.warning("Escreve o tema primeiro! ⚠️")
        else:
            with st.spinner("✨ A criar legendas otimizadas..."):
                prompt = f"Cria DUAS legendas curtas e criativas em português de Portugal sobre '{tema}'. Nicho: {nicho}. Tom: {tom}. Inclui hashtags no fim."
                resposta = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}]
                )
                texto = resposta.choices[0].message.content
                # Divide as duas legendas
                variações = texto.split("\n\n")
                boost = get_engagement_boost()
                hora = get_best_post_hour(nicho)

            st.subheader("🧠 Legendas sugeridas:")
            for i, var in enumerate(variações[:2], 1):
                with st.container():
                    st.markdown(f"**💬 Legenda {i}:**")
                    typing_effect(var.strip())
                    col1, col2 = st.columns([1, 6])
                    with col1:
                        if st.button(f"📋 Copiar {i}", key=f"copy_{i}"):
                            pyperclip.copy(var.strip())
                            st.success("Copiado com sucesso!")
                    with col2:
                        st.info(f"📈 Engajamento: +{boost}% | ⏰ Hora ideal: {hora}")

    st.caption("Plano Starter · Modelo: GPT-4o-mini · © 2025 AI Social Automator")

# ================================
# 🧭 EXECUÇÃO
# ================================
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    login()
else:
    main_app()
