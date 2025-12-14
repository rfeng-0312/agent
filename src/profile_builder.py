# -*- coding: utf-8 -*-
"""
Build a structured learning profile from recent diary entries.

Important:
- Do NOT store diary raw text in the profile.
- Output must be small, schema-constrained JSON.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from database import get_recent_diaries
from personalization import sanitize_learning_profile


PROFILE_SCHEMA_HINT = {
    "weak_topics": ["..."],
    "preferred_style": ["..."],
    "pace": "slow|medium|fast",
    "common_mistakes": ["..."],
    "notes": "..."
}


def _extract_json(text: str) -> Optional[Dict[str, Any]]:
    if not text:
        return None
    text = text.strip()
    try:
        obj = json.loads(text)
        if isinstance(obj, dict):
            return obj
    except Exception:
        pass

    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        return None
    try:
        obj = json.loads(match.group(0))
        if isinstance(obj, dict):
            return obj
    except Exception:
        return None
    return None


def _build_messages(lang: str, diary_text: str) -> List[Dict[str, str]]:
    schema_str = json.dumps(PROFILE_SCHEMA_HINT, ensure_ascii=False)
    if lang == "en-US":
        system = (
            "You are a learning-profile summarizer. Create a small, structured JSON profile from diary text.\n"
            "Rules:\n"
            "- Output JSON only, no markdown.\n"
            "- Do NOT include private details. Do NOT quote diary text.\n"
            "- Follow this schema (fields optional but must be valid):\n"
            f"{schema_str}\n"
            "- Keep arrays <= 3 items each; keep strings short.\n"
        )
        user = f"Diary entries (for analysis only):\n{diary_text}\n\nReturn JSON now."
    else:
        system = (
            "你是学习画像总结器。请根据日记文本提炼一个小而结构化的 JSON 学习画像。\n"
            "规则：\n"
            "- 只输出 JSON，不要 Markdown。\n"
            "- 不要包含隐私细节，不要引用日记原文。\n"
            "- 按以下 schema 输出（字段可选，但必须合法）：\n"
            f"{schema_str}\n"
            "- 每个数组最多 3 条；字符串保持简短。\n"
        )
        user = f"日记内容（仅用于分析）：\n{diary_text}\n\n现在只输出 JSON。"
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


def build_learning_profile_from_diaries(
    *,
    user_id: int,
    lang: str,
    days: int = 14,
    limit: int = 30,
    deepseek_client=None,
    deepseek_model: Optional[str] = None,
    doubao_client=None,
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Returns (profile_dict, error_message). profile_dict is sanitized and small.
    """
    diaries = get_recent_diaries(user_id=user_id, days=days, limit=limit)
    if not diaries:
        return {}, None

    # Keep content small and avoid leaking full diary content upstream
    chunks: List[str] = []
    for diary in diaries:
        content = (diary.get("content") or "").strip()
        if not content:
            continue
        content = re.sub(r"\s+", " ", content)
        chunks.append(content[:400])
        if len(chunks) >= limit:
            break

    diary_text = "\n".join(f"- {c}" for c in chunks)
    if len(diary_text) > 6000:
        diary_text = diary_text[:6000]

    messages = _build_messages(lang, diary_text)

    response_text = None
    try:
        if deepseek_client and deepseek_model:
            resp = deepseek_client.chat.completions.create(
                model=deepseek_model,
                messages=messages,
                stream=False,
            )
            response_text = resp.choices[0].message.content or ""
        elif doubao_client and getattr(doubao_client, "client", None):
            resp = doubao_client.client.chat.completions.create(
                model=doubao_client.model,
                messages=messages,
                stream=False,
                max_tokens=400,
            )
            response_text = resp.choices[0].message.content or ""
        else:
            return None, "No AI client available for profile generation"
    except Exception as e:
        return None, f"Profile generation failed: {e}"

    obj = _extract_json(response_text or "")
    sanitized = sanitize_learning_profile(obj)
    return sanitized, None


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")

