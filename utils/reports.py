# utils/reports.py
import pandas as pd
import os

LOG_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "activity_logs.csv")

def generate_reports():
    logs_path = os.path.abspath(LOG_FILE)
    if not os.path.exists(logs_path):
        return {"message": "No logs available"}

    df = pd.read_csv(logs_path)
    total_actions = len(df)
    unique_users = df["username"].nunique() if "username" in df.columns else 0
    most_active_user = df["username"].value_counts().idxmax() if total_actions else None
    actions_summary = df["action"].value_counts().to_dict() if "action" in df.columns else {}
    return {
        "total_actions": int(total_actions),
        "unique_users": int(unique_users),
        "most_active_user": most_active_user,
        "actions_summary": actions_summary
    }
