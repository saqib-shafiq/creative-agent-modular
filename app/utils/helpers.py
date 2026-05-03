import asyncio
import json


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