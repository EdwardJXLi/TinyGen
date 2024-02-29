# TinyGen API Usage Guide

This document provides a comprehensive guide to using the TinyGen API, which is designed to manage and execute inyGen tasks.

## API Endpoints

### Root

- **Method**: GET
- **URL**: `/`
- **Description**: Returns a simple text response to confirm the API is operational.

**Example Request**:
```
GET /
```

**Example Response**:
```
TinyGen API
```

### Start TinyGen

- **Method**: POST
- **URL**: `/generate`
- **Description**: Starts a new TinyGen task using the provided repository URL and prompt.
- **Body**:
  - `repoUrl`: The GitHub repository URL.
  - `prompt`: The generation prompt.

**Example Request**:
```json
POST /generate
Content-Type: application/json

{
  "repoUrl": "https://github.com/example/repo",
  "prompt": "Generate a Python function for adding two numbers."
}
```

**Example Response**:
```json
{
  "task_id": "uuid-of-the-task",
  "task_url": "http://localhost/task/uuid-of-the-task"
}
```

### Task Status

- **Method**: GET
- **URL**: `/task/{task_id_str}`
- **Description**: Retrieves the status of a specific TinyGen task by its ID.

**Example Request**:
```
GET /task/uuid-of-the-task
```

**Example Response**:
```json
{
  "task_id": "uuid-of-the-task",
  "repo_url": "https://github.com/example/repo",
  "prompt": "Generate a Python function for adding two numbers.",
  "status": "Completed",
  "result_url": "http://localhost/task/uuid-of-the-task/result",
  "logs_url": "http://localhost/task/uuid-of-the-task/logs",
  "start_time": "2024-05-01T12:00:00Z",
  "end_time": "2024-05-01T12:05:00Z",
  "elapsed_time": 300
}
```

### Task Result

- **Method**: GET
- **URL**: `/task/{task_id_str}/result`
- **Description**: Retrieves the result of a completed TinyGen task.

**Example Request**:
```
GET /task/uuid-of-the-task/result
```

**Example Response**:
```
def add_numbers(a, b):
    return a + b
```

### Task Logs

- **Method**: GET
- **URL**: `/task/{task_id_str}/logs`
- **Description**: Retrieves the logs for a specific TinyGen task.

**Example Request**:
```
GET /task/uuid-of-the-task/logs
```

**Example Response**:
```
Task started.
Processing...
Task completed successfully.
```

### Task Cancel

- **Method**: DELETE
- **URL**: `/task/{task_id_str}/cancel`
- **Description**: Cancels a specific TinyGen task.

**Example Request**:
```
DELETE /task/uuid-of-the-task/cancel
```

**Example Response**:
```json
{
  "task_id": "uuid-of-the-task",
  "status": "Cancelled"
}
```

### Health Check

- **Method**: GET
- **URL**: `/health`
- **Description**: Provides a summary of the number of tasks in different states: pending, finished, and errored.

**Example Request**:
```
GET /health
```

**Example Response**:
```json
{
    "pending": 1, 
    "finished": 2, 
    "errored": 3, 
    "cancelled": 4, 
    "other": 5
}
```
