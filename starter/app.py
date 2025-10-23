import streamlit as st
from shared.utils import (
    inject_css, login_card, logout_pill, get_client,
    engagement_and_time, add_history, get_history, copy_button
)
from datetime import datetime

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="AI Social Automator — Starter",
    page_icon="🤖",
    layout="centered"
)
inject_css()

# ---------------- LOGIN ----------------
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    login_card("AI Social Automator — Starter")
    st.stop()

logout_pill()
user = st.session_state.get("username", "")

# ---------------- UI ----------------
st.markdown('<div class="app-wrap">', unsafe_allow_html=True)
st.markdown('<h1 class="title-xl">Cria conteúdo que converte — em segundos.</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtle">2 legendas por geração, hashtags inteligentes e hora ideal de publicação.</p>', unsafe_allow_html=True)
st.write("")

col = st.container()
with col:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    theme = st.text_area("Tema do post", placeholder="Ex.: Nova coleção de outono, foco em elegância e conforto.")
    c1, c2 = st.columns(2)
    with c1:
        niche = st.selectbox("Nicho", ["Geral", "Moda", "Fitness", "Restaurantes", "Beleza", "Tecnologia"])
    with c2:
        tone = st.radio("Tom de voz", ["Neutro", "Inspirador"], horizontal=True)
    short = st.toggle("Versão curta (≤ 200 caracteres)", value=False)
    go = st.button("⚡ Gerar", type="primary", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

client = get_client()

# ---------------- FUNÇÃO DE GERAÇÃO ----------------
def gen_two(theme, niche, tone, short=False):
    sys = "És copywriter de social media. Responde em PT-PT. Máx 2 frases por legenda. Inclui 2–3 hashtags."
    limit = "Reduz a <=200 caracteres." if short else "Mantém natural, sem limite rígido."
    userp = f"Tema: {theme}\nNicho: {niche}\nTom: {tone}\nCria DUAS legendas curtas, distintas, com emojis e 2–3 hashtags.\n{limit}\nFormata como 1) ... 2) ..."
    r = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": sys}, {"role": "user", "content": userp}],
        temperature=0.7,
        max_tokens=260
    )
    text = r.choices[0].message.content.strip()
    parts = [ln[2:].strip(": ").strip() for ln in text.splitlines() if ln[:2] in ("1)", "2)")]
    if len(parts) < 2:
        half = len(text)//2
        parts = [text[:half].strip(), text[half:].strip()]
    return parts[:2]

# ---------------- EXECUÇÃO ----------------
if go:
    if not theme.strip():
        st.warning("Escreve o tema primeiro.")
    else:
        with st.spinner("A criar duas opções de legenda…"):
            caps = gen_two(theme, niche, tone, short)
            stats = [engagement_and_time() for _ in range(2)]

        st.markdown("### 🧠 Legendas sugeridas")
        for i, cap in enumerate(caps, start=1):
            pct, hr, note = stats[i-1]
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.write(f"**{i}.** {cap}")
            st.markdown(
                f'<div class="badge">📈 Engajamento estimado: +{pct}%</div> &nbsp;'
                f'<span class="badge">🕒 {hr} — {note}</span>',
                unsafe_allow_html=True
            )
            copy_button(f"📋 Copiar {i}", cap)
            st.markdown('</div>', unsafe_allow_html=True)

        add_history(user, {
            "when": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "theme": theme, "niche": niche, "tone": tone,
            "items": [
                {"caption": caps[0], "engagement": stats[0][0], "hour": stats[0][1], "note": stats[0][2]},
                {"caption": caps[1], "engagement": stats[1][0], "hour": stats[1][1], "note": stats[1][2]},
            ]
        })
        st.success("Guardado no teu histórico.")

# ---------------- HISTÓRICO ----------------
st.markdown("### 📜 Histórico")
hist = list(reversed(get_history(user)))
if not hist:
    st.caption("Sem histórico ainda.")
else:
    for i, rec in enumerate(hist[:10], start=1):
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.write(f"**{rec['when']}** — *{rec['theme']}*  ({rec['niche']}, {rec['tone']})")
        for j, it in enumerate(rec["items"], start=1):
            st.write(f"**{i}.{j}** {it['caption']}")
            st.caption(f"📊 +{it['engagement']}% · 🕒 {it['hour']} — {it['note']}")
            copy_button(f"📋 Copiar {i}.{j}", it["caption"])
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
