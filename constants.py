# ====================== [TinyGen] ======================
# Copyright (C) 2024 Edward Li - All Rights Reserved
# =======================================================
from dotenv import load_dotenv
import os

load_dotenv()  # take environment variables from .env.

REPO_TEMP_DIR = os.getenv("REPO_TEMP_DIR", "_tinygen_temp_")
