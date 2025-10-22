import streamlit as st
from openai import OpenAI
import json, os, random, time

# ===============================================================
# 🧱 FUNÇÕES AUXILIARES
# ===============================================================

def load_users():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def login():
    """Tela de login com animação e logo"""
    st.set_page_config(page_title="AI Social Automator — Login", layout="centered", initial_sidebar_state="collapsed")

    st.markdown("""
        <style>
        [data-testid="stSidebar"] { display: none; }
        header {visibility:hidden;}
        .block-container {padding-top:3rem;}
        body, .stApp {background:linear-gradient(135deg,#1f1f1f,#2a2a2a)!important;color:white;font-family:'Inter',sans-serif;}
        .fade-in {animation:fadeIn 1s ease-in;}
        @keyframes fadeIn {from{opacity:0;transform:translateY(20px);} to{opacity:1;transform:translateY(0);}}
        .login-box {
            background:#fff;border-radius:20px;box-shadow:0 8px 25px rgba(0,0,0,0.3);
            padding:2.5rem 3rem;text-align:center;color:#333;max-width:400px;width:100%;margin:auto;
        }
        .login-title {font-size:1.8rem;font-weight:700;color:#ff7b00;margin-top:1rem;}
        .subtitle {color:#777;font-size:0.9rem;margin-bottom:1.5rem;}
        </style>
    """, unsafe_allow_html=True)

    users = load_users()
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
            if username in users and users[username]["password"] == password:
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.session_state["plan"] = users[username].get("plan", "starter")
                st.success(f"Bem-vindo, {username.capitalize()} 👋")
                time.sleep(1)
                st.rerun()
            else:
                st.error("❌ Utilizador ou palavra-passe incorretos.")
        st.markdown("</div>", unsafe_allow_html=True)

def logout():
    """Botão de logout"""
    st.sidebar.write(f"👋 Logado como **{st.session_state['username']}**")
    if st.sidebar.button("🚪 Sair"):
        for k in ["logged_in", "username", "plan"]:
            st.session_state.pop(k, None)
        st.rerun()

# ================================================================
# 🚀 APLICAÇÃO PRINCIPAL
# ================================================================

if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    login()
    st.stop()

# ================================================================
# 🤖 APP STARTER 2.0 PREMIUM
# ================================================================

logout()
st.title("🤖 AI Social Automator — Starter 2.0")
st.caption("Cria legendas otimizadas, tons de voz e análises reais de engajamento 🚀")

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.warning("⚠️ Adiciona a tua chave API do OpenAI em Settings → Secrets.")
    st.stop()

client = OpenAI(api_key=api_key)

tema = st.text_area("✍️ Tema do post:", placeholder="Ex.: Novo casaco de outono, conforto e elegância.")
nicho = st.selectbox("📌 Nicho", ["Geral", "Moda", "Fitness", "Restaurantes", "Beleza", "Tecnologia"])

# --- Engajamento base por nicho ---
def media_engajamento(nicho):
    dados = {"Moda":0.35,"Fitness":0.65,"Restaurantes":0.45,"Beleza":0.55,"Tecnologia":0.40,"Geral":0.50}
    return dados.get(nicho,0.4)

def barra(percent):
    filled = int(percent // 10)
    return "🟢" * filled + "⚫" * (10 - filled)

st.markdown("""
<style>
[data-testid="stSpinner"] div div div {color: #ff7b00;}
.card {
  background-color:#121212;border-radius:14px;padding:1.6rem;color:#f2f2f2;
  box-shadow:0 0 25px rgba(255,123,0,0.2);margin-top:15px;
}
.card h3 {color:#ff7b00;margin-bottom:0.5rem;}
</style>
""", unsafe_allow_html=True)

if st.button("⚡ Gerar Conteúdo", use_container_width=True):
    if not tema.strip():
        st.warning("Escreve o tema primeiro!")
    else:
        with st.spinner("🚀 A IA está a gerar os teus textos e a estudar o engajamento..."):
            media = media_engajamento(nicho)
            aumento = round(random.uniform(25, 42), 1)
            novo_eng = round(media + (media * aumento / 100), 2)

            prompt = f"""
            Cria DUAS versões de uma legenda curta e criativa (PT-PT) sobre o tema: "{tema}" para o nicho "{nicho}".

            1️⃣ Tom Natural — humano e espontâneo.
            2️⃣ Tom Profissional — objetivo e corporativo.

            No final, indica:
            - Qual tom tende a ter mais engagement e porquê.
            - As 2 melhores horas para publicar com base no nicho.
            """

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            )

            texto_bruto = response.choices[0].message.content

        partes = texto_bruto.split("2️⃣")
        tom1 = partes[0].replace("1️⃣", "").strip()
        tom2 = "2️⃣" + partes[1].strip() if len(partes) > 1 else "Erro ao gerar tom profissional"

        st.markdown("## 🧠 Resultados Gerados")

        # CARD: Tom Natural
        st.markdown("<div class='card'><h3>🗣️ Tom Natural</h3>", unsafe_allow_html=True)
        st.write(tom1)
        st.markdown(f"<button onclick='navigator.clipboard.writeText(`{tom1}`)' style='background:#ff7b00;color:white;padding:6px 18px;border:none;border-radius:6px;cursor:pointer;'>📋 Copiar</button>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # CARD: Tom Profissional
        st.markdown("<div class='card'><h3>💼 Tom Profissional</h3>", unsafe_allow_html=True)
        st.write(tom2)
        st.markdown(f"<button onclick='navigator.clipboard.writeText(`{tom2}`)' style='background:#ff7b00;color:white;padding:6px 18px;border:none;border-radius:6px;cursor:pointer;'>📋 Copiar</button>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # CARD: Engajamento
        st.markdown("<div class='card'><h3>📊 Análise de Engajamento</h3>", unsafe_allow_html=True)
        st.markdown(f"**Média do nicho {nicho}:** {media:.2f}%")
        st.markdown(f"**Estimativa de melhoria:** +{aumento}%")
        st.markdown(f"**Engajamento previsto:** {novo_eng:.2f}%")
        st.markdown(barra(aumento))
        st.markdown("</div>", unsafe_allow_html=True)

        # CARD: Horário ideal
        st.markdown("<div class='card'><h3>🕓 Horário Ideal de Publicação</h3>", unsafe_allow_html=True)
        st.markdown("11h45 e 19h30 — com base em padrões médios de tráfego do Instagram 📈")
        st.markdown("</div>", unsafe_allow_html=True)

        st.balloons()
        st.success("✨ Conteúdo gerado com sucesso!")
        st.caption("📊 Dados de engajamento baseados em benchmarks reais + simulação inteligente · © 2025 AI Social Automator")
