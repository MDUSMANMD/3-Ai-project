import streamlit as st
import io
import os
import requests
import PyPDF2
import re
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("NVIDIA_API_KEY")

st.set_page_config(page_title="AI Resume Reviewer", page_icon="📄")

st.title("📄 AI Resume Reviewer")
st.markdown("### 🚀 Smart Resume Analysis Tool")
st.markdown("Upload your resume and get instant AI feedback")

if not API_KEY:
    st.error("API key missing in .env file")
    st.stop()

uploaded_file = st.file_uploader("📤 Upload Resume", type=["pdf","txt"])
job_role = st.text_input("🎯 Target Job Role")
analyze = st.button("🔍 Analyze Resume")


def read_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text
    return text


def read_file(file):
    if file.type == "application/pdf":
        return read_pdf(io.BytesIO(file.read()))
    else:
        return file.read().decode()


def call_ai(prompt):

    url = "https://integrate.api.nvidia.com/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "o3-mini",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.4,
        "max_tokens": 700
    }

    response = requests.post(url, headers=headers, json=data)
    result = response.json()

    if "choices" in result:
        return result["choices"][0]["message"]["content"]

    return "AI error"


def clean_format(text):

    text = text.replace("***", "")
    text = text.replace("**", "")

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


if analyze and uploaded_file:

    resume_text = read_file(uploaded_file)

    prompt = f"""
Act as an expert recruiter.

Analyze this resume for {job_role if job_role else "general jobs"}.

Return format:

Rating: X/5

Strengths:
- bullet points

Weaknesses:
- bullet points

Improvements:
- bullet points

Resume:
{resume_text}
"""

    with st.spinner("🤖 AI analyzing resume..."):
        analysis = call_ai(prompt)

    st.session_state.analysis = analysis

    rating_match = re.search(r'(\d)/5', analysis)

    st.markdown("---")
    st.header("⭐ Resume Quality Score")

    if rating_match:

        stars = int(rating_match.group(1))
        star_display = "⭐" * stars + "☆" * (5 - stars)

        if stars == 5:
            quality = "🌟 Excellent Resume"
        elif stars == 4:
            quality = "✅ Strong Resume"
        elif stars == 3:
            quality = "⚠️ Average Resume"
        elif stars == 2:
            quality = "❗ Needs Improvement"
        else:
            quality = "🚫 Poor Resume"

        st.markdown(
            f"<h1 style='text-align:center;font-size:50px'>{star_display}</h1>",
            unsafe_allow_html=True
        )

        st.markdown(
            f"<h3 style='text-align:center;color:orange'>{quality}</h3>",
            unsafe_allow_html=True
        )

    st.markdown("---")
    st.header("📊 Resume Analysis")

    strengths = re.search(r"Strengths:(.*)Weaknesses:", analysis, re.S)
    weaknesses = re.search(r"Weaknesses:(.*)Improvements:", analysis, re.S)
    improvements = re.search(r"Improvements:(.*)", analysis, re.S)

    if strengths:
        st.subheader("💪 Strengths")
        st.markdown(clean_format(strengths.group(1)), unsafe_allow_html=True)

    if weaknesses:
        st.subheader("⚠️ Weaknesses")
        st.markdown(clean_format(weaknesses.group(1)), unsafe_allow_html=True)

    if improvements:
        st.subheader("🚀 Improvements")
        st.markdown(clean_format(improvements.group(1)), unsafe_allow_html=True)


if "analysis" in st.session_state:

    st.markdown("---")
    st.header("🤖 Resume Improvement Chatbot")

    question = st.text_input("Ask AI how to improve your resume")

    if st.button("Ask AI"):

        prompt = f"""
You are a resume coach.

Resume analysis:
{st.session_state.analysis}

User question:
{question}

Give a short clear answer.
"""

        with st.spinner("🤖 AI thinking..."):
            answer = call_ai(prompt)

        st.markdown("### 🤖 AI Response")
        st.markdown(
            f"<div style='font-size:18px; line-height:1.7'>{answer}</div>",
            unsafe_allow_html=True
        )


st.markdown("---")
st.markdown("### 👨‍💻 Created by **MOHAMMED USMAN** 🚀")