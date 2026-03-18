import streamlit as st
import io
import os
import requests
import PyPDF2
import base64
from dotenv import load_dotenv
from docx import Document

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# ---------- LOAD ENV ----------
load_dotenv()
API_KEY = os.getenv("NVIDIA_API_KEY")

# ---------- PAGE ----------
st.set_page_config(page_title="NovaMind AI", page_icon="🚀", layout="wide")

# ---------- PREMIUM UI ----------
st.markdown("""
<style>

/* Background */
.stApp {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    color: white;
}

/* Title Glow */
h1 {
    text-align: center;
    font-size: 50px;
    color: #00ffcc;
    text-shadow: 0px 0px 20px #00ffcc;
}

/* Buttons */
.stButton>button {
    background: linear-gradient(90deg, #00ffcc, #00c3ff);
    color: black;
    border-radius: 12px;
    padding: 12px;
    font-weight: bold;
    transition: 0.3s;
}
.stButton>button:hover {
    transform: scale(1.05);
    box-shadow: 0px 0px 20px #00ffcc;
}

/* Cards */
.card {
    background: rgba(255,255,255,0.05);
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0px 0px 15px rgba(0,255,200,0.2);
    transition: 0.3s;
}
.card:hover {
    transform: scale(1.02);
    box-shadow: 0px 0px 25px #00ffcc;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #0e1117;
}

</style>
""", unsafe_allow_html=True)

# ---------- BRAND ----------
st.sidebar.markdown("""
<div style='text-align:center;'>
    <h1 style='color:#00ffcc;'>🚀 NovaMind AI</h1>
    <p style='color:gray;'>Smart • Fast • Powerful</p>
</div>
""", unsafe_allow_html=True)

# Optional logo (add logo.png in folder)
# st.sidebar.image("logo.png")

# ---------- MENU ----------
mode = st.sidebar.radio(
    "✨ Choose AI Feature",
    [
        "📄 Analyzer",
        "🎓 Study",
        "💼 Career",
        "✍️ Content",
        "💰 Finance",
        "💬 Chat",
        "🧠 Quiz",
        "📊 Planner"
    ]
)

# ---------- FUNCTIONS ----------
def call_ai(prompt):
    url = "https://integrate.api.nvidia.com/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "deepseek-ai/deepseek-v3.2",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.5,
        "max_tokens": 1200
    }

    try:
        res = requests.post(url, headers=headers, json=data)

        if res.status_code != 200:
            return f"API Error: {res.text}"

        return res.json()["choices"][0]["message"]["content"]

    except Exception as e:
        return str(e)


def generate_pdf(content):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()

    elements = []
    for line in content.split("\n"):
        elements.append(Paragraph(line, styles["Normal"]))
        elements.append(Spacer(1, 10))

    doc.build(elements)
    buffer.seek(0)
    return buffer


def read_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for p in reader.pages:
        if p.extract_text():
            text += p.extract_text()
    return text


def read_docx(file):
    doc = Document(file)
    return "\n".join([p.text for p in doc.paragraphs])


def read_file(file):
    if file.type == "application/pdf":
        return read_pdf(io.BytesIO(file.read()))
    elif "word" in file.type:
        return read_docx(file)
    else:
        return file.read().decode(errors="ignore")


def encode_image(file):
    return base64.b64encode(file.read()).decode("utf-8")


# ---------- LANDING ----------
st.markdown("<h1>🚀 NovaMind AI</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align:center;'>All-in-One AI Platform</h3>", unsafe_allow_html=True)

# ============================================================
# 📄 ANALYZER
# ============================================================
if mode == "📄 Analyzer":

    st.markdown("<div class='card'>", unsafe_allow_html=True)

    file = st.file_uploader("Upload File", type=["pdf","txt","docx","png","jpg"])

    if st.button("Analyze") and file:

        if "image" in file.type:
            img = encode_image(file)
            prompt = f"Analyze image: {img}"
        else:
            text = read_file(file)
            prompt = f"Analyze document:\n{text}"

        result = call_ai(prompt)
        st.write(result)
        st.download_button("Download PDF", generate_pdf(result))

    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# 🎓 STUDY
# ============================================================
elif mode == "🎓 Study":

    st.markdown("<div class='card'>", unsafe_allow_html=True)

    q = st.text_area("Enter Question")

    if st.button("Get Answer"):
        res = call_ai(f"Explain for students:\n{q}")
        st.write(res)

    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# 💼 CAREER
# ============================================================
elif mode == "💼 Career":

    role = st.text_input("Role")
    q = st.text_area("Question")

    if st.button("Get Advice"):
        st.write(call_ai(f"{role} career advice: {q}"))

# ============================================================
# ✍️ CONTENT
# ============================================================
elif mode == "✍️ Content":

    topic = st.text_input("Topic")

    if st.button("Generate"):
        st.write(call_ai(f"Write content on {topic}"))

# ============================================================
# 💰 FINANCE
# ============================================================
elif mode == "💰 Finance":

    q = st.text_area("Finance Question")

    if st.button("Get Advice"):
        st.write(call_ai(f"Finance advice: {q}"))

# ============================================================
# 💬 CHAT
# ============================================================
elif mode == "💬 Chat":

    chat = st.text_area("Paste Chat")

    if st.button("Analyze"):
        st.write(call_ai(f"Analyze chat:\n{chat}"))

# ============================================================
# 🧠 QUIZ
# ============================================================
elif mode == "🧠 Quiz":

    topic = st.text_input("Topic")

    if st.button("Generate"):
        st.write(call_ai(f"Create quiz on {topic}"))

# ============================================================
# 📊 PLANNER
# ============================================================
elif mode == "📊 Planner":

    goal = st.text_input("Goal")

    if st.button("Create Plan"):
        st.write(call_ai(f"Plan for: {goal}"))

# ---------- FOOTER ----------
st.markdown("---")
st.markdown("<center>👨‍💻 Created by <b>MOHAMMED.USMAN</b> 🚀</center>", unsafe_allow_html=True)