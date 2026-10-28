import streamlit as st
import json
from pathlib import Path
from PIL import Image
from google import genai

st.set_page_config(page_title="SEMUA JENIS AI", page_icon="🤖", layout="wide")

# HEADER
st.markdown("<h1 style='text-align:center'>SEMUA JENIS <span style='color:#a855f7'>AI</span></h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; background:#6366f1; color:white; padding:8px; border-radius:20px; font-weight:bold'>SEMUA AI POPULER DALAM SATU GAMBAR - KLIK UNTUK BUKA</p>", unsafe_allow_html=True)

# LOAD JSON
json_path = Path(__file__).parent / "ai_tools.json"
with open(json_path, "r", encoding="utf-8") as f:
    db = json.load(f)

# poster asli jika ada
poster_path = Path(__file__).parent / "poster.jpg"
if poster_path.exists():
    st.image(str(poster_path), use_container_width=True)

tab1, tab2 = st.tabs(["📚 56+ AI TOOLS (Bisa Dikklik)", "💬 CHAT AI + GAMBAR DI BAWAH"])

with tab1:
    for kat in db["data"]:
        st.markdown(f"#### {kat['kategori']}")
        cols = st.columns(4)
        for idx, tool in enumerate(kat["tools"]):
            name = tool["name"] if isinstance(tool, dict) else tool
            url = tool["url"] if isinstance(tool, dict) else f"https://www.google.com/search?q={name}"
            with cols[idx % 4]:
                st.link_button(f"🔗 {name}", url, use_container_width=True)
        st.divider()

with tab2:
    st.subheader("Chat baru - Gemini 3.8 Flash & 3.5 Flash-Lite")
    api_key = st.secrets.get("GEMINI_API_KEY") if "GEMINI_API_KEY" in st.secrets else st.sidebar.text_input("Masukkan GEMINI_API_KEY", type="password")
    if not api_key:
        st.warning("Masukkan GEMINI_API_KEY di sidebar atau di Secrets")
        st.stop()

    client = genai.Client(api_key=api_key)
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.write(m["content"])
            if m.get("image") is not None:
                st.image(m["image"], width=250)

    prompt = st.chat_input("Tanya apa saja...")

    # GAMBAR DOANG DI BAWAH CHAT AI
    st.markdown("---")
    st.markdown("**📷 Kirim gambar (opsional) - di bawah chat**")
    uploaded_file = st.file_uploader("Upload gambar", type=["jpg","jpeg","png"], label_visibility="collapsed")
    
    img_preview = None
    if uploaded_file:
        img_preview = Image.open(uploaded_file)
        st.image(img_preview, caption="Preview - akan dikirim bersama chat", width=350)

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt, "image": img_preview})
        with st.chat_message("user"):
            st.write(prompt)
            if img_preview:
                st.image(img_preview, width=250)

        with st.chat_message("assistant"):
            with st.spinner("Gemini 3.8 lagi mikir..."):
                if img_preview:
                    response = client.models.generate_content(model="gemini-3.8-flash", contents=[prompt, img_preview])
                else:
                    response = client.models.generate_content(model="gemini-3.5-flash-lite", contents=prompt)
                st.write(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text, "image": None})
