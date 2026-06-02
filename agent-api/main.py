import os
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="AI Agent Adapter Layer")

LITELLM_BASE_URL = os.getenv("LITELLM_BASE_URL", "http://litellm:4000")
LITELLM_KEY = os.getenv("LITELLM_MASTER_KEY")

TASK_MODEL_MAP = {
    "inspect": "vision_strong",
    "clone_plan": "vision_strong",
    "code_generate": "code_strong",
    "code_fix": "code_strong",
    "copywriting": "cheap_batch",
    "default": "code_fast",
}

class AgentRequest(BaseModel):
    task_type: str = "default"
    prompt: str
    model: str | None = None

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/agent/run")
async def run_agent(req: AgentRequest):
    model = req.model or TASK_MODEL_MAP.get(req.task_type, TASK_MODEL_MAP["default"])

    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "You are an automation agent for website inspection, UI reconstruction, code generation and repair."
            },
            {
                "role": "user",
                "content": req.prompt
            }
        ]
    }

    headers = {
        "Authorization": f"Bearer {LITELLM_KEY}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient(timeout=180) as client:
        r = await client.post(
            f"{LITELLM_BASE_URL}/chat/completions",
            json=payload,
            headers=headers
        )

    if r.status_code >= 400:
        raise HTTPException(status_code=r.status_code, detail=r.text)

    return r.json()
