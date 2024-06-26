# ====================== [TinyGen] ======================
# Copyright (C) 2024 Edward Li - All Rights Reserved
# =======================================================
import json
from traceback import format_exc

import utils.git
import utils.filesystem_io
from utils.openai import OpenAIInteraction, FUNCTIONS
from constants import REPO_TEMP_DIR, OPENAI_API_KEY, MAX_RETRIES
from task import Task


class TinyGenTask(Task):
    def run_tinygen(self):
        """
        Start the primary TinyGen AI Task.

        The following steps are taken:

        1. Clone the repository

        2. Get the list of all files in the repository

        3. Begin the ML loop:
        |
        |> 3.1. Ask TinyGen to determine the relevant files
        |
        |> 3.2. Ask TinyGen to think through its changes in plain text
        |
        |> 3.3. Ask TinyGen to convert these changes to functions
        |  |
        |  |> 3.3.1. Ask for an initial bunch of functions to run
        |  |
        |  |> 3.3.2. Ask if more functions are needed
        |  |
        |  |> 3.3.3. Repeat until no more functions are needed
        |
        |> 3.4. Apply the changes
        |
        |> 3.5. Ask TinyGen if it is satisfied with the changes
        |  |
        |  |> 3.5.1. If not, reset the repository and try again
        |  |
        |  |> 3.5.2. If yes, continue
        |

        4. Generate the diff of the files changes in the repository

        5. Clean up and finish the task
        """
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

            # Get OpenAI Key
            if not self.openai_key:
                self.logger.warn("OpenAI API Key not provided. Using default key.")
                self.openai_key = OPENAI_API_KEY
                if not self.openai_key:
                    self.logger.error("OpenAI API Key not provided. Exiting task.")
                    self.set_error("OpenAI API Key not provided.")
                    return

            # Start up OpenAI Interaction Layer
            self.gpt = OpenAIInteraction(self, self.openai_key)

            # Clone the repo
            self.clone_repo()

            # Get the list of all files in the repository
            file_list = self.list_all_files()

            # Keep retrying until the AI is satisfied with its answer
            for retry_id in range(MAX_RETRIES):
                # Ask TinyGen to determine the relevant files
                relevent_files = self.step_determine_relevant_files(self.prompt, file_list)

                # Ask TinyGen to think through its changes
                proposed_changes = self.step_propose_changes(self.prompt, relevent_files)

                # Ask TinyGen to convert these changes to functions
                function_calls = self.step_generate_functions(self.prompt, proposed_changes, relevent_files)

                # Apply the changes
                self.step_apply_functions(function_calls, relevent_files)

                # Ask TinyGen if it is satisfied with the changes
                # TODO: Feed the AI's own feedback on its previous attempt into the next attempt!
                if self.step_ask_if_done(self.prompt, relevent_files):
                    self.logger.info("TinyGen is satisfied with the changes!")
                    break

                # Reset the repository
                self.logger.info("TinyGen is not satisfied with the changes. Resetting the repository and trying again...")
                self.reset_repo()

            # Generate Diffs
            diff = self.generate_diff()

            # Clean up the cloned repo
            self.delete_repo()

            # Finish the task
            self.set_result(diff)
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

    def step_determine_relevant_files(self, user_prompt: str, file_list: list[str]) -> list[str]:
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
                "content": "You are TinyGen, a code generation assistant specialized in accurately understanding and processing user requests to generate, modify, or delete code, documentation, or other project-related files.\n"
                        "Your primary task is to analyze the user's request and develop a single, optimal solution to fulfill it.\n"
                        "Your current task is to analyze the user's request and identify which files in the existing directory are relevant to this request.\n"
                        "If the user's request is in the form of a problem, try to fix it. If the user's request is in the form of a missing feature, try to add it.\n"
                        "Below is a list of files currently available in the directory. Your goal is to filter out only those files that may be relevant to accomplishing the user's request. "
                        "Available files in the directory:\n"
                        f"{formatted_file_list}\n\n"
                        "With the user's request in mind, first talk through your thought process and brainstorm which files you think are relevant. Files that are deemed optional should be included as well.\n"
                        "Remember to include all file types, such as 'readme', 'requirements', or others, that might typically be overlooked but could be crucial depending on the request.\n"
                        "If you determine that no files are relevant to the user's request, please respond with NO RESPONSE. "
                        "Only respond with NO RESPONSE if you are ABSOLUTELY sure there are not files that could possibly satisfy the user's request."
                        "User's request:\n"
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ]

        # Get the response from OpenAI
        self.logger.info("Asking OpenAI to determine relevant files...")
        response_message = self.gpt.generate(messages)

        # Check if if no files are relavant
        if not response_message.content or "NO RESPONSE" in response_message.content.strip():
            self.logger.warn("OpenAI did not find any relevant files.")
            return []

        # Append the context onto the response
        messages.append(response_message)  # type: ignore

        # Ask follow up question to get the list of relevant files
        messages.append(
            {
                "role": "system",
                "content": "You should no longer respond with NO RESPONSE. You should now provide a list of files that are relevant to the user's request."
                        "Based on the detailed information provided and the context of the user's request, please identify and list all files that are relevant and potentially impacted. "
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
                        "Please provide your detailed response now. Only respond with a list of files! Do not respond with a message!!!\n"
            }
        )

        # Get follow up response from OpenAI
        self.logger.info("Asking OpenAI to format relevant files into a list...")
        response_message = self.gpt.generate(messages)

        # Check if if no files are relavant
        if not response_message.content or "NO RESPONSE" in response_message.content.strip():
            self.logger.warn("OpenAI did not find any relevant files.")
            return []

        # Format and return message from OpenAI
        formatted_relavant_files = response_message.content or ""
        relavant_files = formatted_relavant_files.split()

        # Filter any invalid files generated
        relavant_files = self.filter_invalid_files(relavant_files)

        # Log the relevant files
        self.logger.info("[STEP] Relevant Files Generated!")
        for file in relavant_files:
            self.logger.info(f" - {file}")

        return relavant_files

    def step_propose_changes(self, user_prompt: str, relevant_files: list[str]) -> str:
        # Begin to think through changes
        self.logger.info("==================================================")
        self.logger.info("> [STEP] : Thinking Through Changes")
        self.logger.info(f"> User Prompt: {user_prompt}")
        self.logger.info("> Available Files:")
        for file in relevant_files:
            self.logger.info(f"> - {file}")
        self.logger.info("==================================================")

        # Generate messages for OpenAI
        messages = [
            {
                "role": "system",
                "content": "You are TinyGen, a code generation assistant specialized in accurately understanding and processing user requests to generate, modify, or delete code, documentation, or other project-related files.\n"
                        "Your primary task is to analyze the user's request and develop a single, optimal solution to fulfill it.\n"
                        "The user request may be in a form of a prompt, or it may be in a form of a ticket or issue description."
                        "Here's how to approach different types of requests:\n"
                        "For Problem-solving Requests: If the user presents a problem, focus on identifying and fixing it with a clear, concise solution.\n"
                        "For Feature Addition Requests: If the user asks for a new feature, detail how to incorporate it effectively into the existing codebase or project structure.\n"
                        "For Documentation and Non-code Requests: If the request involves creating or updating documentation (e.g., README.md), prioritize content creation, formatting, and organization over code generation."
                        "\n\n"
                        "Your current task is to analyze the user's request and brainstorm a single solution in order to fulfill the user's request. "
                        "If the user's request is in the form of a problem, try to fix it. If the user's request is in the form of a missing feature, try to add it.\n"
                        "This is a crucial step in the process, as it sets the stage for the next step where you'll be asked to actually make the changes to the codebase.\n"
                        "Do not include multiple solutions or options in your response. Provide the single solution that you believe is the best and easiest way to fulfill the user's request. "
                        "Do not attempt to do anything more than what the user has asked for. If the user's request is unclear or ambiguous, make your best judgment based on the information provided.\n"
                        "Try not to create or modify too many unnecessary files, and ensure that the changes you propose are relevant to the user's request.\n"
                        "Based on the user's request and a list of potentially relevant files you've identified, start by talking through your thought process and brainstorming the changes that need to be made. "
                        "Note that not all files listed may be useful for fulfilling the user's request, so be sure to only include changes that are directly relevant to the user's request.\n"
                        "List out the changes in clear distinct steps. Write 1-2 sentences for each step detailing thought process behind the change. "
                        "Give code changes that need to be made, as well as any new files that need to be added or existing files that need to be modified or deleted.\n"
                        "If actual code changes are needed, write the code out. Do not leave any stubs or pseudocode. Avoid writing things like '// Implement the rest of the function here'"
                        "Write production-level code that you would be comfortable running in a real-world codebase.\n"
                        "Feel free to delete any irrelevant files if you think they are no longer required.\n"
                        "Below are any potentially relevant files, wrapped in XML tags. (Example: <file><name>/path/to/file</name><content>FILE CONTENTS HERE</content></file>):\n"

            },
            {
                "role": "user",
                "content": self.encode_files(relevant_files)
            },
            {
                "role": "system",
                "content": "User Prompt:\n"
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ]

        # Get the response from OpenAI
        self.logger.info("Asking OpenAI to think through changes...")
        response_message = self.gpt.generate(messages, model="gpt-4-turbo-preview")

        return response_message.content or "No Response"

    def step_generate_functions(self, user_prompt: str, proposed_changes: str, relevant_files: list[str]):
        # Begin to determine relevant files
        self.logger.info("==================================================")
        self.logger.info("> [STEP] : Converting Proposed Instructions to Functions")
        self.logger.info(f"> User Prompt: {user_prompt}")
        self.logger.info("==================================================")

        # Keep Track of Function Steps
        function_steps = []

        # Generate messages for OpenAI
        messages = [
            {
                "role": "system",
                "content": "You are TinyGen, a code generation assistant specialized in accurately understanding and processing user requests to generate, modify, or delete code, documentation, or other project-related files.\n"
                        "Your job is to now perform the necessary changes to the codebase to fulfill the user's request. \n"
                        "Ensure to cover all aspects of the changes discussed, including updates to documentation, dependencies, and any specific file content alterations.\n"
                        "Do not try to do anything more than what is listed in the proposed changes.\n"
                        "If any of the relevant files are not used as part of the proposed changes, do not do anything to them.\n"
                        "If any of the relevant files require no changes, do not do anything to them.\n"
                        "Below are the proposed changes:\n"

            },
            {
                "role": "user",
                "content": proposed_changes
            },
            {
                "role": "system",
                "content": "Below are any potentially relevant files, wrapped in XML tags. (Example: <file><name>/path/to/file</name><content>FILE CONTENTS HERE</content></file>):\n"
            },
            {
                "role": "user",
                "content": self.encode_files(relevant_files)
            }
        ]

        # Keep asking for functions until no more are needed
        while True:
            # Get the response from OpenAI
            response_message = self.gpt.generate(messages, tools=FUNCTIONS, temperature=0.2)

            # Append the context onto the response
            messages.append(response_message)  # type: ignore

            # Get the tool calls from the response
            tool_calls = response_message.tool_calls

            # If there are tool calls, format and add them to the function steps
            if tool_calls:
                for tool_call in tool_calls:
                    # Add the function call to the function steps
                    function_steps.append({
                        "function": tool_call.function.name,
                        "arguments": json.loads(tool_call.function.arguments)
                    })
                    # Fake a function response to prompt OpenAI to generate the next function
                    messages.append(
                        {
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": tool_call.function.name,
                            "content": "ok",
                        }
                    )

                # Prompt OpenAI to generate the next function
                messages.append({"role": "system", "content": "Now, apply any more changes you deem fit. Do not try not to repeat and previous functions you have already called. If no more functions are needed, respond with 'done'."})
            else:
                # No more functions are needed
                break

        self.logger.info(f"{len(function_steps)} Functions Generated!")
        return function_steps

    def step_apply_functions(self, function_calls: list[dict], relevent_files: list[str]):
        # Begin to apply functions
        self.logger.info("==================================================")
        self.logger.info("> [STEP] : Applying Functions")
        self.logger.info("==================================================")

        # Apply each function
        for function_call in function_calls:
            try:
                match function_call:
                    case {"function": "modify_file", "arguments": {"file_path": file_path, "content": content}}:
                        self.modify_file(file_path, content)
                    case {"function": "create_file", "arguments": {"file_path": file_path, "content": content}}:
                        relevent_files.append(file_path)
                        self.create_file(file_path, content)
                    case {"function": "delete_file", "arguments": {"file_path": file_path}}:
                        relevent_files.remove(file_path)
                        self.delete_file(file_path)
                    case _:
                        self.logger.warn(f"Unknown function call: {function_call}")
            except Exception as e:
                self.logger.error(f"Error applying function: {str(e)}")

    def step_ask_if_done(self, user_prompt: str, relevant_files: list[str]):
        # Begin to determine relevant files
        self.logger.info("==================================================")
        self.logger.info("> [STEP] : Asking if the AI is Done")
        self.logger.info(f"> User Prompt: {user_prompt}")
        self.logger.info("> Relevant Files:")
        for file in relevant_files:
            self.logger.info(f"> - {file}")
        self.logger.info("==================================================")

        # Ask if the AI is done. Return as boolean
        messages = [
            {
                "role": "system",
                "content": "You are TinyGen, a code generation assistant specialized in accurately understanding and processing user requests to generate, modify, or delete code, documentation, or other project-related files.\n"
                        "Your primary task is to analyze the user's request and develop a single, optimal solution to fulfill it.\n"
                        "If the user's request is in the form of a problem, try to fix it. If the user's request is in the form of a missing feature, try to add it.\n"
                        "You have just finished modifying the codebase to fulfill the user's request. Now, you have to decide whether you are satisfied with the changes you have made.\n"
                        "Think about if the changes you've made are sufficient to fulfill the user's request. Also think about if there are any unnecessary files left behind that may be removed.\n"
                        "Below are the Original Files, wrapped in XML tags. (Example: <file><name>/path/to/file</name><content>FILE CONTENTS HERE</content></file>):\n"
            },
            {
                "role": "user",
                "content": self.encode_files(relevant_files)
            },
            {
                "role": "system",
                "content": "User Prompt:\n"
            },
            {
                "role": "user",
                "content": user_prompt
            },
            {
                "role": "system",
                "content": "Respond with ONLY 'done' if you are happy with the changes you've made and are ready to finalize the process. Do not respond with any other comments if you are happy."
                        "If you are not happy, write 2-3 sentences on what mistake you made. Be sure to only include feedback on the changes you have made, and not on the codebase itself. Do not write 'done' if you are not happy with the changes. \n"
                        "This feedback will be incorporated back into the next attempt, so be clear and concise with what should be done/improved.\n"
                        "Make sure to only respond with 'done' (without any quotes or backticks) OR  with any feedback for the next attempt.\n"
                        "For example, if you were happy with the change, you will respond with:\n"
                        "done\n\n"
                        "If you were not happy, you will respond with something like:\n"
                        "I noticed that the function to filter out binary files is not working as expected. It still processes some binary files, leading to errors. We should refine the file type checking logic to accurately distinguish between text and binary files.\n"
            },
        ]

        # Get the response from OpenAI
        response_message = self.gpt.generate(messages, model="gpt-4-turbo-preview")

        # Check if the response was given
        if not response_message.content:
            self.logger.error("No response from OpenAI.")
            return False

        # Check if the AI is done.
        self.logger.info(f"OpenAI responded with: {response_message.content}")
        return "done" == response_message.content.lower().strip()

    def encode_files(self, files: list[str]) -> str:
        # This function encodes the files into XML format so the AI can understand it better
        self.logger.info("Generating XML for files...")
        xml = ""
        for file in files:
            try:
                xml += f"<file><name>{file}</name><content>{self.read_file(file)}</content></file>"
            except Exception as e:
                self.logger.warn(f"Error reading file {file}: {str(e)}")
        return xml

    def clone_repo(self):
        self.logger.info(f"Cloning repository: {self.repo_url}")
        utils.git.git_clone_repo(REPO_TEMP_DIR, self.task_id, self.repo_url)
        self.logger.info("Repository cloned successfully")

    def delete_repo(self):
        self.logger.info(f"Deleting repository: {self.repo_url}")
        utils.git.git_delete_repo(REPO_TEMP_DIR, self.task_id)
        self.logger.info("Repository deleted successfully")

    def reset_repo(self):
        self.logger.info(f"Resetting repository: {self.repo_url}")
        self.delete_repo()
        self.clone_repo()
        self.logger.info("Repository reset successfully")

    def generate_diff(self):
        self.logger.info(f"Generating diff for repository: {self.repo_url}")
        diff = utils.git.git_generate_diff(REPO_TEMP_DIR, self.task_id)
        self.logger.info("Diff generated successfully")
        return diff

    def list_all_files(self):
        self.logger.info(f"Listing all files in repository: {self.repo_url}")
        files = utils.filesystem_io.list_all_files(REPO_TEMP_DIR, self.task_id)
        return files

    def filter_invalid_files(self, file_list: list[str]) -> list[str]:
        self.logger.info("Filtering invalid files...")

        # Try to open each file. If it fails, remove it from the list
        # Use a set so that duplicates are also removed.
        valid_files = set()
        for file in file_list:
            try:
                self.read_file(file)
                valid_files.add(file)
            except Exception as e:
                self.logger.warn(f"Error reading file {file}: {str(e)}")

        # Print which files are filtered
        invalid_files = list(set(file_list) - set(valid_files))
        self.logger.info(f"Filtered {len(invalid_files)} invalid files: {invalid_files}")

        return list(valid_files)

    def read_file(self, filename: str):
        self.logger.info(f"Reading file {filename}")
        content = utils.filesystem_io.safe_read_file(REPO_TEMP_DIR, self.task_id, filename)
        return content

    def modify_file(self, filename: str, content: str):
        self.logger.info(f"Modifying file {filename}")
        utils.filesystem_io.safe_modify_file(REPO_TEMP_DIR, self.task_id, filename, content)

    def delete_file(self, filename: str):
        self.logger.info(f"Deleting file {filename}")
        utils.filesystem_io.safe_delete_file(REPO_TEMP_DIR, self.task_id, filename)

    def create_file(self, filename: str, content: str):
        self.logger.info(f"Creating file {filename}")
        utils.filesystem_io.safe_create_file(REPO_TEMP_DIR, self.task_id, filename, content)
