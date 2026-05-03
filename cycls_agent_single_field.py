import cycls
import os
import json
import asyncio
import urllib.parse

# ================= CYCLS PRIMITIVES =================

image = (
    cycls.Image()
    .pip("openai")
    .copy(".env")
)

web = (
    cycls.Web()
    .title("🎯 Creative Campaign Agent")
)

# ================= UTILITIES =================

async def safe_completion(client, **kwargs):
    for attempt in range(3):
        try:
            return await client.chat.completions.create(**kwargs)
        except Exception:
            if attempt == 2:
                raise
            await asyncio.sleep(1.5 * (attempt + 1))

def safe_json_parse(content):
    try:
        return json.loads(content)
    except Exception:
        return {}

# ================= MEMORY =================

_memory_store = []

def load_memory():
    return list(_memory_store)

def save_memory(entry):
    _memory_store.append(entry)
    if len(_memory_store) > 8:
        _memory_store.pop(0)

def memory_context():
    if not _memory_store:
        return "No prior campaign history."
    return "\n".join([
        f"- Product: {m['product']} | Tone: {m['tone']}"
        for m in _memory_store
    ])

# ================= PROMPTS =================

def strategist_prompt(ar: bool) -> str:
    if ar:
        return """أنت مستشار استراتيجي كبير متخصص في علم نفس المستهلك والتسويق الثقافي في السعودية.

اكتب بالعربية فقط. استخدم العامية السعودية الطبيعية.
لا تستخدم أي كلمات إنجليزية.

حلل المنتج وأخرج JSON للموجز الاستراتيجي مع:
1. التوتر العاطفي الأساسي
2. اللحظة الثقافية السعودية المحددة
3. الخطاف الحسي
4. الرغبة غير المعلنة

صيغة الإخراج:
{
  "emotional_tension": "",
  "saudi_moment": "",
  "sensory_hook": "",
  "unspoken_desire": ""
}"""
    return """You are a senior creative strategist specializing in consumer psychology
and culturally relevant marketing in Saudi Arabia.

Output in English.

Analyze the product and return a JSON strategic brief with:
1. Core emotional tension
2. Key Saudi cultural moment
3. Sensory hook
4. Unspoken desire

Output format:
{
  "emotional_tension": "",
  "saudi_moment": "",
  "sensory_hook": "",
  "unspoken_desire": ""
}"""


def copy_prompt(product: str, ar: bool) -> str:
    if ar:
        return f"""أنت كاتب إعلانات سعودي محترف، معروف بقدرتك على كتابة قصص حسية وواقعية بالعامية السعودية.

**قواعد مهمة:**
- اكتب بالعربية ONLY
- استخدم العامية السعودية الطبيعية
- اسم المنتج هو: {product}

**البنية المطلوبة:**

[السطر الأول: hook - جملة افتتاحية قصيرة تنتهي بثلاث نقاط "..."]
[سطر فارغ]
[الفقرة الأولى: 3-4 جمل تصف الموقف والزمان والمكان]
[سطر فارغ]
[الفقرة الثانية: 3-4 جمل تصف التجربة الحسية]
[سطر فارغ]
[السطر الأخير: {product}. فائدة المنتج]

**أخرج JSON فقط:**
{{"narrative": "النص الكامل"}}"""
    return f"""You are an award-winning copywriter known for vivid, sensory storytelling.

**CRITICAL RULES:**
- Product name is: {product} - Use this EXACT name in the closing line
- Write in English

**Required Structure:**

[Opening hook line ending with "..."]
[blank line]
[Paragraph 1: 1-2 sentences describing the moment/setting]
[blank line]
[Paragraph 2: 1 sentence describing sensory experience]
[blank line]
[Closing line: {product}. [short benefit]]

**Output ONLY JSON:**
{{"narrative": "full text here"}}"""

# ================= INPUT PARSER =================

def parse_input(text: str) -> dict:
    """
    Parses a structured message in this format:

        Product: Mint & Lemon
        Description: Natural mint and lemon drink, no sugar
        Audience: University students, 18-30, health-conscious
        Voice: Authentic, Refreshing        (optional)
        Language: English                   (optional — English or Arabic)
    """
    data = {}
    for line in text.strip().splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            data[key.strip().lower()] = value.strip()
    return {
        "product":     data.get("product", ""),
        "description": data.get("description", ""),
        "audience":    data.get("audience", ""),
        "voice":       data.get("voice", "Authentic, Refreshing"),
        "language":    data.get("language", "English"),
    }

# ================= AGENT =================

@cycls.agent(image=image, web=web)
async def app(context):
    from openai import AsyncOpenAI

    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # Extract text from the latest message (guard against multimodal lists)
    raw = context.messages[-1]["content"]
    if isinstance(raw, list):
        raw = next((b["text"] for b in raw if b.get("type") == "text"), "")

    params = parse_input(raw)

    # Validate required fields
    missing = [f for f in ("product", "description", "audience") if not params[f]]
    if missing:
        yield (
            "**Please provide all required fields.** Use this format:\n\n"
            "```\n"
            "Product: Your Product Name\n"
            "Description: What it is\n"
            "Audience: Who it's for\n"
            "Voice: Brand tone        ← optional\n"
            "Language: English        ← optional (English or Arabic)\n"
            "```\n\n"
            "**Example:**\n"
            "```\n"
            "Product: Mint & Lemon\n"
            "Description: Natural mint and lemon drink, no sugar\n"
            "Audience: University students, 18-30, health-conscious\n"
            "Voice: Authentic, Refreshing\n"
            "Language: English\n"
            "```"
        )
        return

    is_arabic = params["language"].strip().lower() == "arabic"
    memory    = load_memory()

    # Step 1: Memory
    yield {"type": "status", "status": f"Loaded {len(memory)} prior campaign(s) from memory..."}

    # Step 2: Strategist
    yield {
        "type":     "thinking",
        "thinking": (
            f"Running strategist for: {params['product']}\n"
            f"Audience: {params['audience']} | Voice: {params['voice']}"
        ),
    }

    try:
        r1 = await safe_completion(
            client,
            model="gpt-4o-mini",
            temperature=0.7,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": strategist_prompt(is_arabic)},
                {
                    "role": "user",
                    "content": (
                        f"Previous memory:\n{memory_context()}\n\n"
                        f"Product: {params['product']}\n"
                        f"Description: {params['description']}\n"
                        f"Audience: {params['audience']}\n"
                        f"Voice: {params['voice']}"
                    ),
                },
            ],
        )
        strategic = safe_json_parse(r1.choices[0].message.content)
    except Exception as e:
        yield {"type": "callout", "style": "error", "title": "Strategist Failed", "callout": str(e)}
        return

    # Step 3: Copywriter
    yield {"type": "status", "status": "Strategy complete — writing campaign narrative..."}
    yield {
        "type":     "thinking",
        "thinking": f"Strategic brief:\n{json.dumps(strategic, ensure_ascii=False, indent=2)}",
    }

    try:
        r2 = await safe_completion(
            client,
            model="gpt-4o-mini",
            temperature=0.85,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": copy_prompt(params["product"], is_arabic)},
                {"role": "user",   "content": json.dumps(strategic, ensure_ascii=False)},
            ],
        )
        campaign  = safe_json_parse(r2.choices[0].message.content)
        narrative = campaign.get("narrative", "No output generated.")
    except Exception as e:
        yield {"type": "callout", "style": "error", "title": "Copywriter Failed", "callout": str(e)}
        return

    # Save to memory
    save_memory({
        "product":  params["product"],
        "tone":     params["voice"],
        "audience": params["audience"],
    })

    # Output
    yield {
        "type":    "callout",
        "style":   "success",
        "title":   "✅ Campaign Ready",
        "callout": f"Generated for: {params['product']} | Language: {params['language']}",
    }
    yield f"\n\n{narrative}"


# ================= ENTRY POINTS =================

if __name__ == "__main__":
    # Local dev:  python cycls_agent.py
    # Deploy:     cycls deploy cycls_agent.py   (recommended CLI approach)
    #             or swap .local() → .deploy() below
    app.local()