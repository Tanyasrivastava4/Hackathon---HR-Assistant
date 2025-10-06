# resume_parser/utils.py
import re

DEFAULT_SKILLS = [
    "python", "sql", "machine learning", "ml", "tensorflow", "pytorch",
    "data visualization", "excel", "power bi", "tableau", "java", "c++", "c"
]

def normalize_text(text: str) -> str:
    return re.sub(r'\s+', ' ', text).strip()

def extract_name(text: str) -> str:
    # simple heuristic: first occurrence of "Firstname Lastname" pattern
    match = re.search(r"\b[A-Z][a-z]{1,}\s[A-Z][a-z]{1,}\b", text)
    return match.group(0) if match else "Unknown"

def extract_skills(text: str, skill_list=None):
    if skill_list is None:
        skill_list = DEFAULT_SKILLS
    text_lower = text.lower()
    found = []
    for s in skill_list:
        if s.lower() in text_lower and s not in found:
            found.append(s)
    return found

def extract_education(text: str):
    ed = []
    patterns = [r"\bB\.?Tech\b", r"\bM\.?Tech\b", r"\bB\.?Sc\b", r"\bM\.?Sc\b", r"\bBachelor\b", r"\bMaster\b", r"\bPh\.?D\b"]
    for p in patterns:
        if re.search(p, text, re.IGNORECASE):
            ed.append(re.search(p, text, re.IGNORECASE).group(0))
    return ed if ed else ["Unknown"]

def extract_experience(text: str):
    # looks for patterns like "2 years", "3+ years", "worked for 2 years"
    matches = re.findall(r"\b\d+\+?\s?(?:years?|yrs?)\b", text, flags=re.IGNORECASE)
    return matches if matches else ["Unknown"]
