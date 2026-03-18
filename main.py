import streamlit as st
import io
import os
import requests
import PyPDF2
import base64
from dotenv import load_dotenv
from docx import Document

# PDF
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# ---------- LOAD ENV ----------
load_dotenv()
API_KEY = os.getenv("NVIDIA_API_KEY")

st.set_page_config(page_title="AI Study Assistant", page_icon="📚")

st.title("📚 AI Study Assistant")
st.markdown("### 🚀 Learn Smarter with AI")

if not API_KEY:
    st.error("API key missing")
    st.stop()

# ---------- MODE ----------
mode = st.sidebar.selectbox(
    "Select Feature",
    ["📄 Analyzer", "🎓 Exam Helper", "🧠 Quiz Generator", "📊 Study Planner"]
)

# ---------- COMMON AI FUNCTION ----------
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
            return f"Error {response.status_code}: {response.text}"

        return response.json()["choices"][0]["message"]["content"]

    except Exception as e:
        return str(e)

# ---------- PDF ----------
def generate_pdf(content):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()

    elements = []
    elements.append(Paragraph("<b>AI Generated Report</b>", styles["Title"]))
    elements.append(Spacer(1, 20))

    for line in content.split("\n"):
        elements.append(Paragraph(line, styles["Normal"]))
        elements.append(Spacer(1, 10))

    doc.build(elements)
    buffer.seek(0)
    return buffer

# ---------- FILE READ ----------
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
    elif "word" in file.type:
        return read_docx(file)
    else:
        return file.read().decode()

# ---------- MODE 1: ANALYZER ----------
if mode == "📄 Analyzer":

    file = st.file_uploader("Upload File", type=["pdf", "txt", "docx", "png", "jpg"])

    if st.button("Analyze") and file:

        if "image" in file.type:
            img = base64.b64encode(file.read()).decode()

            prompt = f"""
Analyze this image and describe clearly.

Image:
{img}
"""
        else:
            text = read_file(file)

            prompt = f"""
Analyze this document and give:

Summary
Key Points
Insights

{text}
"""

        result = call_ai(prompt)

        st.write(result)

        st.download_button("📥 Download PDF", generate_pdf(result), "report.pdf")

# ---------- MODE 2: EXAM HELPER ----------
elif mode == "🎓 Exam Helper":

    subject = st.text_input("Subject")
    question = st.text_area("Enter Question")

    if st.button("Get Answer"):

        prompt = f"""
You are a teacher.

Explain clearly for students.

Subject: {subject}

Question:
{question}

Give:
- Simple explanation
- Key points
- Example
"""

        result = call_ai(prompt)

        st.write(result)

        st.download_button("📥 Download Notes", generate_pdf(result), "notes.pdf")

# ---------- MODE 3: QUIZ ----------
elif mode == "🧠 Quiz Generator":

    topic = st.text_input("Enter Topic")

    if st.button("Generate Quiz"):

        prompt = f"""
Create 5 MCQs on {topic}.

Include:
Question
Options A B C D
Correct Answer
"""

        result = call_ai(prompt)

        st.write(result)

# ---------- MODE 4: STUDY PLANNER ----------
elif mode == "📊 Study Planner":

    subject = st.text_input("Subject")
    days = st.slider("Days to prepare", 1, 30, 7)

    if st.button("Create Plan"):

        prompt = f"""
Create a {days}-day study plan for {subject}.

Make it simple and effective for exams.
"""

        result = call_ai(prompt)

        st.write(result)

        st.download_button("📥 Download Plan", generate_pdf(result), "study_plan.pdf")

# ---------- FOOTER ----------
st.markdown("---")
st.markdown("### 👨‍💻 Created by **MOHAMMED USMAN** 🚀")