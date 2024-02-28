# Copyright (C) 2024 Edward Li - All Rights Reserved
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

app = FastAPI()


class GenerateInput(BaseModel):
    repoUrl: str
    prompt: str


def run_ai_pipeline(repo_url: str, prompt: str):
    # Placeholder for your AI pipeline logic
    return {"repoUrl": repo_url, "prompt": prompt, "result": "This is a stub response."}


@app.get("/")
async def read_root():
    return "TinyGen - Hello World"


@app.post("/generate")
async def generate(data: GenerateInput):
    result = run_ai_pipeline(data.repoUrl, data.prompt)
    return result
