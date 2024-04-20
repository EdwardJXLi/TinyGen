# ====================== [TinyGen] ======================
# Copyright (C) 2024 Edward Li - All Rights Reserved
# =======================================================
import os

from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", None)
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY", "")
SUPABASE_PROJECT_URL = os.getenv("SUPABASE_PROJECT_URL", "")
REPO_TEMP_DIR = os.getenv("REPO_TEMP_DIR", "_tinygen_temp_")
DEFAULT_GPT_MODEL = os.getenv("DEFAULT_GPT_MODEL", "gpt-3.5-turbo")
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
