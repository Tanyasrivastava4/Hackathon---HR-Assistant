# jd_generator/utils.py
from utils.prompts import generate_jd_prompt

def prepare_prompt(role: str, level: str, skills: list):
    # optionally add fallback or sanitization here
    skills = skills or []
    return generate_jd_prompt(role=role, level=level, skills=skills)
