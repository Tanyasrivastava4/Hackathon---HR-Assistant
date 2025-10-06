# utils/prompts.py
def generate_jd_prompt(role: str, level: str, skills: list):
    skills_text = ", ".join(skills) if skills else ""
    prompt = (
        "You are an assistant that writes professional and DEI-compliant job descriptions.\n\n"
        f"Role: {role}\n"
        f"Level: {level}\n"
        f"Skills: {skills_text}\n\n"
        "Produce a clear, concise, and inclusive job description. "
        "Avoid biased language and encourage candidates from diverse backgrounds to apply. "
        "Include: short summary, responsibilities, required skills, desired qualifications, and benefits (if applicable)."
    )
    return prompt
