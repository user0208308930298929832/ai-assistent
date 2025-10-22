import streamlit as st
from openai import OpenAI
import os

st.set_page_config(page_title="AI Social Automator - Starter", page_icon="🤖")

st.title("🤖 AI Social Automator — Starter")
st.caption("Cria legendas e hashtags em segundos com IA 🚀")

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.warning("⚠️ Adiciona a tua chave API do OpenAI em Settings → Secrets.")
    st.stop()

client = OpenAI(api_key=api_key)

tema = st.text_area("✍️ Escreve o tema do post:", placeholder="Ex.: Novo casaco de outono, foco em elegância e conforto.")

st.markdown("🎯 **Ajuste de tom disponível a partir do plano PRO** 🔒")
nicho = st.selectbox("📌 Nicho", ["Geral", "Moda", "Fitness", "Restaurantes", "Beleza", "Tecnologia"])

if st.button("⚡ Gerar Conteúdo", use_container_width=True):
    if not tema.strip():
        st.warning("Escreve o tema primeiro!")
    else:
        with st.spinner("A criar o teu conteúdo..."):
            prompt = f"Cria uma legenda curta e criativa em PT-PT sobre: {tema}. Nicho: {nicho}. Inclui 3 hashtags no fim."
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            )
            texto = response.choices[0].message.content
        st.subheader("🧠 Resultado")
        st.write(texto)
        st.success("Feito! 🎉")

st.caption("Plano Starter · Modelo: GPT-4o-mini · © 2025 AI Social Automator")
