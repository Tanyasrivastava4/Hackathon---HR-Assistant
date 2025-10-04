from fastapi import FastAPI, Request, HTTPException
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch
import os

# -----------------------------
# Configuration
MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.1"

# FastAPI App
app = FastAPI(title="HR Assistant LLM Server")

# Load Model
# -----------------------------
print("Loading Mistral-7B model...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    device_map="auto",
    torch_dtype=torch.float16
)
generator = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    device_map="auto",
    torch_dtype=torch.float16
)
print("Model loaded successfully!")

# -----------------------------
# Health Endpoint
# -----------------------------
@app.get("/health")
async def health():
    return {"status": "ok", "model": MODEL_NAME}

# -----------------------------
# Generate JD Endpoint
# -----------------------------
@app.post("/generate_jd")
async def generate_jd(request: Request):
    # Verify webhook secret
    secret = request.headers.get("X-WEBHOOK-SECRET")
    if secret != WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail="Unauthorized: Invalid webhook secret")

    # Get request JSON
    data = await request.json()
    role = data.get("role")
    level = data.get("level")
    skills = data.get("skills", [])

    if not role or not level:
        raise HTTPException(status_code=400, detail="Missing role or level")

    # Build prompt
    skills_text = ", ".join(skills)
    prompt = (
        f"Generate a DEI-compliant job description for a {level} {role} role. "
        f"Include these skills if relevant: {skills_text}. "
        f"Make it inclusive, professional, and clear."
    )

    # Generate JD
    try:
        jd_text = generator(prompt, max_new_tokens=300, do_sample=True, temperature=0.7)[0]["generated_text"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating JD: {e}")

    return {"jd": jd_text}

#uvicorn server:app --host '::' --port 8000 --reload   to start the server

#pip install huggingface_hub
#huggingface-cli login
