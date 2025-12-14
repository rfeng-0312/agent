# -*- coding: utf-8 -*-
"""
Personalization utilities:
- Score -> level mapping
- Effective level resolution (manual > user default > score)
- Basic two-phase teaching flow
- Safe learning-profile handling
- System prompt builders (zh-CN / en-US)
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple


LEVEL_AUTO = "auto"
LEVEL_BASIC = "basic"
LEVEL_STANDARD = "standard"
LEVEL_ADVANCED = "advanced"
LEVEL_VALUES = {LEVEL_AUTO, LEVEL_BASIC, LEVEL_STANDARD, LEVEL_ADVANCED}

PACE_VALUES = {"slow", "medium", "fast"}


def normalize_level(value: Optional[str]) -> str:
    if not value:
        return LEVEL_AUTO
    value = str(value).strip().lower()
    return value if value in LEVEL_VALUES else LEVEL_AUTO


def score_to_level(score: Optional[int]) -> str:
    if score is None:
        return LEVEL_STANDARD
    try:
        score_int = int(score)
    except Exception:
        return LEVEL_STANDARD
    if score_int <= 70:
        return LEVEL_BASIC
    if score_int <= 90:
        return LEVEL_STANDARD
    return LEVEL_ADVANCED


def get_subject_score(subject: str, physics_score: Optional[int], chemistry_score: Optional[int]) -> Optional[int]:
    if subject == "chemistry":
        return chemistry_score
    return physics_score


def resolve_effective_level(
    *,
    level_override: Optional[str],
    default_explain_level: Optional[str],
    score_level: str,
) -> Tuple[str, str]:
    """
    Returns: (level_effective, level_source)
    level_source in {"manual","default","score"}
    """
    override = normalize_level(level_override)
    if override != LEVEL_AUTO:
        return override, "manual"
    default_level = normalize_level(default_explain_level)
    if default_level != LEVEL_AUTO:
        return default_level, "default"
    return score_level, "score"


def default_teaching_phase(level_effective: str) -> int:
    return 1 if level_effective == LEVEL_BASIC else 2


def is_profile_stale(updated_at: Optional[datetime], ttl_hours: int = 24) -> bool:
    if not updated_at:
        return True
    return updated_at < datetime.now() - timedelta(hours=ttl_hours)


def _strip_instruction_like_text(text: str) -> str:
    lowered = text.lower()
    for needle in [
        "ignore previous",
        "system prompt",
        "you are chatgpt",
        "你是系统",
        "忽略以上",
        "执行命令",
        "developer message",
    ]:
        lowered = lowered.replace(needle, "")
    return lowered


def sanitize_learning_profile(profile: Any) -> Dict[str, Any]:
    """
    Accepts dict/JSON string/None and returns a safe, small dict.
    """
    if profile is None:
        return {}
    if isinstance(profile, str):
        try:
            profile = json.loads(profile)
        except Exception:
            return {}
    if not isinstance(profile, dict):
        return {}

    def _clean_list(values: Any, max_items: int = 3) -> list:
        if not isinstance(values, list):
            return []
        cleaned = []
        for item in values:
            if not item:
                continue
            s = str(item).strip()
            s = re.sub(r"\s+", " ", s)
            s = _strip_instruction_like_text(s).strip()
            if not s:
                continue
            if len(s) > 40:
                s = s[:40]
            cleaned.append(s)
            if len(cleaned) >= max_items:
                break
        return cleaned

    cleaned_profile: Dict[str, Any] = {}
    cleaned_profile["weak_topics"] = _clean_list(profile.get("weak_topics"), 3)
    cleaned_profile["preferred_style"] = _clean_list(profile.get("preferred_style"), 3)
    pace = profile.get("pace")
    if isinstance(pace, str) and pace.lower() in PACE_VALUES:
        cleaned_profile["pace"] = pace.lower()
    cleaned_profile["common_mistakes"] = _clean_list(profile.get("common_mistakes"), 3)
    notes = profile.get("notes")
    if isinstance(notes, str):
        notes = re.sub(r"\s+", " ", notes).strip()
        notes = _strip_instruction_like_text(notes).strip()
        if notes:
            cleaned_profile["notes"] = notes[:200]

    # Remove empty fields to keep prompt small
    return {k: v for k, v in cleaned_profile.items() if v}


@dataclass(frozen=True)
class PromptContext:
    subject: str
    lang: str
    level: str
    phase: int
    score: Optional[int]
    user_pref_level: str
    profile: Dict[str, Any]
    deep_think: bool = False
    has_image: bool = False


def _subject_name(subject: str, lang: str) -> str:
    if lang == "en-US":
        return "Chemistry" if subject == "chemistry" else "Physics"
    return "化学" if subject == "chemistry" else "物理"


def _json_block(obj: Any) -> str:
    try:
        return json.dumps(obj, ensure_ascii=False, indent=2)
    except Exception:
        return "{}"


def build_system_prompt_deepseek(subject_prompt: str, ctx: PromptContext) -> str:
    if ctx.lang == "en-US":
        return _build_system_prompt_deepseek_en(subject_prompt, ctx)
    return _build_system_prompt_deepseek_zh(subject_prompt, ctx)


def build_system_prompt_doubao(subject_prompt: str, ctx: PromptContext) -> str:
    if ctx.lang == "en-US":
        return _build_system_prompt_doubao_en(subject_prompt, ctx)
    return _build_system_prompt_doubao_zh(subject_prompt, ctx)


def build_verifier_system_prompt(subject: str, lang: str) -> str:
    """
    Strict verification prompt for the cross-validation stage.
    Keep it independent from student personalization.
    """
    subject_name = _subject_name(subject, lang)
    if lang == "en-US":
        return (
            f"You are a strict {subject_name} reviewer. Independently verify whether the proposed solution is correct.\n"
            "Rules:\n"
            "- Be rigorous; do not assume the solution is correct.\n"
            "- Check logic, formulas/equations, calculations, units, assumptions.\n"
            "- If uncertain, state what is missing and how to check.\n"
            "Output (Markdown headings):\n"
            "## Verdict\n"
            "## Key Checks\n"
            "## If Incorrect: Correction\n"
        )
    return (
        f"你是一位严格的{subject_name}审稿专家。请独立核查“给定解答”是否正确。\n"
        "规则：\n"
        "- 严谨客观，不要预设解答正确。\n"
        "- 检查逻辑、公式/方程式、计算、单位、假设与边界条件。\n"
        "- 如不确定，请说明缺失信息与核查方法。\n"
        "输出格式（Markdown 小标题）：\n"
        "## 核查结论\n"
        "## 核查要点\n"
        "## 若不正确：给出更正\n"
    )


def _build_system_prompt_deepseek_zh(subject_prompt: str, ctx: PromptContext) -> str:
    subject_name = _subject_name(ctx.subject, ctx.lang)
    deep_think_note = ""
    if ctx.deep_think:
        deep_think_note = (
            "\n【重要】你的解答将被另一个模型核查；如果题目来自图片，请在答案开头包含“题目复述/条件整理”，"
            "确保不看图也能核查。"
        )
    return f"""你是一位严谨且擅长因材施教的{subject_name}老师，目标是“让学生学会”，而不是只给结果。

【学科基础要求】（用于保证专业性与准确性）
{subject_prompt}

【学生信息（仅用于教学方式，不得复述隐私）】
- 自评分数：{ctx.score if ctx.score is not None else "未知"}
- 讲解层级：{ctx.level}（若学生手动选择则优先：{ctx.user_pref_level}）
- 当前生效：level={ctx.level}，phase={ctx.phase}（你必须只使用该 level/phase 对应的输出结构）
- 学习画像（结构化摘要，禁止引用原日记内容、禁止猜测隐私）：
{_json_block(ctx.profile)}
{deep_think_note}

【总规则】
1) 你必须严格遵守对应层级与阶段的输出结构。
2) 公式用 LaTeX；步骤编号清晰；单位/量纲要检查。
3) 不得透露“我读取了日记原文”；只能使用画像摘要来调整讲解风格。
4) 若题干信息不足：先列“缺失信息清单”，并给出最多3个澄清问题。

【输出结构（必须严格匹配，使用 Markdown 小标题）】
- 若 level=basic 且 phase=1：
  ## 知识点讲解
  ## 引导完成
  ## 结束语
  重要：禁止输出最终答案/最终数值/最终选项；可以给自检方法但不能泄露结果。
- 若 level=basic 且 phase=2：
  ## 步骤
  ## 答案
  ## 易错点
- 若 level=standard：
  ## 步骤
  ## 答案
  ## 易错点
  ## 可选拓展
- 若 level=advanced：
  ## 步骤
  ## 结论
  ## 易错点
  ## 拓展知识

【任务】
请解答学生的问题。只输出结构化内容，不要额外加免责声明或与任务无关的内容。
"""


def _build_system_prompt_deepseek_en(subject_prompt: str, ctx: PromptContext) -> str:
    subject_name = _subject_name(ctx.subject, ctx.lang)
    deep_think_note = ""
    if ctx.deep_think:
        deep_think_note = (
            "\n[Important] Your solution will be checked by another model. If the problem comes from an image, "
            "include a clear problem restatement/conditions so it can be verified without the image."
        )
    return f"""You are a rigorous {subject_name} tutor who adapts explanations to the student’s level. The goal is teaching, not just giving results.

[Subject baseline requirements]
{subject_prompt}

[Student context (use only to adapt teaching; never quote private diary text)]
- Self-reported score: {ctx.score if ctx.score is not None else "unknown"}
- Explanation level: {ctx.level} (manual override if present: {ctx.user_pref_level})
- Effective: level={ctx.level}, phase={ctx.phase} (use ONLY the matching structure)
- Learning profile (structured summary; do NOT infer private details):
{_json_block(ctx.profile)}
{deep_think_note}

[Global rules]
1) Follow the required output structure exactly.
2) Use LaTeX for formulas; numbered steps; check units/dimensions.
3) Do not mention diaries; only use the profile summary to adjust style.
4) If information is missing, list “Missing info” and ask up to 3 clarifying questions.

[Output Structure (Markdown headings)]
- If level=basic and phase=1:
  ## Core Concepts
  ## Guided Attempt
  ## Closing
  Hard rule: do NOT reveal the final answer/value/option.
- If level=basic and phase=2:
  ## Steps
  ## Final Answer
  ## Common Mistakes
- If level=standard:
  ## Steps
  ## Final Answer
  ## Common Mistakes
  ## Optional Extension
- If level=advanced:
  ## Steps
  ## Conclusion
  ## Common Pitfalls
  ## Extension

[Task]
Solve the student’s problem. Output only the structured sections.
"""


def _build_system_prompt_doubao_zh(subject_prompt: str, ctx: PromptContext) -> str:
    subject_name = _subject_name(ctx.subject, ctx.lang)
    extraction = ""
    if ctx.has_image:
        extraction = """【读图规则（必须做）】
1) 先输出“题目信息提取”：列出已知量、求解目标、关键条件/图中标注。
2) 若关键信息不清晰（数值/单位/图注/方向），在“缺失信息”里指出并问最多3个澄清问题。
3) 对可能 OCR 误读的数字/符号要保守处理，并在步骤里注明假设。
"""
    deep_think_note = ""
    if ctx.deep_think:
        deep_think_note = "\n【重要】你的解答将被另一个模型核查；请在答案中包含“题目复述/条件整理”。"
    prefix = ""
    if ctx.has_image:
        prefix = """## 题目信息提取
- 已知：
- 求：
- 条件/假设：
"""
    return f"""你是一位严谨的{subject_name}老师，擅长从题目图片中提取信息并因材施教。

【学科基础要求】（用于保证专业性与准确性）
{subject_prompt}

【学生信息（仅用于教学方式）】
- 自评分数：{ctx.score if ctx.score is not None else "未知"}
- 讲解层级：{ctx.level}（若学生手动选择则优先：{ctx.user_pref_level}）
- 当前生效：level={ctx.level}，phase={ctx.phase}（你必须只使用该 level/phase 对应的输出结构）
- 学习画像（结构化摘要）：
{_json_block(ctx.profile)}
{deep_think_note}

{extraction}
【输出结构】
严格使用与文字题相同的 level/phase 结构（知识点/引导/步骤/答案/易错点/拓展等）。
{prefix}
"""


def _build_system_prompt_doubao_en(subject_prompt: str, ctx: PromptContext) -> str:
    subject_name = _subject_name(ctx.subject, ctx.lang)
    extraction = ""
    if ctx.has_image:
        extraction = """[Image-reading rules]
1) Start with “Extracted Problem Data”: list givens, target, and constraints/labels from the image.
2) If key info is unclear, state “Missing/Unclear” and ask up to 3 questions.
3) Be conservative about possible OCR misreads; state assumptions explicitly.
"""
    deep_think_note = ""
    if ctx.deep_think:
        deep_think_note = "\n[Important] Your solution will be checked by another model; include a problem restatement/conditions."
    prefix = ""
    if ctx.has_image:
        prefix = """## Extracted Problem Data
- Givens:
- Find:
- Constraints/Assumptions:
"""
    return f"""You are a rigorous {subject_name} tutor who can extract problem statements from an image and adapt to the student level.

[Subject baseline requirements]
{subject_prompt}

[Student context]
- Score: {ctx.score if ctx.score is not None else "unknown"}
- Level: {ctx.level} (manual override if present: {ctx.user_pref_level})
- Effective: level={ctx.level}, phase={ctx.phase} (use ONLY the matching structure)
- Profile:
{_json_block(ctx.profile)}
{deep_think_note}

{extraction}
[Output Structure]
Use the same level/phase structure as the text version (concepts/guided attempt/steps/answer/mistakes/extension).
{prefix}
"""
