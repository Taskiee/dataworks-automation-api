from fastapi import FastAPI
import subprocess
import json
import sqlite3
import os
from datetime import datetime

app = FastAPI()

def run_task(task_id):
    task_map = {
        "A1": run_datagen,
        "A2": format_markdown,
        "A3": count_wednesdays,
        "A4": sort_contacts,
        "A5": extract_recent_logs,
        "A6": index_markdown_files,
        "A7": extract_email,
        "A8": extract_credit_card,
        "A9": find_similar_comments,
        "A10": calculate_gold_ticket_sales,
    }

    if task_id in task_map:
        result = task_map[task_id]()
        return {"status": "success", "task_id": task_id, "result": result}
    
    return {"status": "error", "message": "Invalid task ID"}

@app.get("/run/{task_id}")
def execute_task(task_id: str):
    return run_task(task_id)

def run_datagen():
    subprocess.run(["uv", "install"], check=True)
    return subprocess.run(["python", "datagen.py", "23f1001906@ds.study.iitm.ac.in"], check=True, capture_output=True).stdout.decode()

def format_markdown():
    subprocess.run(["npx", "prettier@3.4.2", "--write", "/data/format.md"], check=True)
    return "Markdown formatted"

def count_wednesdays():
    with open("/data/dates.txt") as f:
        dates = [datetime.strptime(line.strip(), "%Y-%m-%d") for line in f]
    count = sum(1 for d in dates if d.weekday() == 2)
    with open("/data/dates-wednesdays.txt", "w") as f:
        f.write(str(count))
    return count

def sort_contacts():
    with open("/data/contacts.json") as f:
        contacts = json.load(f)
    contacts.sort(key=lambda c: (c["last_name"], c["first_name"]))
    with open("/data/contacts-sorted.json", "w") as f:
        json.dump(contacts, f, indent=2)
    return "Contacts sorted"

def extract_recent_logs():
    log_files = sorted(os.listdir("/data/logs"), key=lambda f: os.path.getmtime(os.path.join("/data/logs", f)), reverse=True)[:10]
    lines = [open(os.path.join("/data/logs", log)).readline().strip() for log in log_files]
    with open("/data/logs-recent.txt", "w") as f:
        f.write("\n".join(lines))
    return "Recent logs extracted"

def index_markdown_files():
    index = {}
    for filename in os.listdir("/data/docs"):
        if filename.endswith(".md"):
            with open(f"/data/docs/{filename}") as f:
                for line in f:
                    if line.startswith("# "):
                        index[filename] = line[2:].strip()
                        break
    with open("/data/docs/index.json", "w") as f:
        json.dump(index, f, indent=2)
    return "Markdown indexed"

def extract_email():
    with open("/data/email.txt") as f:
        email_content = f.read()
    sender_email = "extracted@example.com"  # Placeholder for LLM API
    with open("/data/email-sender.txt", "w") as f:
        f.write(sender_email)
    return sender_email

def extract_credit_card():
    card_number = "4111111111111111"  # Placeholder for LLM API
    with open("/data/credit-card.txt", "w") as f:
        f.write(card_number)
    return card_number

def find_similar_comments():
    with open("/data/comments.txt") as f:
        comments = f.readlines()
    most_similar = (comments[0], comments[1])  # Placeholder logic
    with open("/data/comments-similar.txt", "w") as f:
        f.write("\n".join(most_similar))
    return "Similar comments found"

def calculate_gold_ticket_sales():
    conn = sqlite3.connect("/data/ticket-sales.db")
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(units * price) FROM tickets WHERE type = 'Gold'")
    total_sales = cursor.fetchone()[0] or 0
    with open("/data/ticket-sales-gold.txt", "w") as f:
        f.write(str(total_sales))
    conn.close()
    return total_sales
