# ====================== [TinyGen] ======================
# Copyright (C) 2024 Edward Li - All Rights Reserved
# =======================================================
from constants import REPO_TEMP_DIR
from task import Task
from processes.fs_io import clone_repo, delete_repo, list_all_files

from traceback import format_exc
import time


def run_tinygen(task: Task):
    try:
        # Start the task
        task.start()
        task.logger.info("==================================================")
        task.logger.info("Starting TinyGen task with the following parameters:")
        task.logger.info(f"Task ID: {task.task_id}")
        task.logger.info(f"Repository URL: {task.repo_url}")
        task.logger.info(f"Prompt: {task.prompt}")
        task.logger.info("==================================================")

        # Clone the repo
        task.logger.info(f"Cloning repository: {task.repo_url}")
        clone_repo(REPO_TEMP_DIR, task.task_id, task.repo_url)
        task.logger.info("Repository cloned successfully")

        task.logger.info("\n".join(list_all_files(REPO_TEMP_DIR, task.task_id)))

        # Fake Sleep
        time.sleep(3)

        # Clean up the cloned repo
        task.logger.info("Cleaning up the cloned repository")
        delete_repo(REPO_TEMP_DIR, task.task_id)
        task.logger.info("Repository cleaned up successfully")

        # Finish the task
        task.set_result("This is a fake result")
    except Exception as e:
        # Print out the error
        task.logger.error(format_exc)

        # Set the task status to ERROR
        task.set_error(str(e))

        # Try to clean the repo folder
        try:
            delete_repo(REPO_TEMP_DIR, task.task_id)
        except Exception as e:
            task.logger.error(f"Error cleaning up the cloned repository: {str(e)}")
