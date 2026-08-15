import io
import os
from typing import Optional

import pandas as pd
import requests
import streamlit as st
from dotenv import load_dotenv
from docx import Document
from PyPDF2 import PdfReader
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

load_dotenv()

APP_NAME = "NovaMind AI"
API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
DEFAULT_MODEL = os.getenv("NVIDIA_MODEL", "meta/llama-3.1-70b-instruct")
MAX_INPUT_CHARS = int(os.getenv("NOVAMIND_MAX_INPUT_CHARS", "24000"))

st.set_page_config(page_title=APP_NAME, page_icon="N", layout="wide")


def get_api_key() -> Optional[str]:
    """Read the API key from Streamlit secrets first, then the environment."""
    try:
        secret_key = st.secrets.get("NVIDIA_API_KEY")
    except Exception:
        secret_key = None
    return secret_key or os.getenv("NVIDIA_API_KEY")


API_KEY = get_api_key()

st.markdown(
    """
    <style>
    .stApp { background: #0f1117; }
    .stButton > button { border-radius: 8px; font-weight: 600; }
    .novamind-note { color: #aab4c3; font-size: 0.9rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title(APP_NAME)
st.caption("A practical AI workspace for study support, career feedback, document analysis, and personal insights.")

if not API_KEY:
    st.warning("NVIDIA_API_KEY is not configured. Add it to Streamlit secrets or a local .env file before using AI features.")


if "memory" not in st.session_state:
    st.session_state.memory = {module: [] for module in ("Education", "Career", "Finance", "Analyzer")}
if "usage" not in st.session_state:
    st.session_state.usage = []
if "results" not in st.session_state:
    st.session_state.results = {}


def call_ai(prompt: str, system_message: str = "You are a professional AI assistant. Give structured, clear, and actionable responses.") -> str:
    """Call the NVIDIA-compatible chat endpoint and return a user-safe message."""
    if not API_KEY:
        return "AI is unavailable because NVIDIA_API_KEY is not configured."

    payload = {
        "model": DEFAULT_MODEL,
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt[:MAX_INPUT_CHARS]},
        ],
        "temperature": 0.5,
        "max_tokens": 900,
    }
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

    try:
        with st.spinner("AI is preparing your response..."):
            response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        choices = data.get("choices", [])
        if choices and choices[0].get("message", {}).get("content"):
            return choices[0]["message"]["content"]
        return "The AI service returned an unexpected response format."
    except requests.RequestException as exc:
        return f"The AI request failed: {exc}"
    except (ValueError, KeyError, IndexError) as exc:
        return f"The AI response could not be read: {exc}"


def read_file(uploaded_file) -> str:
    """Extract text from supported uploads without executing their contents."""
    if not uploaded_file:
        return ""
    try:
        file_type = uploaded_file.type or ""
        if file_type == "application/pdf":
            reader = PdfReader(uploaded_file)
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        if file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            document = Document(uploaded_file)
            return "\n".join(paragraph.text for paragraph in document.paragraphs)
        if file_type.startswith("text/") or uploaded_file.name.lower().endswith((".txt", ".md", ".csv")):
            return uploaded_file.getvalue().decode("utf-8", errors="ignore")
        if file_type.startswith("image/"):
            return "The user uploaded an image. Explain what can be inferred from it and state any limitations."
        return "Unsupported file type. Please upload PDF, DOCX, TXT, Markdown, CSV, or an image."
    except Exception as exc:
        return f"The file could not be read safely: {exc}"


def generate_pdf(text: str, title: str = "NovaMind AI Report") -> io.BytesIO:
    """Create a downloadable plain-text report as a PDF."""
    buffer = io.BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.6 * inch,
        leftMargin=0.6 * inch,
        topMargin=0.6 * inch,
        bottomMargin=0.6 * inch,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("ReportTitle", parent=styles["Heading1"], alignment=TA_CENTER, spaceAfter=16)
    body_style = styles["BodyText"]
    elements = [Paragraph(title, title_style)]
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line:
            safe_line = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            elements.extend([Paragraph(safe_line, body_style), Spacer(1, 6)])
    document.build(elements)
    buffer.seek(0)
    return buffer


def record_result(module: str, result: str) -> None:
    st.session_state.results[module] = result
    st.session_state.usage.append(module)


def render_chat(module: str) -> None:
    st.subheader("Ask a follow-up question")
    question = st.text_input("Question", key=f"chat_{module}")
    if st.button("Ask AI", key=f"ask_{module}") and question.strip():
        history = "\n".join(st.session_state.memory[module][-6:])
        result = call_ai(f"Conversation context:\n{history}\n\nNew question:\n{question}")
        st.session_state.memory[module].extend([f"User: {question}", f"AI: {result}"])
        st.write(result)


def render_result(module: str, filename: str) -> None:
    result = st.session_state.results.get(module)
    if result:
        st.markdown("### Result")
        st.write(result)
        st.download_button("Download PDF report", generate_pdf(result, f"{APP_NAME} — {module}"), filename, "application/pdf", key=f"download_{module}")


with st.sidebar:
    st.header(APP_NAME)
    mode = st.radio("Select module", ["Education", "Career", "Finance", "Analyzer", "Dashboard"])
    st.divider()
    st.caption(f"Model: {DEFAULT_MODEL}")

if mode == "Education":
    st.header("Education assistant")
    uploaded = st.file_uploader("Upload notes or study material", type=["pdf", "docx", "txt", "md", "csv", "png", "jpg", "jpeg"])
    question = st.text_area("What would you like to understand?")
    if st.button("Get answer", key="education_submit"):
        content = read_file(uploaded)
        if not content.strip() and not question.strip():
            st.info("Upload material or enter a question first.")
        else:
            result = call_ai(f"Summarize the material, explain difficult points, and answer the question.\n\nMaterial:\n{content}\n\nQuestion:\n{question}")
            record_result("Education", result)
    render_result("Education", "education_report.pdf")
    render_chat("Education")

elif mode == "Career":
    st.header("Career assistant")
    uploaded = st.file_uploader("Upload your resume", type=["pdf", "docx", "txt", "md"])
    role = st.text_input("Target role")
    if st.button("Analyze resume", key="career_submit"):
        content = read_file(uploaded)
        if not content.strip():
            st.info("Upload a resume first.")
        else:
            result = call_ai(f"Review this resume for the target role '{role or 'general applications'}'. Provide a score, strengths, weaknesses, missing skills, ATS improvements, and rewritten examples.\n\nResume:\n{content}", "You are an experienced recruiter and resume reviewer. Be constructive and specific.")
            record_result("Career", result)
    render_result("Career", "career_report.pdf")
    render_chat("Career")

elif mode == "Finance":
    st.header("Finance document assistant")
    st.warning("This tool provides general document analysis, not personalized financial advice.")
    uploaded = st.file_uploader("Upload a financial document", type=["pdf", "txt", "md", "csv"])
    question = st.text_area("What would you like analyzed?")
    if st.button("Analyze document", key="finance_submit"):
        content = read_file(uploaded)
        if not content.strip() and not question.strip():
            st.info("Upload a document or enter a question first.")
        else:
            result = call_ai(f"Analyze the document and explain assumptions, trends, risks, and unanswered questions. Do not present the result as personalized financial advice.\n\nDocument:\n{content}\n\nQuestion:\n{question}")
            record_result("Finance", result)
    render_result("Finance", "finance_report.pdf")
    render_chat("Finance")

elif mode == "Analyzer":
    st.header("File analyzer")
    uploaded = st.file_uploader("Upload a file", type=["pdf", "docx", "txt", "md", "csv", "png", "jpg", "jpeg"])
    if st.button("Analyze file", key="analyzer_submit"):
        content = read_file(uploaded)
        if not content.strip():
            st.info("Upload a supported file first.")
        else:
            result = call_ai(f"Analyze this uploaded content. Return a concise summary, key points, possible issues, and recommended next actions.\n\nContent:\n{content}")
            record_result("Analyzer", result)
    render_result("Analyzer", "analysis_report.pdf")
    render_chat("Analyzer")

else:
    st.header("Usage dashboard")
    if st.session_state.usage:
        usage = pd.Series(st.session_state.usage, name="Feature").value_counts()
        st.metric("Total analyses", int(usage.sum()))
        st.bar_chart(usage)
        st.dataframe(usage.rename("Uses"), use_container_width=True)
    else:
        st.info("Your usage dashboard will appear after the first analysis.")

st.divider()
st.caption("Built by Mohammed Usman • NovaMind AI")
