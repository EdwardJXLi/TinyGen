# ====================== [TinyGen] ======================
# Copyright (C) 2024 Edward Li - All Rights Reserved
# =======================================================
from openai import OpenAI
from openai.types.chat.chat_completion_message import ChatCompletionMessage
from logging import Logger
from typing import Iterable
from constants import DEFAULT_GPT_MODEL


class OpenAIInteraction:
    def __init__(self, task, api_key: str):
        """
        Creates an OpenAIInteraction class, which handles all the communication and interaction with the OpenAI API.

        Parameters:
            task (TinyGenTask): The task object to use for logging.
            api_key (str): The API key to use for the OpenAI API.
        """
        # Initialize the OpenAI API
        self.task = task
        self.logger: Logger = task.logger
        self.api_key: str = api_key

        # Initialize the OpenAI client
        self.logger.info("Initializing OpenAI API Client...")
        self.client = OpenAI(api_key=api_key)

    def generate(
        self,
        messages: Iterable,
        model: str = DEFAULT_GPT_MODEL,
        temperature: float = 0.4,
        response_id: int = 0,
        **kwargs
    ) -> ChatCompletionMessage:
        """
        Generate a response from the OpenAI API.

        Parameters:
            messages (Iterable[ChatCompletionMessageParam]): The messages to use as context for the response. This is an iterable of ChatCompletionMessageParam objects
            model (str): The model to use for the response. Defaults to the default GPT model.
            temperature (float): The temperature to use for the response. Defaults to 0.4.
            response_id (int): The index of the response to return. Defaults to 0.
            **kwargs: Additional keyword arguments to pass to the OpenAI API.

        Returns:
            ChatCompletionMessage: The response from the OpenAI API.
        """
        self.logger.info(f"[TinyGen > GPT] Generating response from OpenAI ({model})...")

        # Generate a response from the OpenAI API
        response = self.client.chat.completions.create(
            model=model,
            temperature=temperature,
            messages=messages,
            **kwargs
        )

        # Log the response
        self.logger.info(f"[TinyGen < GPT] Response received! Content Length: {len(response.choices[response_id].message.content or '')}")

        # Return the fist response
        return response.choices[response_id].message


# Available functions for the OpenAI interaction
FUNCTIONS = [
    {
        "type": "function",
        "function": {
            "name": "create_file",
            "description": "Creates a new file with the given content. Do not call create_file if the file already exists.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "The new file to create. Assume that all relevant subdirectories will be created if they do not exist.",
                    },
                    "content": {
                        "type": "string",
                        "description": "The content of the new file.",
                    },
                },
                "required": ["file_path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "modify_file",
            "description": "Modifies a given file with the given content. Do not call modify_file if the file does not exist.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "The path to the file to modify. This file must exist in the current file structure, or must me a file added in a previous step.",
                    },
                    "content": {
                        "type": "string",
                        "description": "The new content of the file. This content will replace the original content of the file. Make sure to include all necessary content, including any content that was in the original file.",
                    },
                },
                "required": ["file_path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "delete_file",
            "description": "Deletes a given file. Do not call delete_file if the file does not exist.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "The path to the file to delete. This file must exist in the current file structure, or must me a file added in a previous step.",
                    },
                },
                "required": ["file_path"],
            },
        },
    }
]
