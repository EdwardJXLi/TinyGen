# TinyGen

TinyGen is a code generation assistant that specializes in accurately understanding and processing user requests to generate, modify, or delete code, documentation, or other project-related files.

## Introduction

TinyGen utilizes OpenAI's GPT models to analyze user requests and perform tasks such as problem-solving, feature addition, and documentation updates in an efficient and accurate manner.

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
