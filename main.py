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

# ---------- PAGE ----------
st.set_page_config(page_title="AI Super Assistant", page_icon="🚀")

# ---------- UI STYLE ----------
st.markdown("""
<style>
.main {
    background-color: #0e1117;
}
h1, h2, h3 {
    color: #00ffcc;
}
.stButton>button {
    background-color: #00ffcc;
    color: black;
    border-radius: 10px;
    padding: 10px;
}
.stDownloadButton>button {
    background-color: #ff4b4b;
    color: white;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# ---------- TITLE ----------
st.title("🚀 AI Super Assistant")
st.markdown("### Analyze • Learn • Create • Plan • Grow")
st.info("🤖 Your all-in-one AI platform for productivity and learning.")

if not API_KEY:
    st.error("API key missing in .env file")
    st.stop()

# ---------- SIDEBAR ----------
st.sidebar.title("🚀 AI Menu")

st.sidebar.markdown("### 🌟 Features")
st.sidebar.markdown("""
- 📄 Document & Image Analysis  
- 🎓 Study Assistant  
- 💼 Career Guidance  
- ✍️ Content Creation  
- 💰 Finance Help  
- 💬 Chat Analysis  
- 🧠 Quiz Generator  
- 📊 Smart Planner  
""")

mode = st.sidebar.radio(
    "Choose Feature",
    [
        "📄 AI Document & Image Analyzer",
        "🎓 Study Assistant",
        "💼 Career Assistant",
        "✍️ Content Generator",
        "💰 Finance Assistant",
        "💬 Chat Analyzer",
        "🧠 Quiz Generator",
        "📊 Smart Planner"
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

        res_json = response.json()

        if "choices" in res_json:
            return res_json["choices"][0]["message"]["content"]

        return "Unexpected API response"

    except Exception as e:
        return f"Error: {str(e)}"


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
        return file.read().decode(errors="ignore")


def encode_image(file):
    return base64.b64encode(file.read()).decode("utf-8")


# ============================================================
# 📄 DOCUMENT & IMAGE ANALYZER
# ============================================================

if mode == "📄 AI Document & Image Analyzer":

    st.header("📄🖼️ AI Document & Image Analyzer")

    file = st.file_uploader("Upload File", type=["pdf", "txt", "docx", "png", "jpg", "jpeg"])

    doc_type = st.selectbox(
        "Analysis Type",
        ["General Analysis", "Summary", "Key Points", "Detailed Review"]
    )

    if st.button("Analyze") and file:

        if "image" in file.type:
            st.image(file)

            img = encode_image(file)

            prompt = f"""
Analyze this image and give:
- Description
- Key details
- Insights

{img}
"""
        else:
            text = read_file(file)

            if doc_type == "Summary":
                instruction = "Summarize this document."
            elif doc_type == "Key Points":
                instruction = "Give key points."
            elif doc_type == "Detailed Review":
                instruction = "Give strengths, weaknesses and suggestions."
            else:
                instruction = "Analyze document."

            prompt = f"{instruction}\n{text}"

        with st.spinner("🤖 AI analyzing..."):
            result = call_ai(prompt)

        st.session_state.analysis = result

        st.write(result)

        st.download_button("📄 Download PDF", generate_pdf(result), "report.pdf")

    if "analysis" in st.session_state:
        q = st.text_input("Ask about your file")
        if st.button("Ask AI"):
            st.write(call_ai(st.session_state.analysis + "\n" + q))


# ============================================================
# 🎓 STUDY ASSISTANT
# ============================================================

elif mode == "🎓 Study Assistant":

    st.header("🎓 Study Assistant")

    subject = st.text_input("Subject")
    question = st.text_area("Question")

    if st.button("Get Answer"):

        prompt = f"""
Explain clearly for students.

Subject: {subject}
Question: {question}

Give explanation, key points and example.
"""

        result = call_ai(prompt)

        st.write(result)
        st.download_button("📥 Download", generate_pdf(result), "notes.pdf")


# ============================================================
# 💼 CAREER ASSISTANT
# ============================================================

elif mode == "💼 Career Assistant":

    st.header("💼 Career Assistant")

    role = st.text_input("Job Role")
    q = st.text_area("Your Question")

    if st.button("Get Advice"):

        result = call_ai(f"Career advice for {role}: {q}")

        st.write(result)
        st.download_button("📥 Download", generate_pdf(result), "career.pdf")


# ============================================================
# ✍️ CONTENT GENERATOR
# ============================================================

elif mode == "✍️ Content Generator":

    st.header("✍️ Content Generator")

    topic = st.text_input("Topic")
    ctype = st.selectbox("Type", ["Blog", "Caption", "Email", "Story"])

    if st.button("Generate"):

        result = call_ai(f"Write a {ctype} about {topic}")

        st.write(result)
        st.download_button("📥 Download", generate_pdf(result), "content.pdf")


# ============================================================
# 💰 FINANCE ASSISTANT
# ============================================================

elif mode == "💰 Finance Assistant":

    st.header("💰 Finance Assistant")

    ftype = st.selectbox(
        "Category",
        ["Business", "Banking", "Trading", "Crypto", "Personal Finance"]
    )

    q = st.text_area("Ask question")

    if st.button("Get Advice"):

        prompt = f"""
Finance expert.

Category: {ftype}

Question: {q}

Give simple advice + risks.
"""

        result = call_ai(prompt)

        st.write(result)
        st.download_button("📥 Download", generate_pdf(result), "finance.pdf")


# ============================================================
# 💬 CHAT ANALYZER
# ============================================================

elif mode == "💬 Chat Analyzer":

    st.header("💬 Chat Analyzer")

    chat = st.text_area("Paste chat")

    atype = st.selectbox(
        "Analysis Type",
        ["Sentiment", "Tone", "Intent", "Full Analysis"]
    )

    if st.button("Analyze"):

        result = call_ai(f"{atype} analysis:\n{chat}")

        st.write(result)
        st.download_button("📥 Download", generate_pdf(result), "chat.pdf")


# ============================================================
# 🧠 QUIZ GENERATOR
# ============================================================

elif mode == "🧠 Quiz Generator":

    st.header("🧠 Quiz Generator")

    topic = st.text_input("Topic")

    if st.button("Generate Quiz"):

        result = call_ai(f"Create 5 MCQs with answers on {topic}")

        st.write(result)


# ============================================================
# 📊 SMART PLANNER
# ============================================================

elif mode == "📊 Smart Planner":

    st.header("📊 Smart Planner")

    goal = st.text_input("Goal")
    days = st.slider("Days", 1, 30, 7)

    if st.button("Create Plan"):

        result = call_ai(f"{days}-day plan for {goal}")

        st.write(result)
        st.download_button("📥 Download", generate_pdf(result), "plan.pdf")


# ---------- FOOTER ----------
st.markdown("---")
st.markdown("### 👨‍💻 Created by **MOHAMMED.USMAN** 🚀")