import streamlit as st
import io
import os
import requests
import PyPDF2
import re
from dotenv import load_dotenv
from docx import Document

# ---------- LOAD ENV ----------
load_dotenv()
API_KEY = os.getenv("NVIDIA_API_KEY")

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="AI Document Analyzer", page_icon="📄")

st.title("📄 AI Document Analyzer")
st.markdown("### 🚀 Smart AI Analysis for Any Document")
st.markdown("Upload any document and get instant AI insights")

if not API_KEY:
    st.error("API key missing in .env file")
    st.stop()

# ---------- INPUT ----------
uploaded_file = st.file_uploader("📤 Upload Document", type=["pdf", "txt", "docx"])

doc_type = st.selectbox(
    "🧠 Select Analysis Type",
    ["General Analysis", "Summary", "Key Points", "Detailed Review"]
)

analyze = st.button("🔍 Analyze Document")

# ---------- FILE READERS ----------
def read_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text
    return text


def read_docx(file):
    doc = Document(file)
    return "\n".join([para.text for para in doc.paragraphs])


def read_file(file):
    if file.type == "application/pdf":
        return read_pdf(io.BytesIO(file.read()))
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return read_docx(file)
    else:
        return file.read().decode()


# ---------- AI CALL (FIXED) ----------
def call_ai(prompt):

    url = "https://integrate.api.nvidia.com/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "deepseek-ai/deepseek-v3.2",  # ✅ FIXED MODEL
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

        return "Unexpected API response format"

    except Exception as e:
        return f"Error: {str(e)}"


# ---------- FORMATTER ----------
def clean_format(text):

    text = text.replace("***", "").replace("**", "")

    lines = text.split("\n")
    formatted = ""

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if line.startswith("-") or line.startswith("*"):
            formatted += f"<li>{line[1:].strip()}</li>"
        elif re.match(r"\d+\.", line):
            formatted += f"<li>{line}</li>"
        else:
            formatted += f"<li><b>{line}</b></li>"

    return f"<ul style='font-size:18px; line-height:1.7'>{formatted}</ul>"


# ---------- MAIN ----------
if analyze and uploaded_file:

    document_text = read_file(uploaded_file)

    if doc_type == "Summary":
        instruction = "Summarize this document clearly in simple language."
    elif doc_type == "Key Points":
        instruction = "Extract key points in bullet format."
    elif doc_type == "Detailed Review":
        instruction = """
        Analyze this document in detail.

        Give:
        - Strengths
        - Weaknesses
        - Suggestions
        """
    else:
        instruction = "Analyze this document and provide useful insights."

    prompt = f"""
You are an expert AI document analyzer.

{instruction}

Document:
{document_text}
"""

    with st.spinner("🤖 AI analyzing document..."):
        analysis = call_ai(prompt)

    # ❌ HANDLE ERRORS SAFELY
    if "API Error" in analysis or "Error" in analysis:
        st.error(analysis)
        st.stop()

    st.session_state.analysis = analysis

    st.markdown("---")
    st.header("📊 AI Analysis Result")

    st.markdown(
        f"<div style='font-size:18px; line-height:1.8'>{analysis}</div>",
        unsafe_allow_html=True
    )


# ---------- CHATBOT ----------
if "analysis" in st.session_state:

    st.markdown("---")
    st.header("🤖 Ask About This Document")

    question = st.text_input("Ask anything about your document")

    if st.button("Ask AI"):

        prompt = f"""
You are an AI assistant.

Document analysis:
{st.session_state.analysis}

User question:
{question}

Give a clear and helpful answer.
"""

        with st.spinner("🤖 Thinking..."):
            answer = call_ai(prompt)

        if "API Error" in answer or "Error" in answer:
            st.error(answer)
        else:
            st.markdown("### 🤖 AI Response")
            st.markdown(
                f"<div style='font-size:18px; line-height:1.7'>{answer}</div>",
                unsafe_allow_html=True
            )


# ---------- FOOTER ----------
st.markdown("---")
st.markdown("### 👨‍💻 Created by **MOHAMMED.USMAN** 🚀")