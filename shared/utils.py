import os, json, base64, uuid, time, random
from pathlib import Path
from datetime import datetime, timezone
import streamlit as st
import streamlit.components.v1 as components
from string import Template
from openai import OpenAI

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "history"
DATA.mkdir(exist_ok=True)

USERS_PATH = BASE / "users.json"

# ---------- Estilo global (branco clean)
def inject_css():
    st.markdown("""
    <style>
    .app-wrap { max-width: 980px; margin: 0 auto; }
    .card { background:#fff; border:1px solid #e9eef5; border-radius:16px; padding:22px;
            box-shadow:0 4px 16px rgba(14,30,37,0.06); }
    .card:hover { box-shadow:0 10px 28px rgba(14,30,37,0.10); transition:.2s; }
    .title-xl { font-weight:800; letter-spacing:-.02em; font-size:clamp(26px,4vw,40px); margin:6px 0; }
    .subtle { color:#5b6b7d; margin-top:-6px; }
    .badge { display:inline-flex; align-items:center; gap:.5rem; padding:6px 10px; border:1px solid #e5eef8;
             border-radius:999px; background:#f6f9fc; color:#0b1220; font-weight:700; }
    .copy-btn { background: linear-gradient(90deg,#0078ff,#00bfff); color:#fff; border:none; border-radius:10px;
                padding:8px 14px; font-weight:700; cursor:pointer; box-shadow:0 6px 18px rgba(0,120,255,.25); }
    .muted { color:#7c8da0; }
    .grid-2 { display:grid; grid-template-columns:1fr 1fr; gap:16px; }
    @media (max-width: 780px){ .grid-2{ grid-template-columns:1fr; } }
    .smallhint{ font-size:.9rem; color:#6b7a8c; }
    </style>
    """, unsafe_allow_html=True)

# ---------- OpenAI
def get_client():
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        st.error("OPENAI_API_KEY não configurada (Settings → Secrets).")
        st.stop()
    return OpenAI(api_key=key)

# ---------- Auth
def load_users():
    with open(USERS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def login_card(title="AI Social Automator"):
    users = load_users()
    st.markdown('<div class="app-wrap">', unsafe_allow_html=True)
    st.markdown(f'<h1 class="title-xl" style="text-align:center;color:#0078ff;">{title}</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtle" style="text-align:center;">Acede à tua conta para começar 🚀</p>', unsafe_allow_html=True)
    st.write("")
    with st.form("login", clear_on_submit=False):
        st.markdown('<div class="card">', unsafe_allow_html=True)
        u = st.text_input("", placeholder="Utilizador")
        p = st.text_input("", type="password", placeholder="Palavra-passe")
        ok = st.form_submit_button("Entrar", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    if ok:
        if u in users and users[u].get("password") == p:
            st.session_state.update({"logged_in": True, "username": u, "plan": users[u].get("plan","starter")})
            st.success(f"Bem-vindo, {u} 👋"); st.rerun()
        else:
            st.error("❌ Credenciais incorretas.")

def logout_pill():
    with st.sidebar:
        st.caption(f"👤 {st.session_state.get('username','')}")
        if st.button("Sair"):
            for k in ["logged_in","username","plan"]: st.session_state.pop(k, None)
            st.rerun()

# ---------- Histórico por utilizador
def _hpath(user:str) -> Path:
    return DATA / f"{user}.json"

def get_history(user:str):
    p = _hpath(user)
    if not p.exists(): return []
    try:
        return json.load(open(p, "r", encoding="utf-8"))
    except:
        return []

def add_history(user:str, record:dict):
    data = get_history(user)
    data.append(record)
    with open(_hpath(user), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ---------- Botão copiar (robusto)
def copy_button(label:str, text:str, key:str|None=None):
    import streamlit.components.v1 as components
    if key is None: key = f"copy_{uuid.uuid4().hex}"
    b64 = base64.b64encode(text.encode("utf-8")).decode("ascii")
    tpl = Template(r"""
    <div style="display:inline-flex;align-items:center;gap:10px;">
      <button id="$KEY" class="copy-btn">$LABEL</button>
      <script>
      (function(){
        const btn=document.getElementById("$KEY"); if(!btn)return;
        function b64ToUtf8(b64){ const bin=atob(b64); const bytes=new Uint8Array(bin.length);
          for(let i=0;i<bin.length;i++)bytes[i]=bin.charCodeAt(i);
          return new TextDecoder().decode(bytes); }
        const payload="$B64";
        btn.addEventListener("click", async ()=>{
          try{ const txt=b64ToUtf8(payload); await navigator.clipboard.writeText(txt);
               const old=btn.innerText; btn.innerText="Copiado ✅"; setTimeout(()=>btn.innerText=old,1100); }
          catch(e){ const old=btn.innerText; btn.innerText="Erro 😕"; setTimeout(()=>btn.innerText=old,1100); }
        });
      })();
      </script>
    </div>
    """)
    components.html(tpl.substitute(KEY=key, LABEL=label, B64=b64), height=52, scrolling=False)

# ---------- Heurísticas
def engagement_and_time(seed=None):
    rnd = random.Random(seed or time.time_ns())
    pct = round(rnd.uniform(4.8, 9.2), 1)
    hour, note = rnd.choice([
        ("12:30", "almoço — picos de scroll"),
        ("18:00", "fim de tarde — alta atividade"),
        ("21:00", "noite — bom alcance")
    ])
    return pct, hour, note

# ---------- Limites de imagem por utilizador/dia
def check_and_increment_image_quota(user:str, limit_per_day:int=3) -> tuple[bool,int]:
    """Retorna (permitido, restantes)."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    qpath = DATA / f"{user}_quota.json"
    data = {}
    if qpath.exists():
        try: data = json.load(open(qpath, "r", encoding="utf-8"))
        except: data = {}
    used = data.get(today, 0)
    if used >= limit_per_day:
        return False, 0
    data[today] = used + 1
    with open(qpath, "w", encoding="utf-8") as f:
        json.dump(data, f)
    return True, max(0, limit_per_day - data[today])
