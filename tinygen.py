# ====================== [TinyGen] ======================
# Copyright (C) 2024 Edward Li - All Rights Reserved
# =======================================================
from task import Task

from traceback import print_exc
import time


def run_tinygen(task: Task):
    try:
        # Start the task
        task.start()

        # Fake blocking task
        for i in range(15):
            time.sleep(1)
            task.logger.info(f"Task {task.task_id} is running... (Sleep {i})")

        # Finish the task
        task.set_result("This is a fake result")
    except Exception as e:
        # Print out the error
        print_exc()

        # Set the task status to ERROR
        task.set_error(str(e))
