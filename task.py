# ====================== [TinyGen] ======================
# Copyright (C) 2024 Edward Li - All Rights Reserved
# =======================================================
import uuid
import logging

from enum import Enum
from datetime import datetime
from typing import Optional

from utils.supabase import Supabase
from constants import SUPABASE_PROJECT_URL, SUPABASE_API_KEY


# TaskStatus is an enumeration of the possible statuses of a task
class TaskStatus(Enum):
    CREATED = "CREATED"
    PENDING = "PENDING"
    DONE = "DONE"
    ERROR = "ERROR"
    CANCELLED = "CANCELLED"


# Logger handler to keep track of logs
class ListHandler(logging.Handler):
    def __init__(self, logs_list: list[str]):
        super().__init__()
        self.logs_list = logs_list

    def emit(self, record):
        log_entry = self.format(record)
        self.logs_list.append(log_entry)


class Task:
    """
    A Task class to keep track of a TinyGen task state
    """
    def __init__(self, task_id: uuid.UUID, repo_url: str, prompt: str, openai_key: str | None = None):
        # Initialize the task
        self.task_id: uuid.UUID = task_id
        self.repo_url: str = repo_url
        self.prompt: str = prompt
        self.openai_key: str | None = openai_key
        self.status: TaskStatus = TaskStatus.CREATED
        self.result: Optional[str] = None
        self.start_time: datetime = datetime.now()
        self.end_time: Optional[datetime] = None
        self.elapsed_time: Optional[float] = None
        self.logs: list[str] = []  # Initialize logs list

        # Setup custom logger
        self.logger: logging.Logger = self._setup_logger(task_id)

        # Set up a supabase client stub. If supabase is enabled, the client object will be injected by the task manager
        self.supabase: Optional[Supabase] = None

    def _setup_logger(self, task_id: uuid.UUID) -> logging.Logger:
        logger = logging.getLogger(str(task_id))
        logger.setLevel(logging.INFO)
        logger.propagate = False  # Fix log duplication bug

        # Clear existing handlers
        logger.handlers = []

        # Create handlers
        c_handler = logging.StreamHandler()
        list_handler = ListHandler(self.logs)  # Use the custom handler

        # Create formatters and add them to the handlers
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        c_handler.setFormatter(formatter)
        list_handler.setFormatter(formatter)

        # Add handlers to the logger
        logger.addHandler(c_handler)
        logger.addHandler(list_handler)

        return logger

    def update_status(self, status: TaskStatus):
        # Update the status of the task
        self.status = status

        # Update the end time and elapsed time if the task is done
        if status in [TaskStatus.DONE, TaskStatus.ERROR, TaskStatus.CANCELLED]:
            self.end_time = datetime.now()
            self.elapsed_time = (self.end_time - self.start_time).total_seconds()

        # If supabase is enabled, update the status in the supabase table
        if self.supabase:
            self.supabase.update_query(self)

    def running(self) -> bool:
        # Check if the task is running
        return self.status == TaskStatus.PENDING

    def is_done(self) -> bool:
        # Check if the task is done
        return self.status in [TaskStatus.DONE, TaskStatus.ERROR, TaskStatus.CANCELLED]

    def start(self):
        # Start the task
        self.update_status(TaskStatus.PENDING)
        self.logger.info(f"Task {self.task_id} started.")

    def set_result(self, result: str):
        # Set the result of the task
        self.result = result
        self.update_status(TaskStatus.DONE)
        self.logger.info(f"Task {self.task_id} finished in {self.elapsed_time} seconds!")

    def set_error(self, error: str):
        # Set the error of the task
        self.result = error
        self.update_status(TaskStatus.ERROR)
        self.logger.error(f"Task {self.task_id} failed!.")

    def cancel(self):
        # Cancel the task
        self.update_status(TaskStatus.CANCELLED)
        self.logger.warning(f"Task {self.task_id} cancelled.")

    def connect_supabase(self, supabase: Supabase):
        # Connect the supabase client to the task
        self.supabase = supabase
        self.logger.info(f"Task {self.task_id} connected to Supabase {supabase.project_url}.")


class TaskManager:
    """
    A simple in-memory task manager.
    """

    def __init__(self):
        # Create an in-memory storage for tasks
        # TODO: In the future, you can replace the in-memory storage with the supabase table
        self.tasks: dict[uuid.UUID, Task] = {}

        # If both supabase project url and api key are non-empty, create a supabase client
        # Else, set it to None
        if SUPABASE_PROJECT_URL and SUPABASE_API_KEY:
            # Create a supabase client to log tasks
            self.supabase = Supabase(SUPABASE_PROJECT_URL, SUPABASE_API_KEY)
        else:
            # Do not use supabase
            self.supabase = None

    def add_task(self, task: Task):
        # Add a new task to the in-memory storage
        self.tasks[task.task_id] = task

        # If supabase is enabled, inject the supabase dependency
        if self.supabase:
            # Connect the task to the supabase client
            task.connect_supabase(self.supabase)

            # Add the task to the supabase table
            self.supabase.add_query(task)

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

    def get_task_summary(self):
        # Get a summary of the tasks
        # Loop through all tasks and count the number of tasks in each status
        summary = {"pending": 0, "finished": 0, "errored": 0, "cancelled": 0, "other": 0}
        for task in self.tasks.values():
            if task.status == TaskStatus.PENDING:
                summary["pending"] += 1
            elif task.status == TaskStatus.DONE:
                summary["finished"] += 1
            elif task.status == TaskStatus.ERROR:
                summary["errored"] += 1
            elif task.status == TaskStatus.CANCELLED:
                summary["cancelled"] += 1
            else:
                summary["other"] += 1
        return summary
