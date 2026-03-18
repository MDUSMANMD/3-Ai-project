import streamlit as st
import io
import os
import requests
import PyPDF2
import re
import base64
from dotenv import load_dotenv
from docx import Document

# PDF
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# ---------- LOAD ENV ----------
load_dotenv()
API_KEY = os.getenv("NVIDIA_API_KEY")

# ---------- PAGE ----------
st.set_page_config(page_title="AI Study Platform", page_icon="📚")

st.title("📚 AI Study Platform")
st.markdown("### 🚀 Analyze • Learn • Practice")

if not API_KEY:
    st.error("API key missing in .env file")
    st.stop()

# ---------- SIDEBAR MENU ----------
st.sidebar.title("📚 AI Menu")

mode = st.sidebar.radio(
    "Choose Feature",
    [
        "📄 AI Document & Image Analyzer",
        "🎓 Exam Helper",
        "🧠 Quiz Generator",
        "📊 Study Planner"
    ]
)

# ---------- COMMON FUNCTIONS ----------
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
        response = requests.post(url, headers=headers, json=data)

        if response.status_code != 200:
            return f"API Error {response.status_code}: {response.text}"

        result = response.json()

        if "choices" in result:
            return result["choices"][0]["message"]["content"]

        return "Unexpected API response"

    except Exception as e:
        return f"Error: {str(e)}"


def generate_pdf(content):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()

    elements = []
    elements.append(Paragraph("<b>AI Report</b>", styles["Title"]))
    elements.append(Spacer(1, 20))

    for line in content.split("\n"):
        elements.append(Paragraph(line, styles["Normal"]))
        elements.append(Spacer(1, 10))

    doc.build(elements)
    buffer.seek(0)
    return buffer


def read_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        t = page.extract_text()
        if t:
            text += t
    return text


def read_docx(file):
    doc = Document(file)
    return "\n".join([p.text for p in doc.paragraphs])


def read_file(file):
    if file.type == "application/pdf":
        return read_pdf(io.BytesIO(file.read()))
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return read_docx(file)
    else:
        return file.read().decode()


def encode_image(file):
    return base64.b64encode(file.read()).decode("utf-8")


# ============================================================
# 📄 DOCUMENT & IMAGE ANALYZER (YOUR ORIGINAL CODE KEPT)
# ============================================================

if mode == "📄 AI Document & Image Analyzer":

    st.header("📄🖼️ AI Document & Image Analyzer")

    uploaded_file = st.file_uploader(
        "📤 Upload File",
        type=["pdf", "txt", "docx", "png", "jpg", "jpeg"]
    )

    doc_type = st.selectbox(
        "🧠 Select Analysis Type",
        ["General Analysis", "Summary", "Key Points", "Detailed Review"]
    )

    analyze = st.button("🔍 Analyze")

    if analyze and uploaded_file:

        file_type = uploaded_file.type

        if "image" in file_type:
            st.image(uploaded_file, use_column_width=True)

            encoded_img = encode_image(uploaded_file)

            prompt = f"""
Analyze this image and give description, key details and insights.

{encoded_img}
"""
        else:
            document_text = read_file(uploaded_file)

            if doc_type == "Summary":
                instruction = "Summarize this document."
            elif doc_type == "Key Points":
                instruction = "Give key points."
            elif doc_type == "Detailed Review":
                instruction = "Give strengths, weaknesses and suggestions."
            else:
                instruction = "Analyze document."

            prompt = f"""
{instruction}

Document:
{document_text}
"""

        with st.spinner("🤖 AI analyzing..."):
            analysis = call_ai(prompt)

        st.session_state.analysis = analysis

        st.markdown("### 📊 Result")
        st.write(analysis)

        st.download_button(
            "📄 Download PDF",
            generate_pdf(analysis),
            "report.pdf"
        )

    # CHATBOT
    if "analysis" in st.session_state:
        st.markdown("---")
        question = st.text_input("Ask about your file")

        if st.button("Ask AI"):
            answer = call_ai(f"{st.session_state.analysis}\nQuestion:{question}")
            st.write(answer)


# ============================================================
# 🎓 EXAM HELPER
# ============================================================

elif mode == "🎓 Exam Helper":

    st.header("🎓 Exam Helper")

    subject = st.text_input("Subject")
    question = st.text_area("Enter Question")

    if st.button("Get Answer"):

        prompt = f"""
Explain simply.

Subject: {subject}
Question: {question}

Give:
- Explanation
- Key points
- Example
"""

        result = call_ai(prompt)

        st.write(result)

        st.download_button("📥 Download PDF", generate_pdf(result), "notes.pdf")


# ============================================================
# 🧠 QUIZ GENERATOR
# ============================================================

elif mode == "🧠 Quiz Generator":

    st.header("🧠 Quiz Generator")

    topic = st.text_input("Enter Topic")

    if st.button("Generate Quiz"):

        prompt = f"Create 5 MCQs with answers on {topic}"

        result = call_ai(prompt)

        st.write(result)


# ============================================================
# 📊 STUDY PLANNER
# ============================================================

elif mode == "📊 Study Planner":

    st.header("📊 Study Planner")

    subject = st.text_input("Subject")
    days = st.slider("Days", 1, 30, 7)

    if st.button("Create Plan"):

        prompt = f"Create {days}-day study plan for {subject}"

        result = call_ai(prompt)

        st.write(result)

        st.download_button("📥 Download Plan", generate_pdf(result), "plan.pdf")


# ---------- FOOTER (UNCHANGED) ----------
st.markdown("---")
st.markdown("### 👨‍💻 Created by **MOHAMMED.USMAN** 🚀")