import streamlit as st
import streamlit.components.v1 as components
from openai import OpenAI
import os, json, time, random, base64, uuid
from datetime import datetime
from pathlib import Path

# -------------------- CONFIG --------------------
st.set_page_config(page_title="AI Social Automator — Starter 2.9", page_icon="🤖", layout="centered")
APP_TITLE = "AI Social Automator"
BASE = Path(__file__).parent
ASSETS = BASE / "assets"
ASSETS.mkdir(exist_ok=True)
HIST_DIR = BASE / "history"
HIST_DIR.mkdir(exist_ok=True)

ROBOT_LEFT  = str(ASSETS / "robot_left.png")
ROBOT_MID   = str(ASSETS / "robot_center.png")
ROBOT_RIGHT = str(ASSETS / "robot_right.png")

if not Path(ROBOT_LEFT).exists():
    ROBOT_LEFT = "https://raw.githubusercontent.com/encharm/Font-Awesome-SVG-PNG/master/white/png/256/rocket.png"
if not Path(ROBOT_MID).exists():
    ROBOT_MID = "https://raw.githubusercontent.com/encharm/Font-Awesome-SVG-PNG/master/white/png/256/robot.png"
if not Path(ROBOT_RIGHT).exists():
    ROBOT_RIGHT = "https://raw.githubusercontent.com/encharm/Font-Awesome-SVG-PNG/master/white/png/256/bolt.png"

# -------------------- ESTILO --------------------
st.markdown("""
<style>
.stApp { background: radial-gradient(1200px 600px at 50% -10%, #0e1a22 0%, #0a1016 45%, #060b10 100%); color:#e8f4ff; font-family: Inter, system-ui; }
.block-container { max-width: 900px; }
.glass { background: rgba(180,230,255,.06); border:1px solid rgba(160,220,255,.18);
         border-radius:18px; box-shadow:0 12px 35px rgba(0,0,0,.35); backdrop-filter: blur(12px); }
.h1 { text-align:center; font-weight:800; font-size:clamp(26px,4vw,44px); color:#9be3ff; text-shadow:0 0 18px rgba(90,200,255,.25); margin:6px 0 8px; }
.subtle { text-align:center; color:#b9d5e6; margin-top:-6px; }
.card { padding:26px; border-radius:16px; }
.badge { display:inline-flex; gap:.5rem; padding:8px 12px; border-radius:12px; font-weight:700;
         background:rgba(150,220,255,.12); border:1px solid rgba(160,220,255,.22); }
.caption-card { border-left:4px solid #44c6ff; padding:14px 18px; border-radius:12px;
                background:rgba(180,230,255,.05); border:1px solid rgba(160,220,255,.20); }
.robots { display:flex; justify-content:center; gap:28px; margin:10px 0 8px; }
.robots img { filter: drop-shadow(0 10px 30px rgba(0,200,255,.25)); }
.robot-sit { transform: translateY(6px) scale(.96); }
.robot-mid { transform: translateY(-3px) scale(1.05); }
.copy-btn { background: linear-gradient(90deg,#1ebfff,#009cff); color:#00131a; border:none; border-radius:10px;
            padding:8px 16px; font-weight:700; cursor:pointer; box-shadow:0 0 10px rgba(30,191,255,.35); }
hr { border: 1px solid rgba(160,220,255,0.15); }
</style>
""", unsafe_allow_html=True)

# -------------------- UTILS --------------------
def ensure_client():
    api = os.getenv("OPENAI_API_KEY")
    if not api:
        st.warning("⚠️ Adiciona a tua chave em **Settings → Secrets → OPENAI_API_KEY**.")
        st.stop()
    return OpenAI(api_key=api)

def load_users():
    with open(BASE/"users.json","r",encoding="utf-8") as f:
        return json.load(f)

def hpath(username:str) -> Path:
    return HIST_DIR / f"{username}.json"

def load_history(username:str):
    p = hpath(username)
    if not p.exists(): return []
    try:
        return json.load(open(p,"r",encoding="utf-8"))
    except: return []

def save_history(username:str, record:dict):
    data = load_history(username)
    data.append(record)
    with open(hpath(username),"w",encoding="utf-8") as f:
        json.dump(data,f,ensure_ascii=False,indent=2)

def js_copy_button(label:str, text:str, key:str):
    """Botão Copiar funcional via components.html (compatível com Streamlit Cloud)."""
    # Protege o conteúdo para JS
    safe = text.replace("`","\\`")
    html = f"""
    <div style='display:inline-flex;align-items:center;gap:10px;'>
      <button id='{key}' class='copy-btn'
        onclick="navigator.clipboard.writeText(`{safe}`); const b=document.getElementById('{key}');
                 b.innerText='Copiado ✅'; setTimeout(()=>b.innerText='{label}',1200);">
        {label}
      </button>
    </div>
    """
    components.html(html, height=50)

def dynamic_stats(seed=None):
    rnd = random.Random(seed or time.time_ns())
    pct = round(rnd.uniform(4.8, 9.0), 1)
    hour, note = rnd.choice([
        ("13:00", "hora de almoço 🍽️"),
        ("18:00", "fim de tarde — maior atividade 🏙️"),
        ("21:00", "noite — bom alcance 🌙"),
    ])
    return pct, hour, note

def gen_two_captions(theme, niche, tone):
    client = ensure_client()
    sys = "És copywriter de social media. Responde em PT-PT. Máx 2 frases por legenda. Inclui até 3 hashtags."
    user = f"Tema: {theme}\nNicho: {niche}\nTom: {tone}\nCria DUAS legendas curtas e distintas, com emojis e 2–3 hashtags. Formata como 1) ... 2) ..."
    r = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"system","content":sys},{"role":"user","content":user}],
        temperature=0.7, max_tokens=240
    )
    txt = r.choices[0].message.content.strip()
    parts = []
    for ln in txt.splitlines():
        s = ln.strip()
        if s[:2] in ("1)", "2)"):
            parts.append(s[2:].strip(": ").strip())
    if len(parts)<2:
        half = len(txt)//2
        parts = [txt[:half].strip(), txt[half:].strip()]
    return parts[:2]

# -------------------- LOGIN --------------------
def login_screen():
    users = load_users()
    st.markdown('<div class="glass card">', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="robots">
      <img class="robot-sit" src="{ROBOT_LEFT}" width="84">
      <img class="robot-mid" src="{ROBOT_MID}" width="112">
      <img class="robot-sit" src="{ROBOT_RIGHT}" width="84">
    </div>
    """, unsafe_allow_html=True)
    st.markdown(f'<div class="h1">{APP_TITLE}</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtle">Acede à tua conta para começar 🚀</div>', unsafe_allow_html=True)
    st.write("")

    with st.form("login_form", clear_on_submit=False):
        u = st.text_input("👤 Utilizador")
        p = st.text_input("🔑 Palavra-passe", type="password")
        ok = st.form_submit_button("Entrar", use_container_width=True)
        if ok:
            if u in users and users[u].get("password")==p:
                st.session_state["logged_in"]=True
                st.session_state["username"]=u
                st.session_state["mode"]="main"
                st.success(f"Bem-vindo, {u} 👋")
                time.sleep(0.5); st.rerun()
            else:
                st.error("❌ Credenciais incorretas.")
    st.markdown('</div>', unsafe_allow_html=True)

# -------------------- MAIN --------------------
def main_page():
    user = st.session_state.get("username","")
    st.markdown('<div class="glass card">', unsafe_allow_html=True)
    st.markdown(f'<div class="h1">{APP_TITLE} — Starter 2.9</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtle">Legendas otimizadas, tons e histórico — tudo num clique ✨</div>', unsafe_allow_html=True)
    st.write("")

    theme = st.text_area("📝 Tema do post:", placeholder="Ex.: Nova coleção de outono — elegância e conforto")
    col1, col2 = st.columns(2)
    with col1:
        niche = st.selectbox("📌 Nicho", ["Geral","Moda","Fitness","Restaurantes","Beleza","Tecnologia"])
    with col2:
        tone = st.radio("🎚️ Tom de voz", ["Neutro","Inspirador"], horizontal=True)

    colA, colB = st.columns(2)
    gen = colA.button("⚡ Gerar Conteúdo", use_container_width=True, key="gen_btn")
    hist = colB.button("📜 Histórico", use_container_width=True, key="hist_btn")

    st.markdown('</div>', unsafe_allow_html=True)

    if hist:
        st.session_state["mode"]="history"; st.rerun()

    if gen:
        if not theme.strip():
            st.warning("Escreve o tema do post primeiro.")
            return
        with st.spinner("✨ A criar duas opções de legenda…"):
            captions = gen_two_captions(theme, niche, tone)
            stats = [dynamic_stats(seed=random.randint(1,999999)) for _ in range(2)]

        st.markdown('<div class="glass card">', unsafe_allow_html=True)
        st.subheader("🧠 Legendas sugeridas")
        for i, cap in enumerate(captions, start=1):
            pct, hr, note = stats[i-1]
            st.markdown(f'<div class="caption-card">', unsafe_allow_html=True)
            st.markdown(f"**{i}.** {cap}")
            st.markdown(
                f'<div class="badge">📈 Engajamento: +{pct}%</div> &nbsp; '
                f'<div class="badge">🕒 {hr} — {note}</div>',
                unsafe_allow_html=True
            )
            js_copy_button(f"📋 Copiar {i}", cap, key=f"copy_{uuid.uuid4().hex}")
            st.markdown('</div>', unsafe_allow_html=True)
            st.write("")

        # guardar histórico por utilizador (ficheiro local por agora)
        now = datetime.now().strftime("%d/%m/%Y %H:%M")
        record = {
            "when": now, "theme": theme, "niche": niche, "tone": tone,
            "items": [
                {"caption": captions[0], "engagement": stats[0][0], "hour": stats[0][1], "note": stats[0][2]},
                {"caption": captions[1], "engagement": stats[1][0], "hour": stats[1][1], "note": stats[1][2]},
            ]
        }
        save_history(user, record)
        st.success("Guardado no teu histórico. 📜")
        st.markdown('</div>', unsafe_allow_html=True)

# -------------------- HISTÓRICO --------------------
def history_page():
    user = st.session_state.get("username","")
    data = list(reversed(load_history(user)))

    st.markdown('<div class="glass card">', unsafe_allow_html=True)
    st.subheader("📜 Histórico de Gerações")

    if not data:
        st.info("Ainda não geraste nenhuma legenda.")
        if st.button("⬅️ Voltar", key="back_empty"): st.session_state["mode"]="main"; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True); return

    for i, rec in enumerate(data, start=1):
        st.markdown(f"**🗓️ {rec['when']} — Tema:** *{rec['theme']}*  **({rec['niche']}, {rec['tone']})*")
        for j, it in enumerate(rec["items"], start=1):
            st.markdown('<div class="caption-card">', unsafe_allow_html=True)
            st.markdown(f"**💬 Legenda {i}.{j}:** {it['caption']}")
            st.markdown(
                f'<div class="badge">📊 +{it["engagement"]}%</div> &nbsp; '
                f'<div class="badge">🕒 {it["hour"]} — {it["note"]}</div>',
                unsafe_allow_html=True
            )
            js_copy_button(f"📋 Copiar {i}-{j}", it["caption"], key=f"copy_hist_{uuid.uuid4().hex}")
            st.markdown('</div>', unsafe_allow_html=True)
            st.write("")
        st.markdown("<hr/>", unsafe_allow_html=True)

    if st.button("⬅️ Voltar", key="back_hist"): st.session_state["mode"]="main"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# -------------------- NAV / AUTH --------------------
def logout_pill():
    with st.sidebar:
        st.markdown("##### 👋 Logado como **{}**".format(st.session_state.get("username","")))
        if st.button("Sair", key="logout_btn"):
            for k in ["logged_in","username","mode"]: st.session_state.pop(k, None)
            st.rerun()

def router():
    if not st.session_state.get("logged_in"): login_screen(); return
    logout_pill()
    (history_page() if st.session_state.get("mode")=="history" else main_page())

# -------------------- BOOT --------------------
router()
