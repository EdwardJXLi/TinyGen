from task import Task
from tinygen import run_tinygen
from uuid import uuid4

# Test the run_tinygen function
if __name__ == "__main__":
    user_prompt = "test"
    user_repoUrl = ""
    task = Task(uuid4(), user_repoUrl, user_prompt)
    run_tinygen(task)
