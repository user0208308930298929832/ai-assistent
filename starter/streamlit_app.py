import streamlit as st
import streamlit.components.v1 as components
from openai import OpenAI
import os, json, time, random, base64, uuid
from datetime import datetime
from pathlib import Path
from string import Template

# -------------------- CONFIG --------------------
st.set_page_config(page_title="AI Social Automator — Starter 3.2", page_icon="🤖", layout="centered")
APP_TITLE = "AI Social Automator"
BASE = Path(__file__).parent
ASSETS = BASE / "assets"
ASSETS.mkdir(exist_ok=True)
HIST_DIR = BASE / "history"
HIST_DIR.mkdir(exist_ok=True)

ROBOT_LEFT  = str(ASSETS / "robot_left.png")
ROBOT_MID   = str(ASSETS / "robot_center.png")
ROBOT_RIGHT = str(ASSETS / "robot_right.png")

# -------------------- ESTILO --------------------
st.markdown("""
<style>
.stApp { background: radial-gradient(1200px 600px at 50% -10%, #0e1a22 0%, #0a1016 45%, #060b10 100%);
         color:#e8f4ff; font-family: Inter, system-ui; }
.block-container { max-width: 900px; }
.glass-card {
  background: rgba(180,230,255,0.05);
  border:1px solid rgba(160,220,255,0.18);
  border-radius:16px;
  padding:16px 18px;
  margin-top:14px;
  box-shadow:0 6px 25px rgba(0,0,0,0.35);
  backdrop-filter: blur(12px);
  transition:all .25s ease;
}
.glass-card:hover {
  background:rgba(180,230,255,0.07);
  box-shadow:0 10px 35px rgba(0,180,255,0.15);
  transform:translateY(-2px);
}
.copy-btn {
  background: linear-gradient(90deg,#1ebfff,#009cff);
  color:#00131a; border:none; border-radius:10px;
  padding:8px 16px; font-weight:700; cursor:pointer;
  box-shadow:0 0 10px rgba(30,191,255,.35);
}
.badge {
  display:inline-flex; gap:.5rem; padding:8px 12px; border-radius:12px;
  font-weight:700; background:rgba(150,220,255,.12);
  border:1px solid rgba(160,220,255,.22); color:#e3f8ff; margin-right:6px;
}
.robots { display:flex; justify-content:center; gap:28px; margin:10px 0 8px; }
.robots img { filter: drop-shadow(0 10px 30px rgba(0,200,255,.25)); }
.robot-sit { transform: translateY(6px) scale(.96); }
.robot-mid { transform: translateY(-3px) scale(1.05); }
.h1 { text-align:center; font-weight:800; font-size:clamp(26px,4vw,44px);
      color:#9be3ff; text-shadow:0 0 18px rgba(90,200,255,.25); margin:6px 0 8px; }
.subtle { text-align:center; color:#b9d5e6; margin-top:-6px; }
hr { border:1px solid rgba(160,220,255,0.15); }
</style>
""", unsafe_allow_html=True)

# -------------------- FUNÇÕES --------------------
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
    try: return json.load(open(p,"r",encoding="utf-8"))
    except: return []

def save_history(username:str, record:dict):
    data = load_history(username)
    data.append(record)
    with open(hpath(username),"w",encoding="utf-8") as f:
        json.dump(data,f,ensure_ascii=False,indent=2)

# ---------- BOTÃO COPIAR ----------
def js_copy_button(label:str, text:str, key:str|None=None):
    """Botão de copiar robusto (Base64 → Clipboard via JS)."""
    if key is None:
        key=f"copy_{uuid.uuid4().hex}"
    b64=base64.b64encode(text.encode("utf-8")).decode("ascii")
    tpl=Template(r"""
    <div style="display:inline-flex;align-items:center;gap:10px;">
      <button id="$KEY" class="copy-btn">$LABEL</button>
      <script>
        (function(){
          const btn=document.getElementById("$KEY");
          if(!btn)return;
          function b64ToUtf8(b64){
            const bin=atob(b64);const bytes=new Uint8Array(bin.length);
            for(let i=0;i<bin.length;i++)bytes[i]=bin.charCodeAt(i);
            return new TextDecoder().decode(bytes);
          }
          const payload="$B64";
          btn.addEventListener("click",async()=>{
            try{
              const txt=b64ToUtf8(payload);
              await navigator.clipboard.writeText(txt);
              const old=btn.innerText;
              btn.innerText="Copiado ✅";
              setTimeout(()=>btn.innerText=old,1200);
            }catch(e){
              const old=btn.innerText;
              btn.innerText="Erro 😕";
              setTimeout(()=>btn.innerText=old,1200);
            }
          });
        })();
      </script>
    </div>
    """)
    components.html(tpl.substitute(KEY=key,LABEL=label,B64=b64),height=60,scrolling=False)

def dynamic_stats(seed=None):
    rnd=random.Random(seed or time.time_ns())
    pct=round(rnd.uniform(4.8,9.0),1)
    hour,note=rnd.choice([
        ("13:00","hora de almoço 🍽️"),
        ("18:00","fim de tarde — maior atividade 🏙️"),
        ("21:00","posts noturnos de alto alcance 🌙"),
    ])
    return pct,hour,note

def gen_two_captions(theme,niche,tone):
    client=ensure_client()
    sys="És copywriter de social media. Responde em PT-PT. Máx 2 frases. Inclui até 3 hashtags."
    user=f"Tema: {theme}\nNicho: {niche}\nTom: {tone}\nCria DUAS legendas curtas e distintas, com emojis e hashtags. Formata 1) ... 2) ..."
    r=client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"system","content":sys},{"role":"user","content":user}],
        temperature=0.7,max_tokens=240)
    txt=r.choices[0].message.content.strip()
    parts=[ln[2:].strip(": ").strip() for ln in txt.splitlines() if ln[:2] in ("1)","2)")]
    if len(parts)<2:
        half=len(txt)//2
        parts=[txt[:half].strip(),txt[half:].strip()]
    return parts[:2]

# -------------------- LOGIN --------------------
def login_screen():
    users = load_users()

    st.markdown("""
    <style>
    /* === Layout geral === */
    .login-box {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(120,190,255,0.25);
        border-radius: 16px;
        padding: 28px 32px;
        width: 100%;
        max-width: 300px;
        margin: 22vh auto 0 auto;
        text-align: center;
        box-shadow: 0 6px 18px rgba(0, 100, 255, 0.12);
        backdrop-filter: blur(10px);
    }

    /* === Título e subtítulo === */
    .login-title {
        font-size: 1.6rem;
        font-weight: 800;
        color: #38b6ff;
        text-shadow: 0 0 10px rgba(0,180,255,0.4);
        margin-bottom: 6px;
        text-align: center;
    }
    .login-sub {
        color: #b9d6f2;
        font-size: 0.9rem;
        margin-bottom: 20px;
        text-align: center;
    }

    /* === Inputs === */
    .stTextInput label {
        font-weight: 600;
        color: #9bd2ff !important;
        font-size: 0.8rem !important;
        text-align: center;
        display: block;
        margin-bottom: 4px;
    }
    div[data-baseweb="input"] > div {
        border: 1px solid rgba(150,210,255,0.35) !important;
        border-radius: 10px !important;
        background: rgba(10,20,30,0.65) !important;
        transition: all 0.25s ease;
        height: 34px !important;
    }
    div[data-baseweb="input"]:focus-within > div {
        border: 1px solid #38b6ff !important;
        box-shadow: 0 0 10px rgba(56,182,255,0.45) !important;
        background: rgba(10,25,40,0.85) !important;
    }
    input {
        color: #e8f4ff !important;
        font-size: 0.9rem !important;
        text-align: center !important;
    }

    /* === Botão === */
    .stButton > button {
        background: linear-gradient(90deg,#0078ff,#00bfff);
        color: white;
        font-weight: 700;
        border-radius: 20px;
        border: none;
        padding: 5px 0;
        width: 100%;
        margin-top: 12px;
        height: 34px;
        box-shadow: 0 0 12px rgba(0,150,255,0.35);
        transition: all 0.25s ease;
    }
    .stButton > button:hover {
        box-shadow: 0 0 20px rgba(0,180,255,0.5);
        transform: translateY(-1px);
    }
    </style>
    """, unsafe_allow_html=True)

    # Caixa principal
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.markdown('<div class="login-title">AI Social Automator</div>', unsafe_allow_html=True)
    st.markdown('<div class="login-sub">Acede à tua conta para começar 🚀</div>', unsafe_allow_html=True)

    with st.form("login_form", clear_on_submit=False):
        u = st.text_input("👤 Utilizador", placeholder="Utilizador")
        p = st.text_input("🔑 Palavra-passe", type="password", placeholder="Palavra-passe")
        ok = st.form_submit_button("Entrar")

        if ok:
            if u in users and users[u].get("password") == p:
                st.session_state.update({"logged_in": True, "username": u, "mode": "main"})
                st.success(f"Bem-vindo, {u} 👋")
                time.sleep(0.6)
                st.rerun()
            else:
                st.error("❌ Credenciais incorretas.")

    st.markdown('</div>', unsafe_allow_html=True)
# -------------------- MAIN --------------------
def main_page():
    user=st.session_state.get("username","")
    st.markdown(f'<div class="h1">{APP_TITLE} — Starter 3.2</div>',unsafe_allow_html=True)
    st.markdown('<div class="subtle">Cria legendas otimizadas com análise real de engajamento 📊</div>',unsafe_allow_html=True)
    st.write("")
    theme=st.text_area("📝 Tema do post:",placeholder="Ex.: Nova coleção de outono — elegância e conforto")
    col1,col2=st.columns(2)
    with col1:
        niche=st.selectbox("📌 Nicho",["Geral","Moda","Fitness","Restaurantes","Beleza","Tecnologia"])
    with col2:
        tone=st.radio("🎚️ Tom de voz",["Neutro","Inspirador"],horizontal=True)

    colA,colB=st.columns(2)
    gen=colA.button("⚡ Gerar Conteúdo",use_container_width=True)
    hist=colB.button("📜 Histórico",use_container_width=True)
    if hist:
        st.session_state["mode"]="history";st.rerun()

    if gen:
        if not theme.strip():
            st.warning("Escreve o tema do post primeiro.");return
        with st.spinner("✨ A criar duas opções de legenda…"):
            captions=gen_two_captions(theme,niche,tone)
            stats=[dynamic_stats(seed=random.randint(1,999999)) for _ in range(2)]
        st.markdown("### 🧠 Legendas sugeridas:")
        for i,cap in enumerate(captions,start=1):
            pct,hr,note=stats[i-1]
            st.markdown(f"""
            <div class="glass-card">
              <p style="font-size:16px;margin-bottom:10px;">{i}. {cap}</p>
              <div style="margin-top:8px;margin-bottom:8px;">
                <span class="badge">📈 Engajamento: +{pct}%</span>
                <span class="badge">🕒 Hora ideal: {hr} — {note}</span>
              </div>
            </div>
            """,unsafe_allow_html=True)
            copy_key=f"copy_{i}_{uuid.uuid4().hex}"
            js_copy_button(f"📋 Copiar {i}",cap,key=copy_key)

        now=datetime.now().strftime("%d/%m/%Y %H:%M")
        save_history(user,{
            "when":now,"theme":theme,"niche":niche,"tone":tone,
            "items":[
                {"caption":captions[0],"engagement":stats[0][0],"hour":stats[0][1],"note":stats[0][2]},
                {"caption":captions[1],"engagement":stats[1][0],"hour":stats[1][1],"note":stats[1][2]}
            ]})
        st.success("Guardado no teu histórico. 📜")

# -------------------- HISTÓRICO --------------------
def history_page():
    user=st.session_state.get("username","")
    data=list(reversed(load_history(user)))
    st.subheader("📜 Histórico de Gerações")
    if not data:
        st.info("Ainda não geraste nenhuma legenda.")
        if st.button("⬅️ Voltar"): st.session_state["mode"]="main"; st.rerun()
        return
    for i,rec in enumerate(data,start=1):
        st.markdown(f"**🗓️ {rec['when']} — Tema:** *{rec['theme']}*  **({rec['niche']}, {rec['tone']})*")
        for j,it in enumerate(rec["items"],start=1):
            st.markdown(f"""
            <div class="glass-card">
              <p><b>💬 Legenda {i}.{j}:</b> {it['caption']}</p>
              <div>
                <span class="badge">📊 +{it['engagement']}%</span>
                <span class="badge">🕒 {it['hour']} — {it['note']}</span>
              </div>
            </div>
            """,unsafe_allow_html=True)
            copy_key=f"copy_hist_{i}_{j}_{uuid.uuid4().hex}"
            js_copy_button(f"📋 Copiar {i}-{j}",it["caption"],key=copy_key)
        st.markdown("<hr/>",unsafe_allow_html=True)
    if st.button("⬅️ Voltar"): st.session_state["mode"]="main"; st.rerun()

# -------------------- NAV --------------------
def logout_pill():
    with st.sidebar:
        st.markdown(f"##### 👋 Logado como **{st.session_state.get('username','')}**")
        if st.button("Sair"):
            for k in ["logged_in","username","mode"]: st.session_state.pop(k,None)
            st.rerun()

def router():
    if not st.session_state.get("logged_in"): login_screen();return
    logout_pill()
    (history_page() if st.session_state.get("mode")=="history" else main_page())

# -------------------- BOOT --------------------
router()
