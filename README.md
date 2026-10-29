# 🎯 CareerPilot: Your AI Career Copilot

One Streamlit app with seven Gemini-powered tools that help students and early-career professionals with the job search, from the resume to the interview and the learning plan afterwards.

## Features

| Tool | What it does |
|---|---|
| 💬 **Career Chatbot** | Streaming chat with memory of the conversation, focused on career questions |
| 📑 **Resume Analyzer** | Upload a PDF (or paste text) and get a score, ATS check, missing keywords and before/after bullet rewrites |
| ✍️ **Cover Letter Generator** | Letter tailored to a job description, using only facts from your resume |
| 💼 **LinkedIn Post Generator** | Choose tone, length and audience, with optional hashtags |
| 🎤 **Interview Question Generator** | Role- and level-specific questions with what interviewers look for and answer outlines |
| 📝 **Skill Gap Analysis** | Compares your skills with a target role and ranks what to learn first |
| 🗺️ **Learning Roadmap Generator** | Week-by-week plan based on your goal, level and weekly hours |

Every result can be downloaded as a Markdown file.

## Tech stack

Python · Streamlit · Google Gen AI SDK (`google-genai`) · pypdf · prompt engineering

## Project structure

```
careerpilot/
├── app.py          # Streamlit UI: seven pages and navigation
├── prompts.py      # All prompt templates and the system prompt
├── utils.py        # Gemini calls, PDF reading, settings, error handling
├── requirements.txt
└── .streamlit/
    └── secrets.toml.example
```

## Run it locally

```bash
# 1. Create and activate a virtual environment (recommended)
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add your Gemini API key (free at https://aistudio.google.com/apikey)
copy .streamlit\secrets.toml.example .streamlit\secrets.toml     # Windows
# cp .streamlit/secrets.toml.example .streamlit/secrets.toml     # macOS / Linux
# then open secrets.toml and paste your key

# 4. Start the app
streamlit run app.py
```

No `secrets.toml`? You can paste your key into the sidebar while the app is running.

## Deploy (optional)

Push the repo to GitHub, create an app on [Streamlit Community Cloud](https://streamlit.io/cloud) pointing at `app.py`, and add `GEMINI_API_KEY` under **Advanced settings → Secrets**.

## Design notes

- **Grounded outputs:** the cover letter and resume prompts forbid inventing experience, and the skill gap tool only uses skills the user states.
- **Safe key handling:** the API key comes from `secrets.toml`, an environment variable, or the sidebar. It is never hard-coded and `secrets.toml` is git-ignored.
- **Configurable model:** the default model is `DEFAULT_MODEL` in `utils.py`. Override it from the sidebar or with `GEMINI_MODEL`. Gemini retires older models regularly, so update it if you see a "model not available" message.
- **Clear failures:** friendly messages for invalid keys, rate limits, unavailable models and scanned PDFs.
- **Privacy:** resume text is sent to the Gemini API to produce results. Don't upload anything you aren't comfortable sharing with that service.

## Limitations

- Scanned (image-only) PDFs aren't supported because there is no OCR step.
- Only the first 60,000 characters of a PDF are used.
- AI feedback is a starting point, not a replacement for a human reviewer.

## Ideas for next steps

- n8n workflow that posts generated LinkedIn content on a schedule (see my LinkedIn automation project)
- Save chat history and past results to a database
- Compare a resume against a pasted job description with a match score
- OCR support for scanned resumes
