import os, io, datetime, json, base64, streamlit as st
from openai import OpenAI
from PIL import Image

st.set_page_config(page_title="AI Social Automator - Pro", page_icon="🚀")
st.title("🚀 AI Social Automator — Pro")
st.caption("Copy, Hashtags e Imagens com IA · Limite: 3 imagens/dia")

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.warning("⚠️ Adiciona a tua chave API do OpenAI em Settings → Secrets.")
    st.stop()

client = OpenAI(api_key=api_key)
USER_ID = st.text_input("📧 Identificação (email ou nome único):", placeholder="ex: miguel@exemplo.com")

MAX_IMAGES_PER_DAY = 3
USAGE_FILE = "user_usage.json"

def load_usage():
    if os.path.exists(USAGE_FILE):
        with open(USAGE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_usage(data):
    with open(USAGE_FILE, "w") as f:
        json.dump(data, f)

def can_generate(uid):
    data = load_usage()
    today = datetime.date.today().isoformat()
    if uid not in data:
        data[uid] = {"date": today, "count": 0}
    if data[uid]["date"] != today:
        data[uid] = {"date": today, "count": 0}
    if data[uid]["count"] >= MAX_IMAGES_PER_DAY:
        return False, MAX_IMAGES_PER_DAY - data[uid]["count"]
    return True, MAX_IMAGES_PER_DAY - data[uid]["count"]

def register_generation(uid):
    data = load_usage()
    today = datetime.date.today().isoformat()
    if uid not in data or data[uid]["date"] != today:
        data[uid] = {"date": today, "count": 0}
    data[uid]["count"] += 1
    save_usage(data)

tema = st.text_area("✍️ Tema do post:", placeholder="Ex.: Taça de açaí com frutas frescas e granola.")

tom = st.selectbox("🎯 Tom do texto", ["Profissional", "Neutro", "Descontraído", "Luxo", "Outro"])
if tom == "Outro":
    tom = st.text_input("✏️ Escreve o teu próprio tom de voz:")

nicho = st.selectbox("📌 Nicho", ["Geral", "Moda", "Fitness", "Restaurantes", "Beleza", "Tecnologia", "Outro"])
if nicho == "Outro":
    nicho = st.text_input("✏️ Escreve o teu próprio nicho:")

col1, col2 = st.columns(2)
gen_text = col1.button("🧠 Gerar Copy + Hashtags", use_container_width=True)
gen_img = col2.button("🎨 Gerar Imagem IA", use_container_width=True)

def gen_copy_tags(tema, tom, nicho):
    copy_prompt = f"Cria uma legenda curta e apelativa PT-PT para {tema}. Tom: {tom}. Nicho: {nicho}. Inclui hashtags no fim."
    r1 = client.chat.completions.create(model="gpt-4o-mini",
        messages=[{"role":"user","content":copy_prompt}]
    )
    return r1.choices[0].message.content.strip()

def gen_strategy(tema, nicho):
    strat_prompt = f"Cria 3 ideias de posts futuros em PT-PT com base neste tema: {tema}. Nicho: {nicho}. Formato: título - ideia curta."
    r2 = client.chat.completions.create(model="gpt-4o",
        messages=[{"role":"user","content":strat_prompt}]
    )
    return r2.choices[0].message.content.strip()

def gen_image(prompt):
    img = client.images.generate(model="gpt-image-1", prompt=prompt, size="1024x1024")
    raw = base64.b64decode(img.data[0].b64_json)
    return Image.open(io.BytesIO(raw))

if gen_text:
    if not tema.strip():
        st.warning("Escreve o tema primeiro!")
    else:
        with st.spinner("A gerar copy + hashtags..."):
            texto = gen_copy_tags(tema, tom, nicho)
            ideias = gen_strategy(tema, nicho)
        st.subheader("🧠 Legenda + Hashtags")
        st.write(texto)
        st.markdown("---")
        st.subheader("📅 Ideias de conteúdo")
        st.write(ideias)

if gen_img:
    if not USER_ID.strip():
        st.warning("⚠️ Escreve o teu email/nome antes de gerar imagens.")
    elif not tema.strip():
        st.warning("Escreve o tema primeiro!")
    else:
        allowed, left = can_generate(USER_ID)
        if not allowed:
            st.error(f"⚠️ Já usaste as tuas {MAX_IMAGES_PER_DAY} imagens hoje. Volta amanhã.")
        else:
            with st.spinner(f"A criar imagem... (restam {left} tentativas)"):
                image_prompt = f"{tema}, iluminação natural, fotografia profissional, 1:1, fundo limpo."
                img = gen_image(image_prompt)
                st.image(img, caption=f"Imagem gerada ({left} restantes hoje)", use_column_width=True)
                register_generation(USER_ID)
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                st.download_button("⬇️ Download PNG", buf.getvalue(), "post.png", "image/png", use_container_width=True)

st.caption("Plano PRO · Texto: GPT-4o-mini / Estratégia: GPT-4o / Imagens: GPT-image-1 · Limite 3 imagens/dia por conta · © 2025 AI Social Automator")
