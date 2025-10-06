# app.py
import streamlit as st
import pandas as pd
import os
import datetime
from pathlib import Path

# local imports
from resume_parser.parser import parse_resume_folder
from jd_generator.client import generate_jd
from offer_manager.generator import generate_offer_letter
from utils.reports import generate_reports
from config.env import SALAD_PUBLIC_URL

# -------------------------
# Setup and constants
# -------------------------
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
RESUME_DIR = DATA_DIR / "resumes"
PARSED_CSV = DATA_DIR / "parsed_data.csv"
USERS_FILE = DATA_DIR / "users.csv"
LOG_FILE = DATA_DIR / "activity_logs.csv"
OFFERS_DIR = DATA_DIR / "reports" / "offers"

os.makedirs(RESUME_DIR, exist_ok=True)
os.makedirs(OFFERS_DIR, exist_ok=True)
os.makedirs(DATA_DIR / "reports", exist_ok=True)

# create users file and logs if not exist
if not os.path.exists(USERS_FILE):
    pd.DataFrame([{"username": "admin", "password": "admin123", "role": "admin"},
                  {"username": "hr1", "password": "hr123", "role": "hr"}]).to_csv(USERS_FILE, index=False)

if not os.path.exists(LOG_FILE):
    pd.DataFrame(columns=["timestamp", "username", "action"]).to_csv(LOG_FILE, index=False)

# -------------------------
# Utility helpers
# -------------------------
def log_activity(username: str, action: str):
    df = pd.read_csv(LOG_FILE)
    df = pd.concat([df, pd.DataFrame([{
        "timestamp": datetime.datetime.now().isoformat(),
        "username": username,
        "action": action
    }])], ignore_index=True)
    df.to_csv(LOG_FILE, index=False)

def authenticate(username: str, password: str):
    users = pd.read_csv(USERS_FILE)
    match = users[(users["username"] == username) & (users["password"] == password)]
    if not match.empty:
        return match.iloc[0]["role"]
    return None

# -------------------------
# Streamlit UI
# -------------------------
st.set_page_config(page_title="HR Workflow Automator", layout="wide")
st.title("🤖 HR Workflow Automator")

# Login panel
st.sidebar.header("🔐 Login")
username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")
login_clicked = st.sidebar.button("Login")

if login_clicked:
    role = authenticate(username, password)
    if not role:
        st.sidebar.error("Invalid credentials")
    else:
        st.session_state["username"] = username
        st.session_state["role"] = role
        st.sidebar.success(f"Welcome {username} ({role})")

if "username" not in st.session_state:
    st.info("Please login from the sidebar to continue.")
    st.stop()

current_user = st.session_state["username"]
current_role = st.session_state["role"]

st.sidebar.markdown(f"**Signed in as:** `{current_user}`  \n**Role:** `{current_role}`")
st.sidebar.markdown("---")
st.sidebar.markdown(f"LLM Server: `{SALAD_PUBLIC_URL}`")

# Role-based menu
if current_role == "hr":
    menu = st.sidebar.radio("HR Modules", ["Upload & Parse Resumes", "Generate JD", "Offer Manager", "View Parsed Data"])
elif current_role == "admin":
    menu = st.sidebar.radio("Admin Modules", ["User Management", "Activity Reports", "System Summary"])
else:
    st.error("Unknown role")
    st.stop()

# -------------------------
# HR: Upload & Parse
# -------------------------
if current_role == "hr" and menu == "Upload & Parse Resumes":
    st.header("📄 Upload & Parse Resumes")
    uploaded_files = st.file_uploader("Upload PDF or DOCX resumes", type=["pdf", "docx"], accept_multiple_files=True)
    if uploaded_files:
        for file in uploaded_files:
            target = RESUME_DIR / file.name
            with open(target, "wb") as f:
                f.write(file.getbuffer())
        st.success(f"Uploaded {len(uploaded_files)} file(s) to `{RESUME_DIR}`")
        parsed = parse_resume_folder(str(RESUME_DIR))
        df = pd.DataFrame(parsed)
        df.to_csv(PARSED_CSV, index=False)
        st.dataframe(df)
        log_activity(current_user, f"Uploaded and parsed {len(uploaded_files)} resumes")

# -------------------------
# HR: Generate JD
# -------------------------
elif current_role == "hr" and menu == "Generate JD":
    st.header("🧾 Job Description Generator")
    role_input = st.text_input("Role (e.g., Data Scientist)")
    level = st.selectbox("Level", ["Intern", "Junior", "Mid", "Senior"])
    skills_input = st.text_area("Skills (comma-separated) — optional")
    skills_list = [s.strip() for s in skills_input.split(",") if s.strip()] if skills_input else []

    if st.button("Generate JD"):
        if not role_input or not level:
            st.error("Role and level are required")
        else:
            with st.spinner("Generating JD from LLM…"):
                jd = generate_jd(role=role_input, level=level, skills=skills_list)
            if jd:
                st.subheader("Generated JD")
                st.text_area("Job Description", jd, height=300)
                log_activity(current_user, f"Generated JD for {role_input} ({level})")
            else:
                st.error("Failed to generate JD. Check LLM server connection.")

# -------------------------
# HR: Offer Manager
# -------------------------
elif current_role == "hr" and menu == "Offer Manager":
    st.header("📜 Offer Letter Generator")
    # show list of parsed candidates if available
    candidates = []
    if os.path.exists(PARSED_CSV):
        df = pd.read_csv(PARSED_CSV)
        candidates = df["name"].dropna().unique().tolist()

    candidate_name = st.selectbox("Select candidate", ["-- new --"] + candidates)
    if candidate_name == "-- new --":
        candidate_name = st.text_input("Candidate Full Name")

    position = st.text_input("Position")
    salary = st.text_input("Salary (ex: ₹6 LPA)")
    start_date = st.date_input("Start Date")

    if st.button("Generate Offer"):
        if not candidate_name or not position or not salary:
            st.error("Fill candidate name, position and salary")
        else:
            output_path = generate_offer_letter(
                candidate_name=candidate_name,
                position=position,
                salary=salary,
                start_date=str(start_date)
            )
            st.success(f"Offer letter generated: {output_path}")
            log_activity(current_user, f"Generated offer for {candidate_name}")

# -------------------------
# HR: View Parsed Data
# -------------------------
elif current_role == "hr" and menu == "View Parsed Data":
    st.header("📂 Parsed Resumes")
    if os.path.exists(PARSED_CSV):
        df = pd.read_csv(PARSED_CSV)
        st.dataframe(df)
    else:
        st.info("No parsed data found. Upload resumes first.")

# -------------------------
# Admin: User Management
# -------------------------
elif current_role == "admin" and menu == "User Management":
    st.header("👥 User Management")
    users_df = pd.read_csv(USERS_FILE)
    st.dataframe(users_df)

    st.subheader("Add a new user")
    new_username = st.text_input("Username")
    new_password = st.text_input("Password", type="password")
    new_role = st.selectbox("Role", ["hr", "admin"])
    if st.button("Add User"):
        if new_username and new_password:
            users_df = pd.concat([users_df, pd.DataFrame([{"username": new_username, "password": new_password, "role": new_role}])], ignore_index=True)
            users_df.to_csv(USERS_FILE, index=False)
            st.success(f"User {new_username} added")
            log_activity(current_user, f"Added user {new_username}")
        else:
            st.error("Provide username and password")

# -------------------------
# Admin: Activity Reports
# -------------------------
elif current_role == "admin" and menu == "Activity Reports":
    st.header("📊 Activity Logs")
    if os.path.exists(LOG_FILE):
        logs = pd.read_csv(LOG_FILE)
        st.dataframe(logs)
        csv = logs.to_csv(index=False)
        st.download_button("Download logs (CSV)", csv, file_name="activity_logs.csv")
    else:
        st.info("No logs available")

# -------------------------
# Admin: System Summary
# -------------------------
elif current_role == "admin" and menu == "System Summary":
    st.header("📈 System Summary")
    report = generate_reports()
    st.json(report)
