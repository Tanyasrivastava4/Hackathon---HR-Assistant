# jd_generator/client.py
import requests
from schemas.jd_request import JDRequest
from jd_generator.utils import prepare_prompt
from config.env import SALAD_PUBLIC_URL
import json

TIMEOUT = 60  # seconds

def generate_jd(role: str, level: str, skills: list):
    # Validate using Pydantic schema
    req = JDRequest(role=role, level=level, skills=skills)
    payload = req.dict()

    url = f"{SALAD_PUBLIC_URL.rstrip('/')}/generate_jd"
    try:
        resp = requests.post(url, json=payload, timeout=TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        return data.get("jd") or data.get("text") or ""
    except requests.exceptions.RequestException as e:
        print("Request error to LLM server:", e)
        return None
    except ValueError:
        print("Invalid JSON response from LLM server")
        return None
