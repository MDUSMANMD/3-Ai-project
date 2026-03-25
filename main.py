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
.box {
    background: rgba(255,255,255,0.05);
    padding:20px;
    border-radius:12px;
}
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

# ---------- FUNCTIONS ----------
def call_ai(prompt):
    url = "https://integrate.api.nvidia.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    data = {
        "model":"deepseek-ai/deepseek-v3.2",
        "messages":[{"role":"user","content":prompt}],
        "max_tokens":500  # 🔥 faster
    }

    try:
        with st.spinner("🤖 AI is thinking..."):
            res = requests.post(url, headers=headers, json=data, timeout=20)

        if res.status_code != 200:
            return "API Error"

        return res.json()["choices"][0]["message"]["content"]

    except:
        return "Request Timeout / Error"


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


def memory_chat(module, user_input):
    history = "\n".join(st.session_state.memory[module][-4:])
    prompt = f"{history}\nUser:{user_input}"

    response = call_ai(prompt)

    st.session_state.memory[module].append(f"User:{user_input}")
    st.session_state.memory[module].append(f"AI:{response}")

    return response


# ============================================================
# 🎓 EDUCATION
# ============================================================
if mode == "🎓 Education":

    st.header("🎓 Education AI")

    file = st.file_uploader("Upload Notes", type=["pdf","docx","txt","png","jpg"])
    q = st.text_area("Ask Question")

    if st.button("Get Answer"):
        content = read_file(file)
        result = memory_chat("Education", content + "\n" + q)
        st.write(result)
        st.download_button("Download PDF", pdf_download(result))
        st.session_state.usage.append("Education")


# ============================================================
# 💼 CAREER
# ============================================================
elif mode == "💼 Career":

    st.header("💼 Career AI")

    file = st.file_uploader("Upload Resume", type=["pdf","docx","txt","png","jpg"])
    role = st.text_input("Target Role")

    if st.button("Analyze"):
        content = read_file(file)
        result = memory_chat("Career", role + "\n" + content)
        st.write(result)
        st.session_state.usage.append("Career")


# ============================================================
# 💰 FINANCE
# ============================================================
elif mode == "💰 Finance":

    st.header("💰 Finance AI")

    file = st.file_uploader("Upload Data", type=["pdf","txt","png","jpg"])
    q = st.text_area("Ask Question")

    if st.button("Get Advice"):
        content = read_file(file)
        result = memory_chat("Finance", content + "\n" + q)
        st.write(result)
        st.session_state.usage.append("Finance")


# ============================================================
# 📄 ANALYZER
# ============================================================
elif mode == "📄 Analyzer":

    st.header("📄 Analyzer AI")

    file = st.file_uploader("Upload File", type=["pdf","docx","txt","png","jpg"])

    if st.button("Analyze"):
        content = read_file(file)
        result = memory_chat("Analyzer", content)
        st.write(result)
        st.download_button("Download PDF", pdf_download(result))
        st.session_state.usage.append("Analyzer")


# ============================================================
# 📊 DASHBOARD (ADVANCED CHARTS)
# ============================================================
elif mode == "📊 Dashboard":

    st.header("📊 Analytics Dashboard")

    if st.session_state.usage:

        df = pd.DataFrame(st.session_state.usage, columns=["Feature"])

        st.subheader("Usage Count")
        counts = df["Feature"].value_counts()
        st.bar_chart(counts)

        st.subheader("Detailed Data")
        st.write(counts)

    else:
        st.info("No data yet. Use the app first.")

# ---------- FOOTER ----------
st.markdown("---")
st.markdown("<center>👨‍💻 Created by <b>MOHAMMED.USMAN</b></center>", unsafe_allow_html=True)