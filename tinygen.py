from task import Task

import time


def run_tinygen(task: Task):
    # Start the task
    task.start()

    # Simulate a long-running task
    time.sleep(20)

    # Finish the task
    task.set_result("This is a fake result")
