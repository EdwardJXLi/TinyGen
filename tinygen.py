# ====================== [TinyGen] ======================
# Copyright (C) 2024 Edward Li - All Rights Reserved
# =======================================================
from constants import REPO_TEMP_DIR
from task import Task
import processes.git_utils
import processes.filesystem_io

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
            self.clone_repo()

            self.logger.info("\n".join(self.list_all_files()))
            self.read_file("README.md")
            self.modify_file("README.md", "This is a fake modification")
            self.logger.info(self.read_file("README.md"))

            self.create_file("test.txt", "WASD")
            self.delete_file("bin/llm")

            # Fake Sleep
            time.sleep(1)

            self.logger.info(self.generate_diff())

            # Fake Sleep
            time.sleep(1)

            self.reset_repo()

            # Fake Sleep
            time.sleep(1)

            # Clean up the cloned repo
            self.delete_repo()

            # Finish the task
            self.set_result("This is a fake result")
        except Exception as e:
            # Print out the error
            self.logger.error(format_exc())

            # Set the task status to ERROR
            self.set_error(str(e))

            # Try to clean the repo folder
            try:
                self.delete_repo()
            except Exception as e:
                self.logger.error(f"Error cleaning up the cloned repository: {str(e)}")

    def clone_repo(self):
        self.logger.info(f"Cloning repository: {self.repo_url}")
        processes.git_utils.git_clone_repo(REPO_TEMP_DIR, self.task_id, self.repo_url)
        self.logger.info("Repository cloned successfully")

    def delete_repo(self):
        self.logger.info(f"Deleting repository: {self.repo_url}")
        processes.git_utils.git_delete_repo(REPO_TEMP_DIR, self.task_id)
        self.logger.info("Repository deleted successfully")

    def reset_repo(self):
        self.logger.info(f"Resetting repository: {self.repo_url}")
        processes.git_utils.git_reset_repo(REPO_TEMP_DIR, self.task_id)
        self.logger.info("Repository reset successfully")

    def generate_diff(self):
        self.logger.info(f"Generating diff for repository: {self.repo_url}")
        diff = processes.git_utils.git_generate_diff(REPO_TEMP_DIR, self.task_id)
        self.logger.info("Diff generated successfully")
        return diff

    def list_all_files(self):
        self.logger.info(f"Listing all files in repository: {self.repo_url}")
        files = processes.filesystem_io.list_all_files(REPO_TEMP_DIR, self.task_id)
        self.logger.info("Files listed successfully")
        return files

    def read_file(self, filename: str):
        self.logger.info(f"Reading file {filename}")
        content = processes.filesystem_io.safe_read_file(REPO_TEMP_DIR, self.task_id, filename)
        self.logger.info("File read successfully")
        return content

    def modify_file(self, filename: str, content: str):
        self.logger.info(f"Modifying file {filename}")
        processes.filesystem_io.safe_modify_file(REPO_TEMP_DIR, self.task_id, filename, content)
        self.logger.info("File modified successfully")

    def delete_file(self, filename: str):
        self.logger.info(f"Deleting file {filename}")
        processes.filesystem_io.safe_delete_file(REPO_TEMP_DIR, self.task_id, filename)
        self.logger.info("File deleted successfully")

    def create_file(self, filename: str, content: str):
        self.logger.info(f"Creating file {filename}")
        processes.filesystem_io.safe_create_file(REPO_TEMP_DIR, self.task_id, filename, content)
        self.logger.info("File created successfully")
