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
        self.logger.info(f"[TinyGen > GPT] Generating response from OpenAI ({model})...")

        # Generate a response from the OpenAI API
        response = self.client.chat.completions.create(
            model=model,
            temperature=temperature,
            messages=messages,
            **kwargs
        )

        # Log the response
        self.logger.info(f"[TinyGen < GPT] Response received! Content Length: {len(response.choices[response_id].message.content)}")

        # Return the fist response
        return response.choices[response_id].message
