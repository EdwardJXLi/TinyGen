# ====================== [TinyGen] ======================
# Copyright (C) 2024 Edward Li - All Rights Reserved
# =======================================================
from uuid import uuid4

from tinygen import TinyGenTask

# Test the run_tinygen function
if __name__ == "__main__":
    user_prompt = "The program doesn't output anything in Windows 10"
    user_repoUrl = "https://github.com/jayhack/llm.sh"
    task = TinyGenTask(uuid4(), user_repoUrl, user_prompt)
    task.run_tinygen()

    print(task.result)
