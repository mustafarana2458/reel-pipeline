"""script_agent -- single job: write the 60 on-screen text beats for the topic.

Does NOT assign visualPrompt, motion, or transition -- those belong to
visual_prompt_agent, motion_agent, and transition_agent respectively.
"""

from constants import BEAT_COUNT
from providers import generate
from state import Beat, GraphState

SYSTEM_PROMPT = f"""You are the script-writing stage of a short-form vertical video pipeline.

Given a topic, write exactly {BEAT_COUNT} sequential "beats" of on-screen text for a \
fast-paced ~{BEAT_COUNT * 0.5:.0f}-second vertical video (each beat is a 0.5 second \
on-screen block). Each beat needs only:

- id: sequential integer starting at 1
- text: short on-screen text for that beat (a few words to one short sentence -- \
it must read in half a second)

The beats should tell a coherent, escalating story about the topic from hook to payoff, \
not be {BEAT_COUNT} disconnected facts.

Do NOT include image prompts, motion, or transitions -- other stages handle those.

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


def script_agent(state: GraphState) -> GraphState:
    topic = state["topic"]
    user_prompt = f'Topic: "{topic}"\n\nGenerate the {BEAT_COUNT} beats now.'

    parsed = generate(SYSTEM_PROMPT, user_prompt, SCHEMA)
    beats: list[Beat] = parsed["beats"]

    if len(beats) != BEAT_COUNT:
        raise ValueError(f"Expected exactly {BEAT_COUNT} beats, model returned {len(beats)}")

    return {"topic": topic, "beats": beats}
