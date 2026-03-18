import streamlit as st
import io
import os
import requests
import PyPDF2
import re
import base64
from dotenv import load_dotenv
from docx import Document

# ✅ PDF LIBRARY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# ---------- LOAD ENV ----------
load_dotenv()
API_KEY = os.getenv("NVIDIA_API_KEY")

# ---------- PAGE ----------
st.set_page_config(page_title="AI Document & Image Analyzer", page_icon="📄")

st.title("📄🖼️ AI Document & Image Analyzer")
st.markdown("### 🚀 Analyze Documents and Images using AI")

if not API_KEY:
    st.error("API key missing in .env file")
    st.stop()

# ---------- INPUT ----------
uploaded_file = st.file_uploader(
    "📤 Upload File",
    type=["pdf", "txt", "docx", "png", "jpg", "jpeg"]
)

doc_type = st.selectbox(
    "🧠 Select Analysis Type",
    ["General Analysis", "Summary", "Key Points", "Detailed Review"]
)

analyze = st.button("🔍 Analyze")

# ---------- FILE READERS ----------
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


# ---------- IMAGE ENCODE ----------
def encode_image(file):
    return base64.b64encode(file.read()).decode("utf-8")


# ---------- AI CALL ----------
def call_ai(prompt):

    url = "https://integrate.api.nvidia.com/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "deepseek-ai/deepseek-v3.2",
        "messages": [
            {"role": "user", "content": prompt}
        ],
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


# ---------- PDF GENERATOR ----------
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


# ---------- MAIN ----------
if analyze and uploaded_file:

    file_type = uploaded_file.type

    # ---------- IMAGE ----------
    if "image" in file_type:

        st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)

        encoded_img = encode_image(uploaded_file)

        prompt = f"""
You are an AI image analyzer.

Analyze this image.

Give:
- Description
- Key details
- Insights

Image (base64):
{encoded_img}
"""

    # ---------- DOCUMENT ----------
    else:

        document_text = read_file(uploaded_file)

        if doc_type == "Summary":
            instruction = "Summarize this document clearly."
        elif doc_type == "Key Points":
            instruction = "Extract key points."
        elif doc_type == "Detailed Review":
            instruction = """
Analyze this document in detail.

Give:
- Strengths
- Weaknesses
- Suggestions
"""
        else:
            instruction = "Analyze this document and provide insights."

        prompt = f"""
You are an expert AI document analyzer.

{instruction}

Format as a professional report:

Title: AI Analysis Report

Summary:
...

Key Points:
...

Insights:
...

Document:
{document_text}
"""

    # ---------- AI PROCESS ----------
    with st.spinner("🤖 AI analyzing..."):
        analysis = call_ai(prompt)

    if "API Error" in analysis or "Error" in analysis:
        st.error(analysis)
        st.stop()

    st.session_state.analysis = analysis

    st.markdown("---")
    st.header("📊 AI Result")

    st.markdown(
        f"<div style='font-size:18px; line-height:1.8'>{analysis}</div>",
        unsafe_allow_html=True
    )

    # ---------- PDF DOWNLOAD ----------
    pdf_file = generate_pdf(analysis)

    st.download_button(
        label="📄 Download PDF Report",
        data=pdf_file,
        file_name="AI_Analysis_Report.pdf",
        mime="application/pdf"
    )


# ---------- CHATBOT ----------
if "analysis" in st.session_state:

    st.markdown("---")
    st.header("🤖 Ask About It")

    question = st.text_input("Ask anything about your file")

    if st.button("Ask AI"):

        prompt = f"""
Analysis:
{st.session_state.analysis}

Question:
{question}
"""

        with st.spinner("🤖 Thinking..."):
            answer = call_ai(prompt)

        if "Error" in answer:
            st.error(answer)
        else:
            st.markdown("### 🤖 AI Response")
            st.write(answer)


# ---------- FOOTER ----------
st.markdown("---")
st.markdown("### 👨‍💻 Created by **MOHAMMED.USMAN** 🚀")