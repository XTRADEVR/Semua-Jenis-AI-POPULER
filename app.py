import streamlit as st, json
from pathlib import Path
from PIL import Image
from google import genai

st.set_page_config(page_title="SEMUA JENIS AI", page_icon="🤖", layout="wide")

st.markdown("""
<style>
.kategori {
  background: linear-gradient(135deg, #1e1e3f, #2a2a5a);
  border-radius: 16px; padding: 16px; margin-bottom: 18px; border: 1px solid #3a3a6a;
}
.kategori h4 {
  margin:0 0 12px 0; color: #fbbf24; font-size: 14px;
  background: rgba(0,0,0,0.3); padding: 6px 12px; border-radius: 20px; display: inline-block;
}
.badge {
  display: inline-block; background: #0f0f2a; border: 1px solid #4a4a7a;
  color: #e0e0ff; padding: 6px 12px; border-radius: 20px;
  font-size: 12px; margin: 4px 4px; text-decoration: none !important;
}
.badge:hover {background: #6366f1; color:white;}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; font-weight:900'>SEMUA JENIS <span style='color:#a78bfa'>AI</span></h1>", unsafe_allow_html=True)
st.markdown("<div style='text-align:center; background:#6366f1; color:white; padding:10px; border-radius:30px; font-weight:800; margin-bottom:20px'>SEMUA AI POPULER DALAM SATU GAMBAR - KLIK UNTUK BUKA</div>", unsafe_allow_html=True)

json_path = Path(__file__).parent / "ai_tools.json"
with open(json_path, "r", encoding="utf-8") as f:
    db = json.load(f)

tab1, tab2 = st.tabs(["📚 POSTER LENGKAP 189 TOOLS", "💬 CHAT AI + GAMBAR DI BAWAH"])

with tab1:
    col1, col2 = st.columns(2)
    for idx, kat in enumerate(db["data"]):
        target = col1 if idx % 2 == 0 else col2
        with target:
            badges_html = "".join([f"<a class='badge' href='{t['url']}' target='_blank'>🔗 {t['name']}</a>" for t in kat["tools"]])
            st.markdown(f"<div class='kategori'><h4>{kat['kategori']}</h4><div>{badges_html}</div></div>", unsafe_allow_html=True)

with tab2:
    st.subheader("Chat baru - Gemini 3.8 Flash & 3.5 Flash-Lite")
    api_key = st.secrets.get("GEMINI_API_KEY") if "GEMINI_API_KEY" in st.secrets else st.sidebar.text_input("GEMINI_API_KEY", type="password")
    if not api_key: st.stop()

    client = genai.Client(api_key=api_key)
    if "messages" not in st.session_state: st.session_state.messages = []
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.write(m["content"])
            if m.get("image"): st.image(m["image"], width=250)

    prompt = st.chat_input("Tanya apa saja...")
    st.markdown("---")
    st.markdown("**📷 Kirim gambar (opsional) - di bawah chat**")
    uploaded = st.file_uploader("Upload", type=["jpg","jpeg","png"], label_visibility="collapsed")
    img_preview = Image.open(uploaded) if uploaded else None
    if img_preview: st.image(img_preview, width=320)

    if prompt:
        st.session_state.messages.append({"role":"user","content":prompt,"image":img_preview})
        with st.chat_message("user"):
            st.write(prompt)
            if img_preview: st.image(img_preview, width=250)
        with st.chat_message("assistant"):
            if img_preview:
                res = client.models.generate_content(model="gemini-3.8-flash", contents=[prompt, img_preview])
            else:
                res = client.models.generate_content(model="gemini-3.5-flash-lite", contents=prompt)
            st.write(res.text)
