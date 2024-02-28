# ====================== [TinyGen] ======================
# Copyright (C) 2024 Edward Li - All Rights Reserved
# =======================================================
from task import TaskManager
from tinygen import run_tinygen

from fastapi import FastAPI, Request, Response, BackgroundTasks
from pydantic import BaseModel
import uuid

# Create a FastAPI instance
app = FastAPI()

# Create a global TaskManager instance
task_manager = TaskManager()


# Define a Pydantic model for the input data
class GenerateInput(BaseModel):
    repoUrl: str
    prompt: str


# === Root Route ===
@app.get("/")
async def route_root():
    return Response("TinyGen API", media_type="text/plain")


# === Start TinyGen Route ===
@app.post("/generate")
async def route_generate(request: Request, background_tasks: BackgroundTasks, data: GenerateInput):
    # Create a new task with the repo and prompt
    task = task_manager.create_task(data.repoUrl, data.prompt)

    # Start the task in the background
    background_tasks.add_task(run_tinygen, task)

    # Return the task_id and task_url
    return {"task_id": str(task.task_id), "task_url": f"{request.base_url}task/{task.task_id}"}


# === Task Status Route ===
@app.get("/task/{task_id_str}")
async def route_get_task(request: Request, task_id_str: str):
    # Convert the task_id_str to a UUID
    task_id = uuid.UUID(task_id_str)

    # Check if the task exists
    if not task_manager.task_exists(task_id):
        return {"error": f"Task {task_id_str} not found"}

    # Get the task
    task = task_manager.get_task(task_id)

    return {"task_id": str(task.task_id), "status": task.status.value, "result_url": f"{request.base_url}task/{task.task_id}/result"}


# === Task Result Route ===
@app.get("/task/{task_id_str}/result")
async def route_get_result(task_id_str: str):
    # Convert the task_id_str to a UUID
    task_id = uuid.UUID(task_id_str)

    # Check if the task exists
    if not task_manager.task_exists(task_id):
        return Response(f"Task {task_id_str} not found.", status_code=409, media_type="text/plain")

    # Get the task
    task = task_manager.get_task(task_id)

    # Check if the task is done
    if not task.is_done():
        return Response("Task Still Pending...", status_code=404, media_type="text/plain")

    # Return the result
    return Response(task.result, media_type="text/plain")


# === Task Cancel Route ===
@app.delete("/task/{task_id_str}/cancel")
async def route_cancel_task(task_id_str: str):
    # Convert the task_id_str to a UUID
    task_id = uuid.UUID(task_id_str)

    # Check if the task exists
    if not task_manager.task_exists(task_id):
        return {"error": f"Task {task_id_str} not found"}

    # Get the task
    task = task_manager.get_task(task_id)

    # Cancel the task
    task.cancel()

    return {"task_id": str(task.task_id), "status": task.status.value}
