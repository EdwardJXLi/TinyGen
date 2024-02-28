# ====================== [TinyGen] ======================
# Copyright (C) 2024 Edward Li - All Rights Reserved
# =======================================================
import processes.git_utils
import processes.filesystem_io
from constants import REPO_TEMP_DIR, OPENAI_API_KEY
from task import Task
from processes.openai import OpenAIInteraction
from typing import Iterable

from traceback import format_exc


class TinyGenTask(Task):
    def run_tinygen(self):
        try:
            # Start the task
            self.start()
            self.logger.info("")
            self.logger.info("==================================================")
            self.logger.info("> [Starting TinyGen task with the following parameters] ")
            self.logger.info(f"> Task ID: {self.task_id}")
            self.logger.info(f"> Repository URL: {self.repo_url}")
            self.logger.info(f"> Prompt: {self.prompt}")
            self.logger.info("==================================================")
            self.logger.info("")

            # Start up OpenAI Interaction Layer
            self.openai = OpenAIInteraction(self, OPENAI_API_KEY)

            # Clone the repo
            self.clone_repo()

            # Get the list of all files in the repository
            file_list = self.list_all_files()

            # Ask TinyGen to determine the relevant files
            relavant_files = self.step_determine_relevant_files(self.prompt, file_list)

            # TODO
            self.logger.info(relavant_files)

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

    def step_determine_relevant_files(self, user_prompt: str, file_list: Iterable[str]) -> Iterable[str]:
        # Begin to determine relevant files
        self.logger.info("==================================================")
        self.logger.info("> [STEP] : Determining Relevant Files from User Prompt")
        self.logger.info(f"> User Prompt: {user_prompt}")
        self.logger.info("> Available Files:")
        for file in file_list:
            self.logger.info(f"> - {file}")
        self.logger.info("==================================================")

        # Format file list as a string
        formatted_file_list = '\n'.join(file_list)

        # Generate messages for OpenAI
        messages = [
            {
                "role": "system",
                "content": "You are TinyGen, a code generation assistant specialized in understanding and processing user requests to generate or modify code.\n"
                        "Your current task is to analyze the user's request and identify which files in the existing directory are relevant to this request. "
                        "Below is a list of files currently available in the directory. Your goal is to filter out only those files that may be relevant to accomplishing the user's request. "
                        "Available files in the directory:\n"
                        f"{formatted_file_list}\n\n"
                        "With the user's request in mind, first talk through your thought process and brainstorm which files you think are relevant. Files that are deemed optional should be included as well.\n"
                        "Remember to include all file types, such as 'readme', 'requirements', or others, that might typically be overlooked but could be crucial depending on the request.\n\n"
                        "User's request:\n"
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ]

        # Get the response from OpenAI
        self.logger.info("Asking OpenAI to determine relevant files...")
        response_message = self.openai.generate(messages)

        # Append the context onto the response
        messages.append(response_message)  # type: ignore

        # Ask follow up question to get the list of relevant files
        messages.append(
            {
                "role": "system",
                "content": "Based on the detailed information provided and the context of the user's request, please identify and list all files that are relevant and potentially impacted. "
                        "This includes not only the files directly mentioned in the user's request but also any additional files that could be affected by the proposed changes or are necessary for the implementation of these changes. "
                        "Consider configuration files, documentation, dependencies listed in files like 'requirements.txt' or 'package.json', and any other files that might be indirectly influenced.\n"
                        "Your response should comprehensively cover every file that needs attention, ensuring that no potentially relevant file is overlooked. "
                        "This includes files that are explicitly requested to be modified, as well as those that might need updates or modifications due to the ripple effects of the requested changes. "
                        "Remember, the goal is to provide a complete list that will guide the successful modification or enhancement of the project without missing any critical components.\n"
                        "For clarity and ease of reference, list each file path on a separate line, without additional commentary or formatting. "
                        "Your thoroughness in this task is crucial for the accurate and efficient execution of the requested changes.\n\n"
                        "Example response for a web application project might include not only source code but also configuration and documentation files:\n"
                        "app.py\n"
                        "templates/index.html\n"
                        "static/style.css\n"
                        "requirements.txt\n"
                        "README.md\n\n"
                        "In another scenario, for a software project undergoing significant modification, your response might look like:\n"
                        "src/main.py\n"
                        "src/utils/helpers.py\n"
                        "tests/test_main.py\n"
                        ".env.example\n"
                        "requirements.txt\n"
                        "README.md\n\n"
                        "Please provide your detailed response now. Only include files that exist!\n"
            }
        )

        # Get follow up response from OpenAI
        self.logger.info("Asking OpenAI to format relevant files into a list...")
        response_message = self.openai.generate(messages)

        # Format and return message from OpenAI
        formatted_relavant_files = response_message.content or ""
        relavant_files = formatted_relavant_files.split()

        # Log the relevant files
        self.logger.info("[STEP] Relevant Files Generated!")
        for file in relavant_files:
            self.logger.info(f" - {file}")

        return relavant_files

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
        return files

    def read_file(self, filename: str):
        self.logger.info(f"Reading file {filename}")
        content = processes.filesystem_io.safe_read_file(REPO_TEMP_DIR, self.task_id, filename)
        return content

    def modify_file(self, filename: str, content: str):
        self.logger.info(f"Modifying file {filename}")
        processes.filesystem_io.safe_modify_file(REPO_TEMP_DIR, self.task_id, filename, content)

    def delete_file(self, filename: str):
        self.logger.info(f"Deleting file {filename}")
        processes.filesystem_io.safe_delete_file(REPO_TEMP_DIR, self.task_id, filename)

    def create_file(self, filename: str, content: str):
        self.logger.info(f"Creating file {filename}")
        processes.filesystem_io.safe_create_file(REPO_TEMP_DIR, self.task_id, filename, content)
