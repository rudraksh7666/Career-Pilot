"""Prompt templates for every feature (prompt engineering lives here)."""

SYSTEM_COACH = (
    "You are an experienced career coach and technical recruiter who helps "
    "students and early-career professionals, especially in AI and software. "
    "Be specific, honest and practical. Use Markdown with short headings and "
    "bullet points. Never invent facts about the user: if information is "
    "missing, say what you assumed."
)


def resume_analysis(resume: str, target_role: str) -> str:
    role = target_role.strip() or "a general entry-level role in the candidate's field"
    return f"""Review the resume below for the target role: {role}.

Give your feedback in exactly these sections:
1. **Overall score** (out of 10) with a one-line reason
2. **Strengths** (3-5 bullets)
3. **Weaknesses** (3-5 bullets)
4. **ATS and formatting check** (keywords, length, structure, readability)
5. **Missing keywords or skills** for the target role
6. **Bullet-point rewrites**: pick the 3 weakest bullets and show Before / After.
   Only rephrase what is already stated; do not invent achievements or numbers.
7. **Top 5 action items**, most important first

Resume:
\"\"\"
{resume}
\"\"\""""


def cover_letter(resume: str, job_description: str, company: str, role: str, tone: str) -> str:
    return f"""Write a cover letter for the role "{role}" at {company or "the company"}.

Tone: {tone}
Length: 250-350 words, 3-4 short paragraphs, no placeholders like [Your Name]
except one "Sincerely," sign-off line.

Rules:
- Use ONLY experience, skills and projects that appear in the resume. Do not invent anything.
- Match the candidate's real strengths to the job description's key requirements.
- Open with something specific to the role or company, not "I am writing to apply".

Resume:
\"\"\"
{resume}
\"\"\"

Job description:
\"\"\"
{job_description}
\"\"\""""


def linkedin_post(topic: str, tone: str, length: str, audience: str, hashtags: bool) -> str:
    tags = "End with 3-5 relevant hashtags." if hashtags else "Do not use hashtags."
    return f"""Write a LinkedIn post about: {topic}

Tone: {tone}
Length: {length}
Audience: {audience or "professionals and students in tech"}

Requirements:
- Start with a strong first line that makes people click "see more".
- Short paragraphs, plenty of white space, at most 2 emojis.
- Include one concrete insight or example, and end with a question or call to action.
- {tags}
Return only the post text."""


def interview_questions(role: str, level: str, kind: str, count: int) -> str:
    return f"""Generate {count} {kind} interview questions for a {level} {role} candidate.

For each question give:
- **Question**
- **What the interviewer is looking for** (one line)
- **Strong answer outline** (2-3 bullets)

Order from easier to harder. End with 3 smart questions the candidate can ask the interviewer."""


def skill_gap(current_skills: str, target_role: str, resume: str) -> str:
    background = current_skills.strip() or "(none typed)"
    resume_block = f'\nResume (optional extra context):\n"""\n{resume}\n"""\n' if resume else ""
    return f"""Do a skill gap analysis for someone targeting the role: {target_role}.

Current skills (as stated by the user): {background}
{resume_block}
Respond with:
1. **Skills you already have that match the role**
2. **Skill gap table**: Markdown table with columns Skill | Importance (High/Med/Low) | Your level (None/Basic/Good) | Gap
3. **Top 5 priorities** to learn first, and why
4. **Quick wins** achievable in 30 days
5. **Portfolio project ideas** (3) that would prove these skills

Base "your level" only on what the user stated; mark unknown as "Not stated"."""


def learning_roadmap(goal: str, level: str, weeks: int, hours: int) -> str:
    return f"""Create a {weeks}-week learning roadmap.

Goal: {goal}
Current level: {level}
Time available: {hours} hours per week

Format:
- A one-paragraph overview of the approach
- For each week (or block of weeks): **Focus**, **What to learn**, **Practice task**, **Checkpoint** (how to know it is done)
- One portfolio mini-project every 3-4 weeks, with a clear deliverable for GitHub
- Finish with a short "what next" section

Keep each week realistic for {hours} hours. Suggest types of resources (official docs, free courses, books) rather than inventing specific URLs."""
