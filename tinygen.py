# ====================== [TinyGen] ======================
# Copyright (C) 2024 Edward Li - All Rights Reserved
# =======================================================
from constants import REPO_TEMP_DIR
from task import Task
from processes.git_utils import (
    git_clone_repo,
    git_delete_repo,
    git_reset_repo,
    git_generate_diff
)
from processes.filesystem_io import (
    list_all_files,
    safe_read_file,
    safe_modify_file,
    safe_delete_file,
    safe_create_file
)

from traceback import format_exc
import time


class TinyGenTask(Task):
    def run_tinygen(self):
        try:
            # Start the task
            self.start()
            self.logger.info("==================================================")
            self.logger.info("Starting TinyGen task with the following parameters:")
            self.logger.info(f"Task ID: {self.task_id}")
            self.logger.info(f"Repository URL: {self.repo_url}")
            self.logger.info(f"Prompt: {self.prompt}")
            self.logger.info("==================================================")

            # Clone the repo
            self.logger.info(f"Cloning repository: {self.repo_url}")
            git_clone_repo(REPO_TEMP_DIR, self.task_id, self.repo_url)
            self.logger.info("Repository cloned successfully")

            self.logger.info("\n".join(list_all_files(REPO_TEMP_DIR, self.task_id)))
            self.logger.info(safe_read_file(REPO_TEMP_DIR, self.task_id, "README.md"))
            safe_modify_file(REPO_TEMP_DIR, self.task_id, "README.md", "This is a fake modification")
            self.logger.info(safe_read_file(REPO_TEMP_DIR, self.task_id, "README.md"))

            safe_create_file(REPO_TEMP_DIR, self.task_id, "test.txt", "WASD")
            safe_delete_file(REPO_TEMP_DIR, self.task_id, "bin/llm")

            # Fake Sleep
            time.sleep(1)

            self.logger.info(git_generate_diff(REPO_TEMP_DIR, self.task_id))

            # Fake Sleep
            time.sleep(1)

            git_reset_repo(REPO_TEMP_DIR, self.task_id)

            # Fake Sleep
            time.sleep(1)

            # Clean up the cloned repo
            self.logger.info("Cleaning up the cloned repository")
            git_delete_repo(REPO_TEMP_DIR, self.task_id)
            self.logger.info("Repository cleaned up successfully")

            # Finish the task
            self.set_result("This is a fake result")
        except Exception as e:
            # Print out the error
            self.logger.error(format_exc())

            # Set the task status to ERROR
            self.set_error(str(e))

            # Try to clean the repo folder
            try:
                git_delete_repo(REPO_TEMP_DIR, self.task_id)
                self.logger.info("Repository cleaned up successfully")
            except Exception as e:
                self.logger.error(f"Error cleaning up the cloned repository: {str(e)}")
