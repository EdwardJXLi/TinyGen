# ====================== [TinyGen] ======================
# Copyright (C) 2024 Edward Li - All Rights Reserved
# =======================================================
from enum import Enum
import uuid
import logging
from datetime import datetime
from typing import Optional


# TaskStatus is an enumeration of the possible statuses of a task
class TaskStatus(Enum):
    CREATED = "CREATED"
    PENDING = "PENDING"
    DONE = "DONE"
    ERROR = "ERROR"
    CANCELLED = "CANCELLED"


class Task:
    """
    A Task class to keep track of a TinyGen task state
    """
    def __init__(self, task_id: uuid.UUID, repo_url: str, prompt: str):
        # Initialize the task
        self.task_id: uuid.UUID = task_id
        self.repo_url: str = repo_url
        self.prompt: str = prompt
        self.status: TaskStatus = TaskStatus.CREATED
        self.result: Optional[str] = None
        self.start_time: datetime = datetime.now()
        self.end_time: Optional[datetime] = None
        self.elapsed_time: Optional[float] = None

        # Setup custom logger
        self.logger = self._setup_logger(task_id)

    def _setup_logger(self, task_id: uuid.UUID) -> logging.Logger:
        logger = logging.getLogger(str(task_id))
        logger.setLevel(logging.INFO)

        # Create handlers
        c_handler = logging.StreamHandler()

        # Create formatters and add them to the handlers
        c_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        c_handler.setFormatter(c_format)

        # Add handlers to the logger
        logger.addHandler(c_handler)

        return logger

    def update_status(self, status: TaskStatus):
        # Update the status of the task
        self.status = status

        # Update the end time and elapsed time if the task is done
        if status in [TaskStatus.DONE, TaskStatus.ERROR, TaskStatus.CANCELLED]:
            self.end_time = datetime.now()
            self.elapsed_time = (self.end_time - self.start_time).total_seconds()

    def running(self) -> bool:
        # Check if the task is running
        return self.status == TaskStatus.PENDING

    def is_done(self) -> bool:
        # Check if the task is done
        return self.status in [TaskStatus.DONE, TaskStatus.ERROR, TaskStatus.CANCELLED]

    def start(self):
        # Start the task
        self.update_status(TaskStatus.PENDING)

    def set_result(self, result: str):
        # Set the result of the task
        self.result = result
        self.update_status(TaskStatus.DONE)

    def set_error(self, error: str):
        # Set the error of the task
        self.result = error
        self.update_status(TaskStatus.ERROR)

    def cancel(self):
        # Cancel the task
        self.update_status(TaskStatus.CANCELLED)


class TaskManager:
    """
    A simple in-memory task manager.
    """

    def __init__(self):
        # Create an in-memory storage for tasks
        # TODO: In the future, you can replace this with a database
        self.tasks: dict[uuid.UUID, Task] = {}

    def create_task(self, repo_url: str, prompt: str) -> Task:
        # Create a unique TaskID
        task_id = uuid.uuid4()

        # Create Task
        task = Task(task_id, repo_url, prompt)

        # Store the task in the in-memory storage
        self.tasks[task.task_id] = task
        print(f"Task {task.task_id} created.")

        return task

    def task_exists(self, task_id: uuid.UUID) -> bool:
        # Check if the task exists in the in-memory storage
        return task_id in self.tasks

    def get_task(self, task_id: uuid.UUID) -> Task:
        # Get the task from the in-memory storage
        # If the task is not found, raise a KeyError
        if task_id in self.tasks:
            return self.tasks[task_id]
        else:
            raise KeyError(f"Task {task_id} not found.")

    def get_num_running_tasks(self) -> int:
        # Count the number of running tasks
        return sum(1 for task in self.tasks.values() if not task.is_done())
