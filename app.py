"""CareerPilot: a Streamlit app with seven Gemini-powered career tools."""

import streamlit as st

import prompts
from utils import (
    MAX_PDF_CHARS,
    extract_pdf_text,
    friendly_error,
    generate,
    sidebar_settings,
    stream_chat,
)

st.set_page_config(page_title="CareerPilot", page_icon="🎯", layout="wide")

TONES = ["Professional", "Friendly", "Formal", "Confident", "Enthusiastic", "Funny"]
# Chat history sent to the model. Odd number keeps the first message a "user" turn.
MAX_CHAT_MESSAGES = 19


# ----------------------------------------------------------------- helpers
def need_key() -> bool:
    """Warn and return True if there is no API key yet."""
    if not api_key:
        st.warning("Add your Gemini API key in the sidebar to continue.")
        return True
    return False


def run(result_key: str, prompt: str, temperature: float = 0.7) -> None:
    """Generate text and keep it in session state so it survives reruns."""
    if need_key():
        return
    with st.spinner("Working on it..."):
        try:
            st.session_state[result_key] = generate(
                api_key, model, prompt, prompts.SYSTEM_COACH, temperature
            )
        except Exception as exc:
            st.error(friendly_error(exc))


def show(result_key: str, filename: str) -> None:
    """Display a stored result with a download button."""
    result = st.session_state.get(result_key)
    if result:
        st.divider()
        st.markdown(result)
        st.download_button("Download as .md", result, file_name=filename, key=f"dl_{result_key}")


def resume_input(prefix: str, label: str = "Your resume") -> str:
    """Let the user upload a PDF or paste text. Returns the resume text ('' if none)."""
    st.subheader(label)
    tab_pdf, tab_text = st.tabs(["Upload PDF", "Paste text"])
    pdf_text = ""
    with tab_pdf:
        uploaded = st.file_uploader("Upload resume (PDF)", type="pdf", key=f"{prefix}_pdf")
        if uploaded:
            try:
                pdf_text, pages, truncated = extract_pdf_text(uploaded.getvalue())
            except Exception:
                st.error("I couldn't read that file. Is it a valid, unencrypted PDF?")
            else:
                if not pdf_text:
                    st.warning("No selectable text found. This looks like a scanned PDF; paste the text instead.")
                else:
                    st.caption(f"{pages} page(s) · {len(pdf_text):,} characters read")
                    if truncated:
                        st.warning(f"Long file: only the first {MAX_PDF_CHARS:,} characters are used.")
    with tab_text:
        pasted = st.text_area("Paste resume text", height=220, key=f"{prefix}_text")
    st.caption("Your resume text is sent to the Gemini API to generate the result.")
    return pdf_text or pasted.strip()


# ------------------------------------------------------------------ pages
def page_chatbot() -> None:
    st.header("💬 Career Chatbot")
    st.caption("Ask about careers, skills, internships, resumes, interviews, or what to learn next.")

    history = st.session_state.setdefault("chat", [])
    if st.sidebar.button("Clear chat"):
        st.session_state["chat"] = []
        st.rerun()

    if not history:
        st.info("Try: *What skills do I need to become an ML engineer, and where should I start?*")
    for message in history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input("Ask a career question")
    if not question or need_key():
        return

    history.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)
    with st.chat_message("assistant"):
        try:
            reply = st.write_stream(
                stream_chat(api_key, model, history[-MAX_CHAT_MESSAGES:], prompts.SYSTEM_COACH)
            )
        except Exception as exc:
            st.error(friendly_error(exc))
            history.pop()  # drop the unanswered question
            return
    history.append({"role": "assistant", "content": reply})


def page_resume() -> None:
    st.header("📑 Resume Analyzer")
    st.caption("Upload your resume and get a score, ATS check, and concrete rewrites.")
    resume = resume_input("resume")
    role = st.text_input("Target role (optional)", placeholder="e.g. Machine Learning Intern")
    if st.button("Analyze resume", type="primary"):
        if not resume:
            st.warning("Upload or paste your resume first.")
        else:
            run("resume_result", prompts.resume_analysis(resume, role), temperature=0.4)
    show("resume_result", "resume_feedback.md")


def page_cover_letter() -> None:
    st.header("✍️ Cover Letter Generator")
    st.caption("A tailored letter built only from what is actually in your resume.")
    col1, col2 = st.columns(2)
    role = col1.text_input("Job title", placeholder="e.g. Junior Data Analyst")
    company = col2.text_input("Company", placeholder="e.g. Acme Corp")
    tone = st.selectbox("Tone", TONES)
    job_description = st.text_area("Job description", height=200)
    resume = resume_input("cover")
    if st.button("Generate cover letter", type="primary"):
        if not (role.strip() and job_description.strip() and resume):
            st.warning("Please fill in the job title, job description and your resume.")
        else:
            run("cover_result", prompts.cover_letter(resume, job_description, company, role, tone))
    show("cover_result", "cover_letter.md")


def page_linkedin() -> None:
    st.header("💼 LinkedIn Post Generator")
    topic = st.text_input("Topic", placeholder="e.g. What I learned building my first Streamlit app")
    col1, col2 = st.columns(2)
    tone = col1.selectbox("Tone", TONES + ["Inspirational"])
    length = col2.selectbox("Length", ["Short (~80 words)", "Medium (~150 words)", "Long (~250 words)"], index=1)
    audience = st.text_input("Audience (optional)", placeholder="e.g. hiring managers, fellow students")
    hashtags = st.checkbox("Include hashtags", value=True)
    if st.button("Generate post", type="primary"):
        if not topic.strip():
            st.warning("Please enter a topic.")
        else:
            run("linkedin_result", prompts.linkedin_post(topic, tone, length, audience, hashtags), 0.9)
    show("linkedin_result", "linkedin_post.md")


def page_interview() -> None:
    st.header("🎤 Interview Question Generator")
    role = st.text_input("Role", placeholder="e.g. Data Scientist")
    col1, col2, col3 = st.columns(3)
    level = col1.selectbox("Level", ["Fresher / Intern", "Junior", "Mid-level", "Senior"])
    kind = col2.selectbox("Type", ["Technical", "Behavioral", "HR", "Mixed"])
    count = col3.slider("Number of questions", 5, 15, 8)
    if st.button("Generate questions", type="primary"):
        if not role.strip():
            st.warning("Please enter a role.")
        else:
            run("interview_result", prompts.interview_questions(role, level, kind, count))
    show("interview_result", "interview_questions.md")


def page_skill_gap() -> None:
    st.header("📝 Skill Gap Analysis")
    st.caption("Compare what you know with what your target role needs.")
    role = st.text_input("Target role", placeholder="e.g. AI Engineer")
    skills = st.text_area(
        "Your current skills",
        height=140,
        placeholder="e.g. Python (good), SQL (basic), Streamlit, Git, pandas",
    )
    with st.expander("Add your resume for extra context (optional)"):
        resume = resume_input("gap")
    if st.button("Analyze skill gap", type="primary"):
        if not role.strip() or not (skills.strip() or resume):
            st.warning("Please enter a target role and your skills (or a resume).")
        else:
            run("gap_result", prompts.skill_gap(skills, role, resume), temperature=0.4)
    show("gap_result", "skill_gap.md")


def page_roadmap() -> None:
    st.header("🗺️ Learning Roadmap Generator")
    goal = st.text_input("Your goal", placeholder="e.g. Become job-ready as a machine learning engineer")
    level = st.selectbox("Current level", ["Complete beginner", "Some basics", "Intermediate"])
    col1, col2 = st.columns(2)
    weeks = col1.slider("Weeks", 4, 26, 12)
    hours = col2.slider("Hours per week", 3, 30, 8)
    if st.button("Generate roadmap", type="primary"):
        if not goal.strip():
            st.warning("Please enter your goal.")
        else:
            run("roadmap_result", prompts.learning_roadmap(goal, level, weeks, hours))
    show("roadmap_result", "learning_roadmap.md")


PAGES = {
    "💬 Career Chatbot": page_chatbot,
    "📑 Resume Analyzer": page_resume,
    "✍️ Cover Letter": page_cover_letter,
    "💼 LinkedIn Post": page_linkedin,
    "🎤 Interview Questions": page_interview,
    "📝 Skill Gap Analysis": page_skill_gap,
    "🗺️ Learning Roadmap": page_roadmap,
}

# ------------------------------------------------------------------- main
st.title("🎯 CareerPilot")
st.caption("Your AI copilot for the job search")
selected = st.sidebar.radio("Tools", list(PAGES))
st.sidebar.divider()
api_key, model = sidebar_settings()
PAGES[selected]()
