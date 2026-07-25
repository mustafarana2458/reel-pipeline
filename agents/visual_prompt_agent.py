"""visual_prompt_agent -- single job: turn each beat's text into a concise
text-to-image prompt (visualPrompt). Doesn't touch text, motion, transition,
or image -- asset_agent is the one that turns visualPrompt into a real image.
"""

import json

from providers import generate
from state import GraphState

SYSTEM_PROMPT = """You write text-to-image prompts for a short-form vertical video.

You'll be given a numbered list of on-screen text beats. For each beat, write a concise \
visualPrompt describing the visual that should accompany that text on screen -- concrete \
subject, setting, and mood, suitable for feeding directly to an image generator. Keep \
prompts visually specific (not abstract), and keep a consistent visual style across all \
beats so the video doesn't look like a random collage.

Respond with ONLY a single JSON object of this exact shape, no other text, with one entry \
per beat id you were given:
{"beats": [{"id": 1, "visualPrompt": "..."}, ...]}"""

SCHEMA = {
    "type": "object",
    "properties": {
        "beats": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "visualPrompt": {"type": "string"},
                },
                "required": ["id", "visualPrompt"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["beats"],
    "additionalProperties": False,
}


def visual_prompt_agent(state: GraphState) -> GraphState:
    topic = state["topic"]
    beats = state["beats"]

    beats_for_prompt = [{"id": beat["id"], "text": beat["text"]} for beat in beats]
    user_prompt = (
        f'Topic: "{topic}"\n\n'
        f"Beats:\n{json.dumps(beats_for_prompt, indent=2)}\n\n"
        f"Generate a visualPrompt for every beat id above."
    )

    parsed = generate(SYSTEM_PROMPT, user_prompt, SCHEMA)
    prompt_by_id = {beat["id"]: beat["visualPrompt"] for beat in parsed["beats"]}

    missing = [beat["id"] for beat in beats if beat["id"] not in prompt_by_id]
    if missing:
        raise ValueError(f"Model didn't return a visualPrompt for beat ids: {missing}")

    for beat in beats:
        beat["visualPrompt"] = prompt_by_id[beat["id"]]

    return {"topic": topic, "beats": beats}
