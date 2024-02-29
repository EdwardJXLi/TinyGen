# TinyGen

TinyGen is a code generation assistant that specializes in accurately understanding and processing user requests to generate, modify, or delete code, documentation, or other project-related files.

## Introduction

TinyGen utilizes OpenAI's GPT models to analyze user requests and perform tasks such as problem-solving, feature addition, and documentation updates in an efficient and accurate manner.

## Quickstart

> A demo of the TinyGen API is available at [tinygen.hydranet.dev](https://tinygen.hydranet.dev/).

To to get started with using the TinyGen API, follow these steps:

1. **Start a Task**: Post to the `/generate` endpoint to start a new TinyGen task. Provide the repository URL and your prompt in the request body.

2. **Check Task Status**: Use the `/task/{task_id}` endpoint to check the status of your task.

3. **View Task Logs**: To see what happened during the task execution, visit the `/task/{task_id}/logs` endpoint.

4. **Get Task Result**: Once completed, the result of your task can be found at `/task/{task_id}/result`.

For more detailed instructions on using the TinyGen API, see the [Usage Guide](USAGE.md).

## Local Installation Instructions

To set up TinyGen on your local machine, follow these steps:

1. Clone the repository:
```bash
git clone https://github.com/EdwardJXLi/TinyGen
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Create an `.env` file to include your OpenAI API key.
```
OPENAI_API_KEY={your-api-key}
```

4. (Optional) Add your supabase credentials to the `.env` file if you want to use the database features.
```
SUPABASE_PROJECT_URL={your-supabase-url}
SUPABASE_API_KEY={your-supabase-key}
```

5. To start using TinyGen, run the following command:

```bash
uvicorn main:app --reload
```

## Docker Setup Instructions

### Prerequisites

Make sure you have Docker and docker-compose installed on your machine.

### Docker Instructions

1. Clone the repository:
```bash
git clone https://github.com/EdwardJXLi/TinyGen
```

2. Navigate to the cloned directory where you will find the `docker-compose.yml` file.

3. Update the `docker-compose.yml` file with your OpenAI API key, Supabase API key, and Supabase Project URL. Replace placeholder values with your actual credentials.

4. Build and run the Docker container using the command:
```bash
docker-compose up
```

5. Access the running application at `http://localhost:8000` or the configured port.

### Additional Notes

- **Environment Variables**: The variables in `docker-compose.yml` can be adjusted to suit your needs.
- **Stopping TinyGen**: Use `docker-compose down` to stop and remove the Docker containers.
