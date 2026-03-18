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

# ---------- ENV ----------
load_dotenv()
API_KEY = os.getenv("NVIDIA_API_KEY")

# ---------- PAGE ----------
st.set_page_config(page_title="NovaMind AI", page_icon="🚀", layout="wide")

# ---------- GLASS UI ----------
st.markdown("""
<style>

/* Background */
.stApp {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
}

/* Glass Card */
.glass {
    background: rgba(255, 255, 255, 0.08);
    border-radius: 20px;
    padding: 25px;
    backdrop-filter: blur(15px);
    box-shadow: 0 0 30px rgba(0,255,200,0.2);
    transition: 0.3s;
}
.glass:hover {
    box-shadow: 0 0 50px rgba(0,255,200,0.4);
}

/* Title */
h1 {
    text-align:center;
    color:#00ffcc;
    text-shadow:0 0 20px #00ffcc;
}

/* Buttons */
.stButton>button {
    background: linear-gradient(90deg, #00ffcc, #00c3ff);
    color:black;
    border-radius:12px;
    padding:10px;
    transition:0.3s;
}
.stButton>button:hover {
    transform:scale(1.05);
    box-shadow:0 0 20px #00ffcc;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background:#0e1117;
}

</style>
""", unsafe_allow_html=True)

# ---------- BRAND ----------
st.sidebar.markdown("""
<div style='text-align:center;'>
<h1>🚀 NovaMind AI</h1>
<p style='color:gray;'>Smart • Fast • Powerful</p>
</div>
""", unsafe_allow_html=True)

mode = st.sidebar.radio(
    "✨ Choose Feature",
    ["📄 Analyzer","🎓 Study","💼 Career","✍️ Content","💰 Finance","💬 Chat","🧠 Quiz","📊 Planner"]
)

# ---------- COMMON ----------
def call_ai(prompt):
    url = "https://integrate.api.nvidia.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {API_KEY}","Content-Type":"application/json"}
    data = {
        "model":"deepseek-ai/deepseek-v3.2",
        "messages":[{"role":"user","content":prompt}],
        "temperature":0.5
    }
    try:
        res = requests.post(url, headers=headers, json=data)
        if res.status_code != 200:
            return f"Error: {res.text}"
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
        elements.append(Spacer(1,10))
    doc.build(elements)
    buffer.seek(0)
    return buffer

def read_pdf(file):
    reader = PyPDF2.PdfReader(file)
    return "".join([p.extract_text() or "" for p in reader.pages])

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

def handle_upload(file):
    if not file:
        return ""
    if "image" in file.type:
        return f"Image Data:\n{encode_image(file)}"
    else:
        return read_file(file)

# ---------- TITLE ----------
st.markdown("<h1>🚀 NovaMind AI</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align:center;'>All-in-One AI Platform</h3>", unsafe_allow_html=True)

# ============================================================
# 📄 ANALYZER
# ============================================================
if mode == "📄 Analyzer":

    st.markdown("<div class='glass'>", unsafe_allow_html=True)

    file = st.file_uploader("Upload File", type=["pdf","txt","docx","png","jpg","jpeg"])

    if st.button("Analyze"):
        content = handle_upload(file)
        result = call_ai(f"Analyze:\n{content}")
        st.write(result)
        st.download_button("Download PDF", generate_pdf(result))

    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# 🎓 STUDY
# ============================================================
elif mode == "🎓 Study":

    st.markdown("<div class='glass'>", unsafe_allow_html=True)

    file = st.file_uploader("Upload Notes/Image", type=["pdf","txt","docx","png","jpg"])
    q = st.text_area("Question")

    if st.button("Get Answer"):
        content = handle_upload(file)
        result = call_ai(f"Study help:\n{content}\nQuestion:{q}")
        st.write(result)

    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# 💼 CAREER
# ============================================================
elif mode == "💼 Career":

    st.markdown("<div class='glass'>", unsafe_allow_html=True)

    file = st.file_uploader("Upload Resume/Image", type=["pdf","docx","png","jpg"])
    role = st.text_input("Role")

    if st.button("Get Advice"):
        content = handle_upload(file)
        st.write(call_ai(f"Career advice for {role}:\n{content}"))

    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# ✍️ CONTENT
# ============================================================
elif mode == "✍️ Content":

    st.markdown("<div class='glass'>", unsafe_allow_html=True)

    file = st.file_uploader("Upload Reference", type=["pdf","txt","docx","png","jpg"])
    topic = st.text_input("Topic")

    if st.button("Generate"):
        content = handle_upload(file)
        st.write(call_ai(f"Create content on {topic} using:\n{content}"))

    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# 💰 FINANCE
# ============================================================
elif mode == "💰 Finance":

    st.markdown("<div class='glass'>", unsafe_allow_html=True)

    file = st.file_uploader("Upload Data/Image", type=["pdf","txt","png","jpg"])
    q = st.text_area("Finance Question")

    if st.button("Get Advice"):
        content = handle_upload(file)
        st.write(call_ai(f"Finance advice:\n{content}\n{q}"))

    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# 💬 CHAT
# ============================================================
elif mode == "💬 Chat":

    st.markdown("<div class='glass'>", unsafe_allow_html=True)

    file = st.file_uploader("Upload Chat Screenshot/File", type=["txt","png","jpg"])
    chat = st.text_area("Or paste chat")

    if st.button("Analyze"):
        content = handle_upload(file)
        st.write(call_ai(f"Analyze chat:\n{chat}\n{content}"))

    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# 🧠 QUIZ
# ============================================================
elif mode == "🧠 Quiz":

    st.markdown("<div class='glass'>", unsafe_allow_html=True)

    file = st.file_uploader("Upload Study Material", type=["pdf","txt","docx","png","jpg"])
    topic = st.text_input("Topic")

    if st.button("Generate Quiz"):
        content = handle_upload(file)
        st.write(call_ai(f"Create quiz on {topic} using:\n{content}"))

    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# 📊 PLANNER
# ============================================================
elif mode == "📊 Planner":

    st.markdown("<div class='glass'>", unsafe_allow_html=True)

    file = st.file_uploader("Upload Goals/Image", type=["pdf","txt","png","jpg"])
    goal = st.text_input("Goal")

    if st.button("Create Plan"):
        content = handle_upload(file)
        st.write(call_ai(f"Plan for {goal}:\n{content}"))

    st.markdown("</div>", unsafe_allow_html=True)

# ---------- FOOTER ----------
st.markdown("---")
st.markdown("<center>👨‍💻 Created by <b>MOHAMMED.USMAN</b> 🚀</center>", unsafe_allow_html=True)