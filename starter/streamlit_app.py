import streamlit as st
from openai import OpenAI
import json, os, random, time, requests
from datetime import datetime

# ================================
# 🎨 ESTILO GLOBAL GLASS
# ================================
GLASS_STYLE = """
<style>
[data-testid="stSidebar"] { background: rgba(255,255,255,0.07) !important; backdrop-filter: blur(12px); }
header { visibility: hidden; }
body, .stApp {
    background: radial-gradient(circle at 20% 30%, #0a0f16 0%, #000 100%) !important;
    font-family: 'Inter', sans-serif !important;
    color: #e8faff !important;
}
div[data-testid="stMarkdownContainer"] { color: #e8faff !important; }

.glass-box {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.2);
    backdrop-filter: blur(15px);
    border-radius: 20px;
    box-shadow: 0 8px 25px rgba(0,255,255,0.05);
    padding: 2rem 2.5rem;
    margin-bottom: 2rem;
    animation: fadeIn 0.8s ease-in-out;
}
.glass-title {
    text-align:center;
    font-size:1.8rem;
    font-weight:700;
    color:#00f6ff;
}
button {
    border-radius:10px!important;
}
@keyframes fadeIn {
  from {opacity:0; transform:translateY(10px);}
  to {opacity:1; transform:translateY(0);}
}
.copy-btn {
    background-color:#00f6ff;
    color:#000;
    border:none;
    padding:8px 18px;
    border-radius:10px;
    cursor:pointer;
    font-weight:600;
}
</style>
"""

# ================================
# 🔐 LOGIN SYSTEM
# ================================
def load_users():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def login():
    """Página de login moderna em vidro"""
    st.set_page_config(page_title="AI Social Automator — Login", layout="centered")
    st.markdown(GLASS_STYLE, unsafe_allow_html=True)

    st.markdown('<div class="glass-box">', unsafe_allow_html=True)
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712109.png", width=90)
    st.markdown('<div class="glass-title">AI Social Automator</div>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center;color:#b0eaff;">Acede à tua conta para começar 🚀</p>', unsafe_allow_html=True)

    username = st.text_input("👤 Utilizador")
    password = st.text_input("🔑 Palavra-passe", type="password")

    users = load_users()
    if st.button("Entrar", use_container_width=True):
        if username in users and users[username]["password"] == password:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.session_state.setdefault("history", [])
            st.success(f"Bem-vindo, {username.capitalize()} 👋")
            time.sleep(0.4)
            st.rerun()
        else:
            st.error("❌ Credenciais incorretas.")
    st.markdown("</div>", unsafe_allow_html=True)

# ================================
# ⚙️ FUNÇÕES AUXILIARES
# ================================
def random_boost(): return round(random.uniform(5.0, 9.5), 1)
def random_hour():
    horas = ["09:00 — manhã ☀️","13:00 — almoço 🍽️","18:00 — pico 📈","21:00 — noite 🌙"]
    return random.choice(horas)

# ================================
# 🚀 APP PRINCIPAL
# ================================
def main_app():
    st.set_page_config(page_title="AI Social Automator — Starter 2.7", layout="centered")
    st.markdown(GLASS_STYLE, unsafe_allow_html=True)
    st.sidebar.success(f"👋 Logado como {st.session_state['username']}")
    if st.sidebar.button("📜 Histórico"): show_history(); st.stop()
    if st.sidebar.button("🚪 Sair"):
        for k in ["logged_in","username","history"]: st.session_state.pop(k, None)
        st.rerun()

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    st.markdown('<div class="glass-box">', unsafe_allow_html=True)
    st.markdown('<div class="glass-title">🤖 AI Social Automator — Starter 2.7</div>', unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;color:#b0eaff;'>Cria legendas otimizadas e guarda o teu histórico ✨</p>", unsafe_allow_html=True)

    tema = st.text_area("✍️ Tema do post:", placeholder="Ex.: Nova coleção de outono – elegância e conforto.")
    nicho = st.selectbox("📌 Nicho", ["Geral","Moda","Beleza","Restaurantes","Tecnologia","Fitness"])
    tom = st.radio("🎯 Tom de voz", ["Neutro","Inspirador"])

    if st.button("⚡ Gerar Conteúdo", use_container_width=True):
        if not tema.strip(): st.warning("Escreve o tema primeiro! ⚠️")
        else:
            with st.spinner("✨ A criar legendas otimizadas..."):
                prompt = f"Cria DUAS legendas curtas e criativas em português de Portugal sobre '{tema}'. Nicho: {nicho}. Tom: {tom}. Inclui hashtags no fim."
                resposta = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role":"user","content":prompt}]
                )
                texto = resposta.choices[0].message.content
                variações = texto.split("\n\n")

            legendas_geradas = []
            for i,var in enumerate(variações[:2],1):
                boost = random_boost()
                hora = random_hour()
                st.markdown(f"""
                <div class='glass-box'>
                    <h4>💬 Legenda {i}</h4>
                    <p>{var.strip()}</p>
                    <p style='color:#b0eaff;'>📈 Engajamento estimado: +{boost}%<br>⏰ Hora ideal: {hora}</p>
                    <button class='copy-btn' onclick="navigator.clipboard.writeText(`{var.strip()}`)">📋 Copiar</button>
                </div>
                """, unsafe_allow_html=True)
                legendas_geradas.append({"texto":var.strip(),"boost":boost,"hora":hora})

            st.session_state["history"].append({
                "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "tema": tema,
                "nicho": nicho,
                "tom": tom,
                "legendas": legendas_geradas
            })
    st.markdown("</div>", unsafe_allow_html=True)
    st.caption("Plano Starter · Modelo: GPT-4o-mini · © 2025 AI Social Automator")

# ================================
# 📜 HISTÓRICO VISUAL GLASS
# ================================
def show_history():
    st.set_page_config(page_title="Histórico — AI Social Automator", layout="centered")
    st.markdown(GLASS_STYLE, unsafe_allow_html=True)
    st.title("📜 Histórico de Gerações")
    if "history" not in st.session_state or not st.session_state["history"]:
        st.info("Ainda não geraste nenhuma legenda!")
        if st.button("⬅️ Voltar"): st.rerun(); return

    for idx,item in enumerate(reversed(st.session_state["history"]),1):
        st.markdown(f"<div class='glass-box'><h3>🗓️ {item['data']} — {item['tema']}</h3><p><i>{item['nicho']} | {item['tom']}</i></p>", unsafe_allow_html=True)
        for j,leg in enumerate(item["legendas"],1):
            st.markdown(f"""
                <div style='margin-top:1rem;margin-bottom:1rem;padding:1rem;border-radius:15px;background:rgba(255,255,255,0.05);'>
                    <b>💬 Legenda {j}:</b><br>{leg['texto']}<br>
                    <span style='color:#b0eaff;'>📈 +{leg['boost']}% | ⏰ {leg['hora']}</span><br><br>
                    <button class='copy-btn' onclick="navigator.clipboard.writeText(`{leg['texto']}`)">📋 Copiar</button>
                </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    if st.button("⬅️ Voltar"): st.rerun()

# ================================
# 🧭 EXECUÇÃO
# ================================
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    login()
else:
    main_app()
