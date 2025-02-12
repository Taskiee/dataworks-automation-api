from fastapi import FastAPI
import subprocess
import json
import sqlite3
import os
import requests
import markdown
import csv
import shutil
from bs4 import BeautifulSoup
from datetime import datetime
from PIL import Image
import speech_recognition as sr

def ensure_data_security(filepath):
    """Ensure the file path is within /data and does not attempt deletion."""
    if not filepath.startswith("/data"):
        raise PermissionError("Access outside /data is not allowed")
    if "rm " in filepath or "delete" in filepath:
        raise PermissionError("File deletion is not allowed")

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
        "B3": fetch_api_data,
        "B4": clone_git_repo,
        "B5": run_sql_query,
        "B6": scrape_website,
        "B7": compress_image,
        "B8": transcribe_audio,
        "B9": convert_markdown_to_html,
        "B10": filter_csv_data,
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
# Existing A1-A10 functions (kept unchanged)

def fetch_api_data():
    response = requests.get("https://jsonplaceholder.typicode.com/todos/1")
    data = response.json()
    with open("/data/api_data.json", "w") as f:
        json.dump(data, f, indent=2)
    return "API data fetched and saved"

def clone_git_repo():
    subprocess.run(["git", "clone", "https://github.com/example/repo.git", "/data/repo"], check=True)
    return "Git repository cloned"

def run_sql_query():
    conn = sqlite3.connect("/data/database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    with open("/data/sql_result.txt", "w") as f:
        f.write(str(count))
    conn.close()
    return f"SQL query executed, count: {count}"

def scrape_website():
    response = requests.get("https://example.com")
    soup = BeautifulSoup(response.text, "html.parser")
    data = soup.find("h1").text
    with open("/data/scraped_data.txt", "w") as f:
        f.write(data)
    return "Website scraped and data saved"

def compress_image():
    img = Image.open("/data/image.png")
    img.save("/data/image_compressed.jpg", "JPEG", quality=50)
    return "Image compressed"

def transcribe_audio():
    recognizer = sr.Recognizer()
    with sr.AudioFile("/data/audio.mp3") as source:
        audio = recognizer.record(source)
    text = recognizer.recognize_google(audio)
    with open("/data/audio_transcript.txt", "w") as f:
        f.write(text)
    return "Audio transcribed"

def convert_markdown_to_html():
    with open("/data/document.md") as f:
        md_content = f.read()
    html_content = markdown.markdown(md_content)
    with open("/data/document.html", "w") as f:
        f.write(html_content)
    return "Markdown converted to HTML"

def filter_csv_data():
    with open("/data/data.csv") as f:
        reader = csv.DictReader(f)
        filtered_data = [row for row in reader if row["status"] == "active"]
    with open("/data/filtered_data.json", "w") as f:
        json.dump(filtered_data, f, indent=2)
    return "Filtered CSV data saved as JSON"
