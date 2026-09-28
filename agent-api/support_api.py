import json
import os
import re

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

LITELLM_BASE_URL = os.getenv("LITELLM_BASE_URL", "http://litellm:4000")
LITELLM_KEY = os.getenv("LITELLM_MASTER_KEY")

SUPPORT_MODEL_CHAIN = ("support_fast", "support_fallback")


class SupportEvidence(BaseModel):
    title: str
    url: str
    content: str


class SupportAnswerRequest(BaseModel):
    question: str
    department: str | None = None
    evidence: list[SupportEvidence]


def support_json(content: str) -> dict:
    text = content.strip()

    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.I)
        text = re.sub(r"\s*```$", "", text)

    return json.loads(text)


def requires_human(question: str) -> bool:
    normalized = re.sub(r"\s+", " ", question.lower()).strip()

    patterns = (
        r"\b(?:password|api key|access token|secret key|private key|ssh key|credit card|card number|cvv|ssn)\s*(?:is|:|=)",
        r"\b(?:my|our)\s+(?:order|invoice|refund|payment)\s+(?:status|number|id|balance)\b",
        r"(?:密码是|密码[:：=]|api密钥|访问令牌|私钥|ssh密钥|信用卡号|安全码|订单号|发票号|账户余额|退款状态|付款状态)",
    )

    return any(re.search(pattern, normalized, re.I | re.U) for pattern in patterns)


async def call_support_model(model: str, question: str, department: str, evidence: list[dict]):
    system = (
        "You are WWKNOW Support AI. Answer only from the supplied public WWKNOW knowledgebase evidence. "
        "Never use outside knowledge to fill gaps. Never invent prices, policies, product availability, account status, "
        "order status, invoice status, payment status, refund status, credentials, configuration values, or operational facts. "
        "If evidence is insufficient, ambiguous, conflicting, or customer-specific/private data is required, return needs_human. "
        "Return JSON only with exactly these keys: status, answer, reason, citation_ids. "
        "status must be answered or needs_human. For answered, answer must be concise and complete, reason must be null, "
        "and citation_ids must contain one or more supplied evidence ids. For needs_human, answer must be null, "
        "reason must be a short machine-readable string, and citation_ids must be an empty array."
    )

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "question": question,
                        "department": department,
                        "evidence": evidence,
                    },
                    ensure_ascii=False,
                ),
            },
        ],
        "temperature": 0,
        "max_tokens": 700,
    }

    headers = {
        "Authorization": f"Bearer {LITELLM_KEY}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=40) as client:
        response = await client.post(
            f"{LITELLM_BASE_URL}/chat/completions",
            json=payload,
            headers=headers,
        )

    if response.status_code >= 400:
        raise RuntimeError(f"model_http_{response.status_code}")

    data = response.json()
    content = (
        (((data.get("choices") or [{}])[0].get("message") or {}).get("content") or "")
    )

    return support_json(content), str(data.get("model") or model)


@router.post("/support/answer")
async def support_answer(req: SupportAnswerRequest):
    question = re.sub(r"\s+", " ", req.question).strip()[:2000]
    department = re.sub(r"\s+", " ", req.department or "General").strip()[:120]

    if not question:
        raise HTTPException(status_code=422, detail="Question is required.")

    if requires_human(question):
        return {
            "status": "needs_human",
            "answer": None,
            "reason": "sensitive_or_account_specific",
            "sources": [],
            "model": None,
        }

    evidence = []

    for index, item in enumerate(req.evidence[:5], start=1):
        content = re.sub(r"\s+", " ", item.content).strip()[:6000]

        if not content:
            continue

        evidence.append(
            {
                "id": f"E{index}",
                "title": item.title.strip()[:240],
                "url": item.url.strip()[:1000],
                "content": content,
            }
        )

    if not evidence:
        return {
            "status": "needs_human",
            "answer": None,
            "reason": "insufficient_evidence",
            "sources": [],
            "model": None,
        }

    last_reason = "model_unavailable"

    for model in SUPPORT_MODEL_CHAIN:
        try:
            result, actual_model = await call_support_model(
                model,
                question,
                department,
                evidence,
            )

            status = result.get("status")

            if status == "needs_human":
                return {
                    "status": "needs_human",
                    "answer": None,
                    "reason": str(result.get("reason") or "insufficient_evidence")[:80],
                    "sources": [],
                    "model": actual_model,
                }

            if status != "answered":
                last_reason = "invalid_model_response"
                continue

            answer = str(result.get("answer") or "").strip()
            citation_ids = result.get("citation_ids") or []
            allowed = {item["id"]: item for item in evidence}

            if not answer or len(answer) > 4000 or not isinstance(citation_ids, list):
                last_reason = "invalid_model_response"
                continue

            selected = []
            selected_ids = set()

            for citation_id in citation_ids:
                if citation_id in allowed and citation_id not in selected_ids:
                    selected.append(allowed[citation_id])
                    selected_ids.add(citation_id)

            if not selected:
                last_reason = "uncited_answer"
                continue

            return {
                "status": "answered",
                "answer": answer,
                "reason": None,
                "sources": [
                    {"title": item["title"], "url": item["url"]}
                    for item in selected
                ],
                "model": actual_model,
            }

        except Exception:
            last_reason = "model_unavailable"

    return {
        "status": "needs_human",
        "answer": None,
        "reason": last_reason,
        "sources": [],
        "model": None,
    }
