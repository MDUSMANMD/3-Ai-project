import streamlit as st
import io, requests
import PyPDF2
from docx import Document
import pandas as pd

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# ---------- API ----------
API_KEY = st.secrets["NVIDIA_API_KEY"]

st.set_page_config(page_title="NovaMind AI", layout="wide")

# ---------- UI ----------
st.markdown("""
<style>
.stApp {background:#1e1e1e; color:white;}
</style>
""", unsafe_allow_html=True)

st.sidebar.title("🚀 NovaMind AI")

mode = st.sidebar.radio(
    "Select Module",
    ["🎓 Education", "💼 Career", "💰 Finance", "📄 Analyzer", "📊 Dashboard"]
)

# ---------- MEMORY ----------
if "memory" not in st.session_state:
    st.session_state.memory = {
        "Education": [], "Career": [], "Finance": [], "Analyzer": []
    }

if "usage" not in st.session_state:
    st.session_state.usage = []

# ---------- AI FUNCTION ----------
def call_ai(prompt):
    url = "https://integrate.api.nvidia.com/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "meta/llama3-70b-instruct",  # ✅ stable model
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 300
    }

    try:
        with st.spinner("🤖 AI is thinking..."):
            res = requests.post(url, headers=headers, json=data, timeout=25)

        if res.status_code != 200:
            return f"API ERROR {res.status_code}:\n{res.text}"

        result = res.json()
        return result["choices"][0]["message"]["content"]

    except Exception as e:
        return f"ERROR: {str(e)}"

# ---------- FILE READER ----------
def read_file(file):
    if not file:
        return ""

    if "pdf" in file.type:
        reader = PyPDF2.PdfReader(file)
        return "".join([p.extract_text() or "" for p in reader.pages])

    elif "word" in file.type:
        doc = Document(file)
        return "\n".join([p.text for p in doc.paragraphs])

    elif "image" in file.type:
        return "User uploaded an image. Describe and analyze it."

    else:
        return file.read().decode(errors="ignore")

# ---------- PDF ----------
def pdf_download(text):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()

    elements = []
    for line in text.split("\n"):
        elements.append(Paragraph(line, styles["Normal"]))
        elements.append(Spacer(1, 10))

    doc.build(elements)
    buffer.seek(0)
    return buffer

# ---------- MEMORY CHAT ----------
def memory_chat(module, user_input):
    history = "\n".join(st.session_state.memory[module][-4:])
    prompt = f"{history}\nUser: {user_input}"

    response = call_ai(prompt)

    st.session_state.memory[module].append(f"User: {user_input}")
    st.session_state.memory[module].append(f"AI: {response}")

    return response

# ---------- CHATBOT ----------
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

    file = st.file_uploader("Upload Notes", type=["pdf","docx","txt","png","jpg"])
    q = st.text_area("Ask Question")

    if st.button("Get Answer"):
        content = read_file(file)
        result = memory_chat("Education", content + "\n" + q)

        st.markdown("### 📘 Answer")
        st.write(result)

        st.markdown("---")
        st.download_button("⬇️ Download PDF", pdf_download(result))

        st.session_state.usage.append("Education")

    chatbot("Education")

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

        st.markdown("### 💼 Career Analysis")
        st.write(result)

        st.markdown("---")
        st.download_button("⬇️ Download PDF", pdf_download(result))

        st.session_state.usage.append("Career")

    chatbot("Career")

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

        st.markdown("### 💰 Advice")
        st.write(result)

        st.markdown("---")
        st.download_button("⬇️ Download PDF", pdf_download(result))

        st.session_state.usage.append("Finance")

    chatbot("Finance")

# ============================================================
# 📄 ANALYZER
# ============================================================
elif mode == "📄 Analyzer":

    st.header("📄 Analyzer AI")

    file = st.file_uploader("Upload File", type=["pdf","docx","txt","png","jpg"])

    if st.button("Analyze"):
        content = read_file(file)
        result = memory_chat("Analyzer", content)

        st.markdown("### 📊 Analysis Result")
        st.write(result)

        st.markdown("---")
        st.download_button("⬇️ Download PDF", pdf_download(result))

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
st.markdown("<center>👨‍💻 Created by <b>MOHAMMED.USMAN</b> 🚀</center>", unsafe_allow_html=True)