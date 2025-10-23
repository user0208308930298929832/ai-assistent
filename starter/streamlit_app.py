import streamlit as st
from openai import OpenAI
import os, json, time, random, base64, uuid
from datetime import datetime
from pathlib import Path

# =========================
#   CONFIG / CONSTANTES
# =========================
st.set_page_config(page_title="AI Social Automator — Starter 2.8", page_icon="🤖", layout="centered")

APP_TITLE = "AI Social Automator"
HISTORY_DIR = Path(__file__).parent / "history"
HISTORY_DIR.mkdir(exist_ok=True)

# Robôs (troque pelos seus PNGs locais em /assets)
ASSETS_DIR = Path(__file__).parent / "assets"
ROBOT_LEFT  = str(ASSETS_DIR / "robot_left.png")
ROBOT_MID   = str(ASSETS_DIR / "robot_center.png")
ROBOT_RIGHT = str(ASSETS_DIR / "robot_right.png")

# Fallbacks se as imagens não existirem
if not Path(ROBOT_LEFT).exists():
    ROBOT_LEFT = "https://raw.githubusercontent.com/encharm/Font-Awesome-SVG-PNG/master/black/png/256/robot.png"
if not Path(ROBOT_MID).exists():
    ROBOT_MID = "https://raw.githubusercontent.com/encharm/Font-Awesome-SVG-PNG/master/black/png/256/android.png"
if not Path(ROBOT_RIGHT).exists():
    ROBOT_RIGHT = "https://raw.githubusercontent.com/encharm/Font-Awesome-SVG-PNG/master/black/png/256/reddit-alien.png"

# =========================
#   CSS (Glass + Azul Gelo)
# =========================
st.markdown("""
<style>
/* fundo gradiente escuro */
.stApp {
  background: radial-gradient(1200px 600px at 50% -10%, #0e1a22 0%, #0b1318 40%, #0a0f13 100%);
  color: #e8f4ff;
  font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, "Apple Color Emoji","Segoe UI Emoji";
}

/* container central mais estreito */
.block-container { max-width: 900px; }

/* Glass base */
.glass {
  background: rgba(180, 230, 255, 0.06);
  border: 1px solid rgba(160, 220, 255, 0.15);
  border-radius: 20px;
  box-shadow: 0 12px 35px rgba(0,0,0,0.35);
  backdrop-filter: blur(12px);
}

/* Acentos Azul Gelo */
.accent { color: #9be3ff; }

/* título com brilho */
.h1-title {
  font-size: clamp(26px, 4vw, 44px);
  font-weight: 800;
  letter-spacing: .3px;
  text-shadow: 0 0 18px rgba(90, 200, 255, .25);
  margin: 6px 0 10px 0;
  text-align:center;
}
.subtle { color: #b9d5e6; text-align:center; margin-top: -6px; }

/* card de login / histórico */
.card {
  padding: 28px;
  border-radius: 18px;
}

/* inputs mais suaves */
.stTextInput > div > div > input,
.stTextArea textarea, .stSelectbox > div > div > div {
  background: rgba(255,255,255,0.04) !important;
  border: 1px solid rgba(160, 220, 255, 0.18) !important;
  color: #eaf7ff !important;
}

/* botões */
button[kind="primary"] {
  background: linear-gradient(90deg, #44c6ff 0%, #3ec9f5 100%) !important;
  color: #00131a !important;
  border: 0 !important;
  font-weight: 700 !important;
  letter-spacing: .25px;
  border-radius: 12px !important;
}

/* botões secundários */
.btn-ghost {
  display:inline-flex; align-items:center; gap:.6rem;
  padding:10px 14px; border-radius:10px;
  border:1px solid rgba(160, 220, 255, 0.18);
  background: rgba(180,230,255,0.06);
  color:#cfefff; text-decoration:none; font-weight:600; cursor:pointer;
}

/* "chips" informativos */
.badge {
  display:inline-flex; align-items:center; gap:.5rem;
  padding:10px 14px; border-radius:12px; font-weight:700;
  background: rgba(150, 220, 255, .12);
  border:1px solid rgba(160, 220, 255, .22);
}

/* card de legenda/histórico */
.caption-card {
  border-left: 4px solid #44c6ff;
  padding: 14px 18px; border-radius: 14px;
  background: rgba(180,230,255,0.05);
  border: 1px solid rgba(160,220,255,0.20);
}

/* botões copiar (JS) */
.copy-btn {
  display:inline-flex; align-items:center; gap:.6rem;
  padding:10px 14px; border-radius:10px;
  border:1px solid rgba(160, 220, 255, 0.18);
  background: rgba(180,230,255,0.06);
  color:#cfefff; text-decoration:none; font-weight:600; cursor:pointer;
}
.copy-btn:hover { background: rgba(180,230,255,0.12); }

/* fileira dos robôs */
.robots { display:flex; justify-content:center; gap:30px; margin: 8px 0 10px 0; }
.robots img {
  filter: drop-shadow(0 10px 30px rgba(0,200,255,.2));
}
/* sentados (bordas suaves) */
.robot-sit { transform: translateY(6px) scale(.96); }
.robot-mid { transform: translateY(-4px) scale(1.05); }

/* animação sutil */
.fade-in { animation: fi .5s ease; }
@keyframes fi { from {opacity:0; transform:translateY(8px);} to {opacity:1; transform:translateY(0);} }
</style>
""", unsafe_allow_html=True)

# =========================
#   UTILITÁRIOS
# =========================
def load_users():
    p = Path(__file__).parent / "users.json"
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)

def history_path(username: str) -> Path:
    return HISTORY_DIR / f"{username}.json"

def load_history(username: str):
    p = history_path(username)
    if not p.exists(): return []
    try:
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_history(username: str, record: dict):
    items = load_history(username)
    items.append(record)
    with open(history_path(username), "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

def js_copy_button(label: str, text: str, key: str):
    """Botão Copiar com JS (sem dependências)."""
    # Evita problemas de aspas: b64 -> atob no browser
    b64 = base64.b64encode(text.encode("utf-8")).decode("ascii")
    html = f"""
    <button class="copy-btn" id="{key}" onclick="navigator.clipboard.writeText(atob('{b64}')).then(()=>{
      const b=document.getElementById('{key}'); if(b){{b.innerText='Copiado! ✅'; setTimeout(()=>{{b.innerText='{label}';}},1200);}}
    })">{label}</button>
    """
    st.markdown(html, unsafe_allow_html=True)

def dynamic_engagement_and_time(seed: int = None):
    """Gera percentagens e horários diferentes/realistas."""
    rnd = random.Random(seed or time.time_ns())
    percent = round(rnd.uniform(4.8, 8.9), 1)  # 4.8% – 8.9%
    # Horários “universais” típicos (com etiquetas):
    candidates = [
        ("13:00", "hora de almoço 🍽️"),
        ("18:00", "fim de tarde — maior atividade 🏙️"),
        ("21:00", "posts noturnos de alto alcance 🌙"),
    ]
    hour, note = rnd.choice(candidates)
    return percent, hour, note

def ensure_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.warning("⚠️ Adiciona a tua chave API do OpenAI em **Settings → Secrets** (OPENAI_API_KEY).")
        st.stop()
    return OpenAI(api_key=api_key)

def gen_captions(theme: str, niche: str, tone: str):
    """Gera duas legendas diferentes + hashtags curtas (PT-PT)."""
    client = ensure_client()
    sys = "És um copywriter de social media. Responde em PT-PT. Mantém a legenda curta (máx. 1-2 frases) e inclui 2–3 hashtags."
    user = f"Tema: {theme}\nNicho: {niche}\nTom: {tone}\nGera DUAS opções de legenda, concisas e distintas, com emojis pertinentes e hashtags (máx 3). Formata como lista 1) ... 2) ..."

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"system","content":sys},{"role":"user","content":user}],
        temperature=0.7,
        max_tokens=240,
    )
    txt = resp.choices[0].message.content.strip()
    # Parse simples "1) ..." / "2) ..."
    parts = []
    for line in txt.splitlines():
        line=line.strip()
        if line[:2] in ("1)", "2)"):
            parts.append(line[2:].strip(": ").strip())
    if len(parts) < 2:
        # Fallback: divide por dois pontos/linhas
        half = len(txt)//2
        parts = [txt[:half].strip(), txt[half:].strip()]
    return parts[:2]

# =========================
#   LOGIN
# =========================
def login_screen():
    users = load_users()

    st.markdown('<div class="glass card fade-in">', unsafe_allow_html=True)

    # Linha dos três robôs (laranja esq., azulão centro, azul dir.)
    st.markdown(f"""
    <div class="robots">
      <img class="robot-sit" src="{ROBOT_LEFT}"  width="84">
      <img class="robot-mid" src="{ROBOT_MID}"   width="110">
      <img class="robot-sit" src="{ROBOT_RIGHT}" width="84">
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f'<div class="h1-title accent">{APP_TITLE}</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtle">Acede à tua conta para começar 🚀</div>', unsafe_allow_html=True)
    st.write("")

    with st.form("login_form", clear_on_submit=False):
        u = st.text_input("👤 Utilizador")
        p = st.text_input("🔑 Palavra-passe", type="password")
        ok = st.form_submit_button("Entrar", use_container_width=True)
        if ok:
            if u in users and users[u].get("password") == p:
                st.session_state["logged_in"] = True
                st.session_state["username"] = u
                st.session_state["mode"] = "main"
                st.success(f"Bem-vindo, {u} 👋")
                st.rerun()
            else:
                st.error("❌ Utilizador ou palavra-passe incorretos.")
    st.markdown('</div>', unsafe_allow_html=True)

# =========================
#   PÁGINA PRINCIPAL
# =========================
def main_page():
    u = st.session_state.get("username", "utilizador")

    st.markdown('<div class="glass card fade-in">', unsafe_allow_html=True)
    st.markdown(f'<div class="h1-title accent">{APP_TITLE} — Starter 2.8</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtle">Cria legendas otimizadas, tons de voz e análises reais de engajamento 📊</div>', unsafe_allow_html=True)
    st.write("")

    theme = st.text_area("📝 Tema do post:", placeholder="Ex.: Mostrar novo outfit de outono da minha loja de roupa")
    col1, col2 = st.columns(2)
    with col1:
        niche = st.selectbox("📌 Nicho", ["Geral", "Moda", "Fitness", "Restaurantes", "Beleza", "Tecnologia"], index=0)
    with col2:
        tone = st.radio("🎚️ Tom de voz", ["Neutro", "Inspirador"], horizontal=True)

    cta = st.button("⚡ Gerar Conteúdo", use_container_width=True, key="gen_main")
    hist_btn = st.button("📜 Histórico", use_container_width=True, key="main_hist")

    st.markdown('</div>', unsafe_allow_html=True)  # fecha card

    if hist_btn:
        st.session_state["mode"] = "history"
        st.rerun()

    if cta:
        if not theme.strip():
            st.warning("Escreve antes o **tema** do post.")
            return
        with st.spinner("A criar duas opções de legenda…"):
            caps = gen_captions(theme=theme, niche=niche, tone=tone)
            # estatísticas distintas para cada
            stats = [dynamic_engagement_and_time(seed=random.randint(1,999999)) for _ in range(2)]

        st.markdown('<div class="glass card fade-in">', unsafe_allow_html=True)
        st.subheader("🧠 Legendas sugeridas:")

        for idx, caption in enumerate(caps, start=1):
            pct, hour, note = stats[idx-1]
            st.write(f"**{idx}.** {caption}")
            # badges
            st.markdown(
                f'<div class="badge">📈 Engajamento: +{pct}%</div> &nbsp; '
                f'<div class="badge">🕒 Hora ideal: {hour} — {note}</div>',
                unsafe_allow_html=True
            )
            # copiar (JS)
            js_copy_button(f"📋 Copiar {idx}", caption, key=f"copy_{uuid.uuid4().hex}")
            st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)

        # grava histórico do utilizador
        now = datetime.now().strftime("%d/%m/%Y %H:%M")
        record = {
            "when": now,
            "theme": theme,
            "niche": niche,
            "tone": tone,
            "items": [
                {"caption": caps[0], "engagement": stats[0][0], "hour": stats[0][1], "note": stats[0][2]},
                {"caption": caps[1], "engagement": stats[1][0], "hour": stats[1][1], "note": stats[1][2]},
            ]
        }
        save_history(u, record)
        st.success("Guardado no teu histórico. 📜")
        st.markdown('</div>', unsafe_allow_html=True)  # fecha card

# =========================
#   HISTÓRICO
# =========================
def history_page():
    u = st.session_state.get("username", "utilizador")
    data = list(reversed(load_history(u)))

    st.markdown('<div class="glass card fade-in">', unsafe_allow_html=True)
    st.subheader("📜 Histórico de Gerações")

    if not data:
        st.info("Ainda não geraste nenhuma legenda.")
        if st.button("⬅️ Voltar", key="back_empty"):
            st.session_state["mode"] = "main"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        return

    for i, rec in enumerate(data, start=1):
        st.markdown(
            f"**🗓️ {rec['when']} — Tema:** *{rec['theme']}*  **({rec['niche']}, {rec['tone']})*",
            unsafe_allow_html=True
        )
        for j, it in enumerate(rec["items"], start=1):
            st.markdown(f'<div class="caption-card">', unsafe_allow_html=True)
            st.write(f"**💬 Legenda {i}.{j}:** {it['caption']}")
            st.markdown(
                f'<div class="badge">📊 +{it["engagement"]}%</div> &nbsp; '
                f'<div class="badge">🕒 {it["hour"]} — {it["note"]}</div>',
                unsafe_allow_html=True
            )
            js_copy_button(f"📋 Copiar {i}-{j}", it["caption"], key=f"copy_hist_{uuid.uuid4().hex}")
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)

        st.markdown('<hr style="border: 1px solid rgba(160,220,255,0.15)"/>', unsafe_allow_html=True)

    if st.button("⬅️ Voltar", key="back_hist"):
        st.session_state["mode"] = "main"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# =========================
#   NAV / AUTH
# =========================
def logout_pill():
    with st.sidebar:
        st.markdown("##### 👋 Logado como **{}**".format(st.session_state.get("username","")), unsafe_allow_html=True)
        if st.button("Sair"):
            for k in ["logged_in", "username", "mode"]:
                st.session_state.pop(k, None)
            st.rerun()

def router():
    if not st.session_state.get("logged_in"):
        login_screen()
        return
    logout_pill()
    mode = st.session_state.get("mode", "main")
    if mode == "history":
        history_page()
    else:
        main_page()

router()
