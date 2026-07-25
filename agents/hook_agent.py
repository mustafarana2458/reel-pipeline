"""hook_agent -- single job: rewrite the first HOOK_BEAT_COUNT beats' text into
a stronger, scroll-stopping hook. Touches nothing else -- doesn't add beats,
doesn't remove beats, doesn't touch visualPrompt/motion/transition/image.
"""

import json

from constants import HOOK_BEAT_COUNT
from providers import generate
from state import GraphState

SYSTEM_PROMPT = f"""You specialize in the opening seconds of short-form vertical video.

You'll be given a topic and the first {HOOK_BEAT_COUNT} on-screen text beats a script \
writer already drafted for it. Rewrite ONLY those {HOOK_BEAT_COUNT} beats to be a \
stronger, more scroll-stopping hook: a bold claim, a curiosity gap, or a surprising \
statement that makes someone stop scrolling in the first half-second.

Keep exactly {HOOK_BEAT_COUNT} beats with the same ids. Each beat's text still needs \
to read in about half a second. Do not change anything about the rest of the video --
you only see and only touch these {HOOK_BEAT_COUNT} beats.

Respond with ONLY a single JSON object of this exact shape, no other text:
{{"beats": [{{"id": 1, "text": "..."}}, ...]}}"""

SCHEMA = {
    "type": "object",
    "properties": {
        "beats": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "text": {"type": "string"},
                },
                "required": ["id", "text"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["beats"],
    "additionalProperties": False,
}


def hook_agent(state: GraphState) -> GraphState:
    topic = state["topic"]
    beats = state["beats"]
    original_hook = beats[:HOOK_BEAT_COUNT]

    user_prompt = (
        f'Topic: "{topic}"\n\n'
        f"Current first {HOOK_BEAT_COUNT} beats:\n"
        f"{json.dumps(original_hook, indent=2)}\n\n"
        f"Rewrite them into a stronger hook."
    )

    parsed = generate(SYSTEM_PROMPT, user_prompt, SCHEMA)
    new_hook = parsed["beats"]

    if len(new_hook) != HOOK_BEAT_COUNT:
        raise ValueError(
            f"Expected exactly {HOOK_BEAT_COUNT} hook beats, model returned {len(new_hook)}"
        )

    text_by_id = {beat["id"]: beat["text"] for beat in new_hook}
    for beat in beats[:HOOK_BEAT_COUNT]:
        if beat["id"] in text_by_id:
            beat["text"] = text_by_id[beat["id"]]

    return {"topic": topic, "beats": beats}
