from fastapi import FastAPI
from api import tasks

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "DataWorks Automation API is running"}

@app.post("/run-task/{task_id}")
def run_task(task_id: str):
    return tasks.execute_task(task_id)
