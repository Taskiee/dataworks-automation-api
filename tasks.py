import os
import openai
from fastapi import FastAPI, HTTPException, Query
import subprocess
import json
import sqlite3
import requests
import markdown
from bs4 import BeautifulSoup
from datetime import datetime
from PIL import Image
import whisper
import pandas as pd

app = FastAPI()

# Use AI Proxy token from environment variable
AIPROXY_TOKEN = os.environ.get("AIPROXY_TOKEN")
if not AIPROXY_TOKEN:
    raise ValueError("AIPROXY_TOKEN environment variable is not set.")

openai.api_key = AIPROXY_TOKEN  # Secure API key usage

# Function to call GPT-4o-Mini via AI Proxy
def call_llm(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": "You are a concise, efficient automation assistant."},
                  {"role": "user", "content": prompt}]
    )
    return response["choices"][0]["message"]["content"].strip()

# Task execution function
@app.post("/run")
def execute_task(task: str = Query(..., description="Natural language task description")):
    """Executes a task based on natural language input."""
    task = task.lower()

    if "format" in task and "prettier" in task:
        return {"status": "success", "task": "format_markdown", "result": format_markdown()}
    if "count wednesdays" in task:
        return {"status": "success", "task": "count_wednesdays", "result": count_wednesdays()}
    if "sort contacts" in task:
        return {"status": "success", "task": "sort_contacts", "result": sort_contacts()}
    if "extract email" in task:
        return {"status": "success", "task": "extract_email", "result": extract_email()}
    if "transcribe audio" in task:
        return {"status": "success", "task": "transcribe_audio", "result": transcribe_audio()}
    
    # If no match, send to LLM for dynamic processing
    llm_result = call_llm(f"Execute: {task}")
    return {"status": "llm-executed", "task": task, "result": llm_result}

# File content retrieval endpoint for evaluation
@app.get("/read")
def read_file(path: str = Query(..., description="Path to file inside /data/")):
    """Reads a file's contents securely from /data/."""
    if not path.startswith("/data/"):
        raise HTTPException(status_code=403, detail="Access to this file is forbidden.")
    
    try:
        with open(path, "r") as f:
            return {"status": "success", "path": path, "content": f.read()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")

#  A2: Format Markdown with Prettier (dynamic version handling)
def format_markdown():
    subprocess.run(["npx", "prettier@3.4.2", "--write", "/data/format.md"], check=True)
    return "Markdown formatted with Prettier"

#  A3: Count Wednesdays
def count_wednesdays():
    with open("/data/dates.txt") as f:
        dates = [datetime.strptime(line.strip(), "%Y-%m-%d") for line in f]
    count = sum(1 for d in dates if d.weekday() == 2)
    with open("/data/dates-wednesdays.txt", "w") as f:
        f.write(str(count))
    return count

# A4: Sort Contacts
def sort_contacts():
    with open("/data/contacts.json") as f:
        contacts = json.load(f)
    contacts.sort(key=lambda c: (c["last_name"], c["first_name"]))
    with open("/data/contacts-sorted.json", "w") as f:
        json.dump(contacts, f, indent=2)
    return "Contacts sorted"

# A5: Extract Recent Logs
def extract_recent_logs(_=None):
    log_files = sorted(os.listdir("/data/logs"), key=lambda f: os.path.getmtime(os.path.join("/data/logs", f)), reverse=True)[:10]
    lines = [open(os.path.join("/data/logs", log)).readline().strip() for log in log_files]
    with open("/data/logs-recent.txt", "w") as f:
        f.write("\n".join(lines))
    return "Recent logs extracted"

# A6: Index Markdown Files
def query_llm(text):
    """
    Calls GPT-4o-Mini via AI Proxy to generate a summary of the Markdown file.
    """
    if not AIPROXY_TOKEN:
        raise ValueError("AIPROXY_TOKEN environment variable is not set.")

    url = "https://api.aiproxy.io/v1/run"  # AI Proxy endpoint
    headers = {"Authorization": f"Bearer {AIPROXY_TOKEN}"}
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are an AI that extracts key insights from Markdown files."},
            {"role": "user", "content": f"Summarize this Markdown file:\n{text}"}
        ]
    }
    
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        return response.json().get("choices", [{}])[0].get("message", {}).get("content", "").strip()
    else:
        return "Error: LLM request failed"
#A6 Markdown


# A7: Extract Email Using LLM
def extract_email():
    with open("/data/email.txt") as f:
        email_content = f.read()
    sender_email = call_llm(f"Extract sender email from: {email_content}")
    with open("/data/email-sender.txt", "w") as f:
        f.write(sender_email)
    return sender_email

# A8: Extract Credit Card Using LLM
def extract_credit_card(_=None):
    card_number = call_llm("Extract the credit card number from /data/credit-card.png")
    with open("/data/credit-card.txt", "w") as f:
        f.write(card_number.replace(" ", ""))
    return card_number

#  A9: Find Similar Comments Using LLM
def find_similar_comments(_=None):
    with open("/data/comments.txt") as f:
        comments = f.readlines()
    similarity_result = call_llm(f"Find the two most similar comments from: {comments}")
    with open("/data/comments-similar.txt", "w") as f:
        f.write(similarity_result)
    return similarity_result

#  A10: Calculate Gold Ticket Sales
def calculate_gold_ticket_sales(_=None):
    conn = sqlite3.connect("/data/ticket-sales.db")
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(units * price) FROM tickets WHERE type = 'Gold'")
    total_sales = cursor.fetchone()[0] or 0
    with open("/data/ticket-sales-gold.txt", "w") as f:
        f.write(str(total_sales))
    conn.close()
    return total_sales

#  B3: Fetch API Data
def fetch_api_data(api_url):
    response = requests.get(api_url)
    with open("/data/api-response.json", "w") as f:
        json.dump(response.json(), f, indent=2)
    return "API data fetched"

#  B4: Clone Git Repo
def clone_git_repo(repo_url):
    subprocess.run(["git", "clone", repo_url, "/data/repo"], check=True)
    return "Repo cloned"

#  B5: Run SQL Query
def run_sql_query(query):
    conn = sqlite3.connect("/data/database.db")
    cursor = conn.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    conn.close()
    return result

#  B6: Scrape Website
def scrape_website(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    text = soup.get_text()
    with open("/data/scraped.txt", "w") as f:
        f.write(text)
    return "Website scraped"

#  B7: Compress Image
def compress_resize_image(image_path):
    img = Image.open(image_path)
    img.resize((800, 600)).save("/data/image_resized.jpg", quality=80)
    return "Image resized"

#  B8: Transcribe Audio
def transcribe_audio(audio_path):
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    with open("/data/transcription.txt", "w") as f:
        f.write(result["text"])
    return "Audio transcribed"

#  B9: Convert Markdown to HTML
def convert_md_to_html(md_path):
    html_content = markdown.markdown(open(md_path).read())
    with open("/data/output.html", "w") as f:
        f.write(html_content)
    return "Markdown converted to HTML"

#  B10: Filter CSV
def filter_csv_via_api(filter_criteria):
    df = pd.read_csv("/data/input.csv")
    df.query(filter_criteria).to_json("/data/filtered.json", orient="records")
    return "Filtered CSV saved"



TASKS = {
    "A2": format_markdown,
    "A3": count_wednesdays,
    "A4": sort_contacts,
    "A7": extract_email,
    "A8": transcribe_audio,
    "B3": fetch_api_data,
    "B4": clone_git_repo,
    "B5": run_sql_query,
    "B6": scrape_website,
    "B7": compress_resize_image,
    "B9": convert_md_to_html,
    "B10": filter_csv_via_api,
}

def execute_task(task_id: str, *args):
    if task_id in TASKS:
        return TASKS[task_id](*args) if args else TASKS[task_id]()
    raise ValueError(f"Unknown task ID: {task_id}")
