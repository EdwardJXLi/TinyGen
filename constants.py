# ====================== [TinyGen] ======================
# Copyright (C) 2024 Edward Li - All Rights Reserved
# =======================================================
from dotenv import load_dotenv
import os

load_dotenv()  # take environment variables from .env.

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "UNKNOWN_KEY")
REPO_TEMP_DIR = os.getenv("REPO_TEMP_DIR", "_tinygen_temp_")
DEFAULT_GPT_MODEL = os.getenv("DEFAULT_GPT_MODEL", "gpt-3.5-turbo")
