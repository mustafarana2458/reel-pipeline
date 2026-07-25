"""motion_agent -- single job: assign a motion to every beat.

Doesn't touch text, visualPrompt, transition, or image -- only decides which
of MOTIONS each beat gets, based on the beat's content and pacing.
"""

import json

from constants import MOTIONS
from providers import generate
from state import GraphState

SYSTEM_PROMPT = f"""You choreograph camera motion for a fast-paced short-form vertical video.

You'll be given a numbered list of on-screen text beats. For each beat, assign one motion \
from exactly this set: {MOTIONS}.

Guidelines:
- Vary the motion across beats so the video doesn't feel repetitive -- avoid the same \
motion for more than 2-3 beats in a row.
- Use all {len(MOTIONS)} motions somewhere in the sequence.
- "shake" reads as urgency/shock -- good for surprising or emphatic beats.
- "zoom-in" reads as emphasis/reveal -- good for punchlines or key facts.
- "pan-left" and "tilt" are calmer -- good for connecting/narrative beats.

Respond with ONLY a single JSON object of this exact shape, no other text, with one entry \
per beat id you were given:
{{"beats": [{{"id": 1, "motion": "..."}}, ...]}}"""

SCHEMA = {
    "type": "object",
    "properties": {
        "beats": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "motion": {"type": "string", "enum": MOTIONS},
                },
                "required": ["id", "motion"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["beats"],
    "additionalProperties": False,
}


def motion_agent(state: GraphState) -> GraphState:
    topic = state["topic"]
    beats = state["beats"]

    beats_for_prompt = [{"id": beat["id"], "text": beat["text"]} for beat in beats]
    user_prompt = (
        f'Topic: "{topic}"\n\n'
        f"Beats:\n{json.dumps(beats_for_prompt, indent=2)}\n\n"
        f"Assign a motion to every beat id above."
    )

    parsed = generate(SYSTEM_PROMPT, user_prompt, SCHEMA)
    motion_by_id = {beat["id"]: beat["motion"] for beat in parsed["beats"]}

    missing = [beat["id"] for beat in beats if beat["id"] not in motion_by_id]
    if missing:
        raise ValueError(f"Model didn't return a motion for beat ids: {missing}")

    for beat in beats:
        beat["motion"] = motion_by_id[beat["id"]]

    return {"topic": topic, "beats": beats}
