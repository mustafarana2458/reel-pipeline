"""Model backends shared by every LLM-driven agent (script, hook,
visual_prompt, motion, transition).

Each backend takes the same (system_prompt, user_prompt, json_schema) triple
and returns the parsed JSON object the model produced. `generate()` is the
one place that reads MODEL_PROVIDER -- every agent calls that single
function, so switching the whole pipeline from Gemini to Opus is one env
var change in agents/.env, not five.
"""

import json
import os

from config import ANTHROPIC_MODEL, GEMINI_MODEL, MODEL_PROVIDER


def generate_with_anthropic(system_prompt: str, user_prompt: str, json_schema: dict) -> dict:
    from anthropic import Anthropic

    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    response = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=8192,
        thinking={"type": "adaptive"},
        output_config={
            "effort": "high",
            "format": {"type": "json_schema", "schema": json_schema},
        },
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    for block in response.content:
        if block.type == "text":
            return json.loads(block.text)
    raise ValueError("No text block found in the Anthropic response")


def generate_with_gemini(system_prompt: str, user_prompt: str, json_schema: dict) -> dict:
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            response_mime_type="application/json",
            # Plain JSON Schema -- Gemini enforces this server-side (constrained
            # decoding), so the response is guaranteed to match the schema
            # instead of relying on the prompt alone.
            response_json_schema=json_schema,
        ),
    )
    return json.loads(response.text)


def generate(system_prompt: str, user_prompt: str, json_schema: dict) -> dict:
    """Dispatch to whichever backend MODEL_PROVIDER selects. Every text-generating
    agent calls this instead of picking a backend itself."""
    if MODEL_PROVIDER == "anthropic":
        return generate_with_anthropic(system_prompt, user_prompt, json_schema)
    if MODEL_PROVIDER == "gemini":
        return generate_with_gemini(system_prompt, user_prompt, json_schema)
    raise ValueError(
        f"Unknown MODEL_PROVIDER: {MODEL_PROVIDER!r} (expected 'anthropic' or 'gemini')"
    )
