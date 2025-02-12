from fastapi import FastAPI
from tasks import execute_task  # Import the function correctly

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "DataWorks Automation API is running"}

@app.post("/run-task/{task_id}")
def run_task(task_id: str):
    """Executes a given task based on task_id"""
    result = execute_task(task_id)
    return {"task_id": task_id, "status": result}
