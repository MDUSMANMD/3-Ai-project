import streamlit as st
import io, os, requests, base64
import PyPDF2
from dotenv import load_dotenv
from docx import Document
import pandas as pd

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

load_dotenv()
API_KEY = os.getenv("NVIDIA_API_KEY")

st.set_page_config(page_title="NovaMind AI", layout="wide")

# ---------- UI ----------
st.markdown("""
<style>
.stApp {background:#1e1e1e; color:white;}
.box {background:rgba(255,255,255,0.05); padding:20px; border-radius:12px;}
</style>
""", unsafe_allow_html=True)

st.sidebar.title("🚀 NovaMind AI")

mode = st.sidebar.radio(
    "Select Module",
    ["🎓 Education", "💼 Career", "💰 Finance", "📄 Analyzer", "📊 Dashboard"]
)

# ---------- SESSION ----------
if "memory" not in st.session_state:
    st.session_state.memory = {"Education":[], "Career":[], "Finance":[], "Analyzer":[]}

if "usage" not in st.session_state:
    st.session_state.usage = []

# ---------- CACHE ----------
@st.cache_data(show_spinner=False)
def cached_ai(prompt):
    return call_ai(prompt)

# ---------- AI ----------
def call_ai(prompt):
    url = "https://integrate.api.nvidia.com/v1/chat/completions"

    headers = {"Authorization": f"Bearer {API_KEY}"}

    data = {
        "model":"deepseek-ai/deepseek-v3.2",
        "messages":[{"role":"user","content":prompt}],
        "max_tokens":250  # ⚡ FAST
    }

    try:
        res = requests.post(url, headers=headers, json=data, timeout=15)
        if res.status_code != 200:
            return "API Error"
        return res.json()["choices"][0]["message"]["content"]
    except:
        return "Timeout / Error"


# ---------- FILE ----------
def read_file(file):
    if not file: return ""
    if "pdf" in file.type:
        reader = PyPDF2.PdfReader(file)
        return "".join([p.extract_text() or "" for p in reader.pages])
    elif "word" in file.type:
        doc = Document(file)
        return "\n".join([p.text for p in doc.paragraphs])
    elif "image" in file.type:
        return base64.b64encode(file.read()).decode()
    else:
        return file.read().decode(errors="ignore")

# ---------- PDF ----------
def pdf_download(text):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf)
    styles = getSampleStyleSheet()
    elements = []
    for line in text.split("\n"):
        elements.append(Paragraph(line, styles["Normal"]))
        elements.append(Spacer(1,10))
    doc.build(elements)
    buf.seek(0)
    return buf

# ---------- MEMORY ----------
def memory_chat(module, user_input):
    history = "\n".join(st.session_state.memory[module][-3:])
    prompt = f"{history}\nUser:{user_input}"

    response = cached_ai(prompt)  # ⚡ cached

    st.session_state.memory[module].append(f"User:{user_input}")
    st.session_state.memory[module].append(f"AI:{response}")

    return response

# ---------- CHAT ----------
def chatbot(module):
    st.markdown("### 💬 Chat with AI")
    q = st.text_input("Ask anything")

    if st.button("Ask AI"):
        if q:
            res = memory_chat(module, q)
            st.write(res)

# ============================================================
# 🎓 EDUCATION
# ============================================================
if mode == "🎓 Education":
    st.header("🎓 Education AI")

    file = st.file_uploader("Upload", type=["pdf","docx","txt","png","jpg"])
    q = st.text_area("Ask")

    if st.button("Get Answer"):
        content = read_file(file)
        res = memory_chat("Education", content + q)
        st.write(res)
        st.download_button("Download PDF", pdf_download(res))
        st.session_state.usage.append("Education")

    chatbot("Education")

# ============================================================
# 💼 CAREER
# ============================================================
elif mode == "💼 Career":
    st.header("💼 Career AI")

    file = st.file_uploader("Upload", type=["pdf","docx","txt","png","jpg"])
    role = st.text_input("Role")

    if st.button("Analyze"):
        res = memory_chat("Career", role + read_file(file))
        st.write(res)
        st.session_state.usage.append("Career")

    chatbot("Career")

# ============================================================
# 💰 FINANCE
# ============================================================
elif mode == "💰 Finance":
    st.header("💰 Finance AI")

    file = st.file_uploader("Upload", type=["pdf","txt","png","jpg"])
    q = st.text_area("Ask")

    if st.button("Get Advice"):
        res = memory_chat("Finance", read_file(file) + q)
        st.write(res)
        st.session_state.usage.append("Finance")

    chatbot("Finance")

# ============================================================
# 📄 ANALYZER
# ============================================================
elif mode == "📄 Analyzer":
    st.header("📄 Analyzer AI")

    file = st.file_uploader("Upload", type=["pdf","docx","txt","png","jpg"])

    if st.button("Analyze"):
        res = memory_chat("Analyzer", read_file(file))
        st.write(res)
        st.download_button("Download PDF", pdf_download(res))
        st.session_state.usage.append("Analyzer")

    chatbot("Analyzer")

# ============================================================
# 📊 DASHBOARD
# ============================================================
elif mode == "📊 Dashboard":
    st.header("📊 Advanced Analytics Dashboard")

    if st.session_state.usage:
        df = pd.DataFrame(st.session_state.usage, columns=["Feature"])
        counts = df["Feature"].value_counts()

        st.bar_chart(counts)
        st.write(counts)
        st.metric("Total Usage", len(st.session_state.usage))
    else:
        st.info("No usage yet")

# ---------- FOOTER ----------
st.markdown("---")
st.markdown("<center>👨‍💻 Created by <b>MOHAMMED.USMAN</b></center>", unsafe_allow_html=True)