import streamlit as st
from openai import OpenAI
import json, os, random, time, requests
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
            st.session_state.setdefault("history", [])
            st.success(f"Bem-vindo, {username.capitalize()} 👋")
            time.sleep(0.5)
            st.rerun()
        else:
            st.error("❌ Credenciais incorretas.")
    st.markdown("</div>", unsafe_allow_html=True)

# ================================
# 📊 FUNÇÕES AUXILIARES
# ================================
def random_boost():
    return round(random.uniform(5.0, 9.5), 1)

def random_hour():
    horas = [
        "09:00 — manhã, bom para lifestyle ☀️",
        "13:00 — hora de almoço 🍽️",
        "18:00 — pico de atividade 📈",
        "21:00 — posts noturnos de alto alcance 🌙"
    ]
    return random.choice(horas)

def typing_effect(text, speed=0.015):
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
    st.set_page_config(page_title="AI Social Automator — Starter 2.6", layout="centered")
    st.sidebar.success(f"👋 Logado como {st.session_state['username']}")

    if st.sidebar.button("📜 Histórico"):
        show_history()
        st.stop()

    if st.sidebar.button("🚪 Sair"):
        for k in ["logged_in", "username", "plan", "history"]:
            st.session_state.pop(k, None)
        st.rerun()

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    st.markdown("<h1 style='text-align:center;'>🤖 AI Social Automator — Starter 2.6</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>Cria legendas otimizadas, tons de voz e guarda o teu histórico de criações 📊</p>", unsafe_allow_html=True)
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
                variações = texto.split("\n\n")

            st.subheader("🧠 Legendas sugeridas:")

            legendas_geradas = []
            for i, var in enumerate(variações[:2], 1):
                boost = random_boost()
                hora = random_hour()

                with st.container():
                    st.markdown(f"**💬 Legenda {i}:**")
                    typing_effect(var.strip())

                    col1, col2 = st.columns([1, 6])
                    with col1:
                        if st.button(f"📋 Copiar {i}", key=f"copy_{i}"):
                            st.session_state["copied"] = var.strip()
                            st.success("Copiado com sucesso!")
                    with col2:
                        st.info(f"📈 Engajamento estimado: +{boost}% | ⏰ Hora ideal: {hora}")

                legendas_geradas.append({
                    "texto": var.strip(),
                    "boost": boost,
                    "hora": hora
                })

            # Salva no histórico
            st.session_state["history"].append({
                "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "tema": tema,
                "nicho": nicho,
                "tom": tom,
                "legendas": legendas_geradas
            })

    st.caption("Plano Starter · Modelo: GPT-4o-mini · © 2025 AI Social Automator")

# ================================
# 📜 MODO HISTÓRICO
# ================================
def show_history():
    st.title("📜 Histórico de Gerações")
    if "history" not in st.session_state or not st.session_state["history"]:
        st.info("Ainda não geraste nenhuma legenda!")
        if st.button("⬅️ Voltar"):
            st.rerun()
        return

    for idx, item in enumerate(reversed(st.session_state["history"]), 1):
        st.markdown(f"### 🗓️ {item['data']} — Tema: *{item['tema']}* ({item['nicho']}, {item['tom']})")
        for j, leg in enumerate(item["legendas"], 1):
            st.markdown(f"**💬 Legenda {j}:** {leg['texto']}")
            st.caption(f"📈 +{leg['boost']}% | ⏰ {leg['hora']}")
            if st.button(f"📋 Copiar {idx}-{j}", key=f"copy_hist_{idx}_{j}"):
                st.session_state["copied"] = leg["texto"]
                st.success("Copiado!")

        st.markdown("---")

    if st.button("⬅️ Voltar"):
        st.rerun()

# ================================
# 🧭 EXECUÇÃO
# ================================
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    login()
else:
    main_app()
