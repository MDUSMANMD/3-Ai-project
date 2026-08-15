# NovaMind AI

NovaMind AI is a Streamlit workspace that combines education support, career feedback, document analysis, and a lightweight usage dashboard in one application. It uses an NVIDIA-compatible chat-completions endpoint and accepts common PDF, DOCX, TXT, Markdown, CSV, and image uploads.

## Features

- **Education assistant:** summarize study material, explain difficult concepts, and answer follow-up questions.
- **Career assistant:** review a resume for a target role, identify missing skills, and suggest ATS-friendly improvements.
- **Finance document assistant:** analyze uploaded financial documents with an explicit reminder that the output is general information rather than personalized financial advice.
- **File analyzer:** extract text from supported files and return structured summaries and recommended next actions.
- **Downloadable reports:** export generated results as PDF files.
- **Session memory:** ask follow-up questions within each module during the current Streamlit session.
- **Usage dashboard:** view module usage for the current session.

## Quick start

### 1. Create an environment

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

### 2. Configure the API key

Copy `.env.example` to `.env` for local development, or add the same key to Streamlit secrets when deploying:

```bash
cp .env.example .env
```

The required setting is `NVIDIA_API_KEY`. You can optionally set `NVIDIA_MODEL` and `NOVAMIND_MAX_INPUT_CHARS`.

### 3. Run the application

```bash
streamlit run main.py
```

## Configuration

| Variable | Required | Default | Purpose |
|---|---:|---|---|
| `NVIDIA_API_KEY` | Yes | None | API credential for the chat-completions endpoint. |
| `NVIDIA_MODEL` | No | `meta/llama-3.1-70b-instruct` | Model identifier sent to the endpoint. |
| `NOVAMIND_MAX_INPUT_CHARS` | No | `24000` | Maximum text sent in one request to limit oversized uploads. |

Never commit `.env`, Streamlit secrets, or API keys. The repository includes a `.gitignore` that excludes common secret and local-environment files.

## Project structure

```text
.
├── main.py             # Streamlit application
├── requirements.txt     # Runtime dependencies
├── .env.example         # Safe configuration template
└── README.md            # Project documentation
```

## Responsible use

Uploaded files are processed in memory by the application and their text may be sent to the configured AI provider when an analysis is requested. Do not upload confidential material unless you understand the provider, retention, and access implications. Finance output is informational only and is not a substitute for advice from a qualified professional.

## Roadmap

The next useful improvements are persistent user accounts, evaluation fixtures for prompt quality, provider abstraction, structured JSON responses, and an optional database-backed history view.

## License

No license has been selected yet. Add a license before accepting external contributions or redistributing the project.
