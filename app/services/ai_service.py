from openai import AsyncOpenAI
import os
import json

from app.services.prompts import (
    strategist_prompt,
    copy_prompt,
    strategy_critic_prompt,
    copy_critic_prompt
)
from app.services.memory import save_memory, memory_context
from app.utils.helpers import safe_completion, safe_json_parse


# ================= CRITIC =================

async def run_critic(client, prompt, content):
    r = await safe_completion(
        client,
        model="gpt-4o-mini",
        temperature=0.3,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": content}
        ]
    )
    return safe_json_parse(r.choices[0].message.content)


# ================= MAIN PIPELINE =================

async def run_campaign(req):
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    is_arabic = req.output_language.lower() == "arabic"

    # =========================================================
    # 🧠 STRATEGY LOOP
    # =========================================================

    best_strategy = None
    best_score = -1
    improvement = ""

    for attempt in range(2):
        yield {"type": "step", "content": f"Strategy attempt {attempt + 1}..."}

        extra_feedback = ""
        if attempt > 0 and improvement:
            extra_feedback = f"\n\nImprove based on this feedback:\n{improvement}"

        r1 = await safe_completion(
            client,
            model="gpt-4o-mini",
            temperature=0.7,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": strategist_prompt(is_arabic)},
                {"role": "user", "content": (
                    f"Previous memory:\n{memory_context()}\n\n"
                    f"Product: {req.product_name}\n"
                    f"Description: {req.product_desc}\n"
                    f"Audience: {req.target_audience}\n"
                    f"Voice: {req.brand_voice}"
                    f"{extra_feedback}"
                )}
            ]
        )

        strategy = safe_json_parse(r1.choices[0].message.content)

        critic = await run_critic(
            client,
            strategy_critic_prompt(),
            json.dumps(strategy, ensure_ascii=False)
        )

        score = critic.get("score", 0)

        if score > best_score:
            best_score = score
            best_strategy = strategy

        yield {"type": "step", "content": f"Strategy score: {score}/10"}

        if score >= 7:
            break

        improvement = critic.get("improvement_suggestions", "")

    # Safety fallback
    if not best_strategy:
        best_strategy = {}

    # =========================================================
    # ✍️ COPY LOOP
    # =========================================================

    best_copy = None
    best_score = -1
    improvement = ""

    for attempt in range(2):
        yield {"type": "step", "content": f"Copywriter attempt {attempt + 1}..."}

        extra_feedback = ""
        if attempt > 0 and improvement:
            extra_feedback = f"\n\nImprove based on this feedback:\n{improvement}"

        r2 = await safe_completion(
            client,
            model="gpt-4o-mini",
            temperature=0.85,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": copy_prompt(req.product_name, is_arabic)},
                {"role": "user", "content": (
                    json.dumps(best_strategy, ensure_ascii=False) + extra_feedback
                )}
            ]
        )

        campaign = safe_json_parse(r2.choices[0].message.content)
        narrative = campaign.get("narrative", "")

        critic = await run_critic(
            client,
            copy_critic_prompt(),
            narrative
        )

        score = critic.get("score", 0)

        if score > best_score:
            best_score = score
            best_copy = narrative

        yield {"type": "step", "content": f"Copywriter score: {score}/10"}

        if score >= 7:
            break

        improvement = critic.get("improvement_suggestions", "")

    # Safety fallback
    if not best_copy:
        best_copy = "No output generated"

    # =========================================================
    # 💾 SAVE MEMORY
    # =========================================================

    save_memory({
        "product": req.product_name,
        "tone": req.brand_voice,
        "audience": req.target_audience
    })

    # =========================================================
    # 📤 FINAL OUTPUT
    # =========================================================

    yield {
        "type": "narrative",
        "content": best_copy.replace("\n", "<br>")
    }