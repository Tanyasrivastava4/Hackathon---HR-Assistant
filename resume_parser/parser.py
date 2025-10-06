# resume_parser/parser.py
import os
from pathlib import Path
from .utils import normalize_text, extract_name, extract_skills, extract_education, extract_experience

# PDF and DOCX reading
def _read_pdf(path):
    try:
        from pdfminer.high_level import extract_text
    except Exception as e:
        raise RuntimeError("pdfminer.six is required to parse PDF files. Install via requirements.") from e
    return extract_text(path)

def _read_docx(path):
    try:
        from docx import Document
    except Exception as e:
        raise RuntimeError("python-docx is required to parse DOCX files. Install via requirements.") from e
    doc = Document(path)
    return "\n".join([p.text for p in doc.paragraphs])

def parse_resume(file_path: str):
    file_path = str(file_path)
    if file_path.lower().endswith(".pdf"):
        text = _read_pdf(file_path)
    elif file_path.lower().endswith(".docx"):
        text = _read_docx(file_path)
    else:
        raise ValueError("Unsupported resume format: only .pdf and .docx are supported")

    text = normalize_text(text)
    return {
        "name": extract_name(text),
        "skills": extract_skills(text),
        "education": extract_education(text),
        "experience": extract_experience(text),
        "source_file": os.path.basename(file_path)
    }

def parse_resume_folder(folder_path: str):
    folder = Path(folder_path)
    results = []
    for file in folder.iterdir():
        if file.is_file() and file.suffix.lower() in [".pdf", ".docx"]:
            try:
                parsed = parse_resume(str(file))
                results.append(parsed)
            except Exception as e:
                # skip problematic file but continue
                results.append({"name": "ParseError", "skills": [], "education": [], "experience": [], "source_file": file.name})
    return results
