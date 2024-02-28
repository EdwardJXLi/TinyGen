# Copyright (C) 2024 Edward Li - All Rights Reserved
from task import TaskManager, Task
from tinygen import run_tinygen

import uuid
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel

# Create a FastAPI instance
app = FastAPI()

# Create a global TaskManager instance
task_manager = TaskManager()


# Define a Pydantic model for the input data
class GenerateInput(BaseModel):
    repoUrl: str
    prompt: str


@app.get("/")
async def route_root():
    return {"Hello": "World"}


@app.post("/generate")
async def route_generate(background_tasks: BackgroundTasks, data: GenerateInput):
    task: Task = task_manager.create_task(data.repoUrl, data.prompt)
    background_tasks.add_task(run_tinygen, task)
    return {"task_id": str(task.task_id)}


@app.get("/result/{task_id_str}")
async def route_get_result(task_id_str: str):
    # Convert the task_id_str to a UUID
    task_id = uuid.UUID(task_id_str)

    # Check if the task exists
    if not task_manager.task_exists(task_id):
        return {"error": f"Task {task_id_str} not found"}

    # Get the task
    task = task_manager.get_task(task_id)

    # Check if the task is done
    if not task.is_done():
        return {"task_id": str(task.task_id), "status": task.status.value}

    return {"task_id": str(task.task_id), "status": task.status.value, "result": task.result}
