import streamlit as st
import io
import requests
import PyPDF2
from docx import Document
import pandas as pd

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib.enums import TA_CENTER

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="NovaMind AI",
    page_icon="🚀",
    layout="wide"
)

# =========================================================
# API KEY
# =========================================================
API_KEY = st.secrets["NVIDIA_API_KEY"]

# =========================================================
# CUSTOM CSS
# =========================================================
st.markdown(
    """
    <style>

    .stApp {
        background-color: #0f1117;
        color: white;
    }

    h1, h2, h3 {
        color: white;
    }

    .stButton > button {
        background-color: #4CAF50;
        color: white;
        border-radius: 10px;
        padding: 10px 20px;
        border: none;
        font-weight: bold;
    }

    .stButton > button:hover {
        background-color: #45a049;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.title("🚀 NovaMind AI")

mode = st.sidebar.radio(
    "Select Module",
    [
        "🎓 Education",
        "💼 Career",
        "💰 Finance",
        "📄 Analyzer",
        "📊 Dashboard"
    ]
)

# =========================================================
# SESSION STATE
# =========================================================
if "memory" not in st.session_state:
    st.session_state.memory = {
        "Education": [],
        "Career": [],
        "Finance": [],
        "Analyzer": []
    }

if "usage" not in st.session_state:
    st.session_state.usage = []

# =========================================================
# AI FUNCTION
# =========================================================
def call_ai(prompt):

    url = "https://integrate.api.nvidia.com/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # ✅ WORKING MODEL
    payload = {
        "model": "meta/llama-3.1-70b-instruct",
        "messages": [
            {
                "role": "system",
                "content": "You are a professional AI assistant. Give structured and clear responses."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7,
        "max_tokens": 700
    }

    try:

        with st.spinner("🤖 AI is thinking..."):
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=60
            )

        if response.status_code != 200:
            return f"❌ API ERROR {response.status_code}: {response.text}"

        data = response.json()

        # ✅ SAFER RESPONSE HANDLING
        if "choices" in data:
            return data["choices"][0]["message"]["content"]

        return "❌ Invalid API response"

    except Exception as e:
        return f"❌ ERROR: {str(e)}"

# =========================================================
# FILE READER
# =========================================================
def read_file(file):

    if not file:
        return ""

    try:

        # PDF
        if file.type == "application/pdf":

            reader = PyPDF2.PdfReader(file)
            text = ""

            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"

            return text

        # DOCX
        elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":

            doc = Document(file)
            return "\n".join([p.text for p in doc.paragraphs])

        # TXT
        elif file.type == "text/plain":
            return file.read().decode("utf-8", errors="ignore")

        # IMAGE
        elif "image" in file.type:
            return "User uploaded an image. Analyze and describe it professionally."

        return "Unsupported file type"

    except Exception as e:
        return f"Error reading file: {str(e)}"

# =========================================================
# PDF GENERATOR
# =========================================================
def pdf_download(text):

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        name="Title",
        parent=styles["Heading1"],
        alignment=TA_CENTER,
        spaceAfter=20
    )

    body_style = styles["Normal"]

    elements = []

    elements.append(Paragraph("NovaMind AI Report", title_style))
    elements.append(Spacer(1, 20))

    cleaned_text = (
        text
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )

    for line in cleaned_text.split("\n"):

        line = line.strip()

        if line:
            elements.append(Paragraph(line, body_style))
            elements.append(Spacer(1, 8))

    doc.build(elements)

    buffer.seek(0)

    return buffer

# =========================================================
# MEMORY CHAT
# =========================================================
def memory_chat(module, user_input):

    history = "\n".join(st.session_state.memory[module][-4:])

    prompt = f"""
    Previous Conversation:
    {history}

    User Input:
    {user_input}
    """

    response = call_ai(prompt)

    st.session_state.memory[module].append(f"User: {user_input}")
    st.session_state.memory[module].append(f"AI: {response}")

    return response

# =========================================================
# CHATBOT
# =========================================================
def chatbot(module):

    st.markdown("## 💬 Chat with AI")

    question = st.text_input("Ask anything")

    if st.button("Ask AI"):

        if question:

            response = memory_chat(module, question)

            st.success("Response Generated")
            st.write(response)

# =========================================================
# EDUCATION MODULE
# =========================================================
if mode == "🎓 Education":

    st.header("🎓 Education AI")

    file = st.file_uploader(
        "Upload Notes",
        type=["pdf", "docx", "txt", "png", "jpg"]
    )

    question = st.text_area("Ask Question")

    if st.button("Get Answer"):

        content = read_file(file)

        result = memory_chat(
            "Education",
            content + "\n" + question
        )

        st.markdown("### 📘 Answer")
        st.write(result)

        st.download_button(
            "⬇️ Download PDF Report",
            pdf_download(result),
            file_name="Education_Report.pdf"
        )

        st.session_state.usage.append("Education")

    chatbot("Education")

# =========================================================
# CAREER MODULE
# =========================================================
elif mode == "💼 Career":

    st.header("💼 Career AI")

    file = st.file_uploader(
        "Upload Resume",
        type=["pdf", "docx", "txt"]
    )

    role = st.text_input("Target Role")

    if st.button("Analyze Resume"):

        content = read_file(file)

        prompt = f"""
        Analyze this resume for the role: {role}

        Give:
        1. Resume Score
        2. Strengths
        3. Weaknesses
        4. Missing Skills
        5. ATS Improvement Tips

        Resume:
        {content}
        """

        result = memory_chat("Career", prompt)

        st.markdown("### 💼 Career Analysis")
        st.write(result)

        st.download_button(
            "⬇️ Download PDF Report",
            pdf_download(result),
            file_name="Career_Report.pdf"
        )

        st.session_state.usage.append("Career")

    chatbot("Career")

# =========================================================
# FINANCE MODULE
# =========================================================
elif mode == "💰 Finance":

    st.header("💰 Finance AI")

    file = st.file_uploader(
        "Upload Financial File",
        type=["pdf", "txt"]
    )

    question = st.text_area("Ask Finance Question")

    if st.button("Get Advice"):

        content = read_file(file)

        result = memory_chat(
            "Finance",
            content + "\n" + question
        )

        st.markdown("### 💰 Finance Advice")
        st.write(result)

        st.download_button(
            "⬇️ Download PDF Report",
            pdf_download(result),
            file_name="Finance_Report.pdf"
        )

        st.session_state.usage.append("Finance")

    chatbot("Finance")

# =========================================================
# ANALYZER MODULE
# =========================================================
elif mode == "📄 Analyzer":

    st.header("📄 File Analyzer AI")

    file = st.file_uploader(
        "Upload File",
        type=["pdf", "docx", "txt", "png", "jpg"]
    )

    if st.button("Analyze File"):

        content = read_file(file)

        result = memory_chat("Analyzer", content)

        st.markdown("### 📊 Analysis Result")
        st.write(result)

        st.download_button(
            "⬇️ Download PDF Report",
            pdf_download(result),
            file_name="Analysis_Report.pdf"
        )

        st.session_state.usage.append("Analyzer")

    chatbot("Analyzer")

# =========================================================
# DASHBOARD
# =========================================================
elif mode == "📊 Dashboard":

    st.header("📊 Analytics Dashboard")

    if st.session_state.usage:

        df = pd.DataFrame(
            st.session_state.usage,
            columns=["Feature"]
        )

        counts = df["Feature"].value_counts()

        st.bar_chart(counts)

        st.write(counts)

        st.metric("Total Usage", len(st.session_state.usage))

    else:
        st.info("No usage yet")

# =========================================================
# FOOTER
# =========================================================
st.markdown("---")

st.markdown(
    """
    <center>
    👨‍💻 Created by <b>MOHAMMED.USMAN</b> 🚀
    </center>
    """,
    unsafe_allow_html=True
)