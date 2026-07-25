"""transition_agent -- single job: assign a transition to every beat.

Doesn't touch text, visualPrompt, motion, or image. A beat's transition
describes how it enters FROM the previous beat -- the first beat has no
previous beat, so its transition is always forced to "cut" regardless of
what the model says.
"""

import json

from constants import TRANSITIONS
from providers import generate
from state import GraphState

SYSTEM_PROMPT = f"""You choreograph cut points for a fast-paced short-form vertical video.

You'll be given a numbered list of on-screen text beats. For each beat, assign the \
transition used to enter it FROM the previous beat, from exactly this set: {TRANSITIONS}.

Guidelines:
- "cut" is a hard, instant cut -- use it most often, it's the default rhythm.
- "whip" is a fast directional whip-pan -- good for a change of subject or a beat that \
picks up energy.
- "glitch" is a jarring stutter/RGB-split -- good for shock beats, punchlines, or "wait, \
what?" moments. Use it sparingly for it to land.
- Vary transitions across the sequence and use all {len(TRANSITIONS)} somewhere, but \
don't overuse "whip"/"glitch" back-to-back.
- Beat id 1 has no previous beat -- whatever you assign it will be ignored and forced to \
"cut", so don't worry about it.

Respond with ONLY a single JSON object of this exact shape, no other text, with one entry \
per beat id you were given:
{{"beats": [{{"id": 1, "transition": "..."}}, ...]}}"""

SCHEMA = {
    "type": "object",
    "properties": {
        "beats": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "transition": {"type": "string", "enum": TRANSITIONS},
                },
                "required": ["id", "transition"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["beats"],
    "additionalProperties": False,
}


def transition_agent(state: GraphState) -> GraphState:
    topic = state["topic"]
    beats = state["beats"]

    beats_for_prompt = [{"id": beat["id"], "text": beat["text"]} for beat in beats]
    user_prompt = (
        f'Topic: "{topic}"\n\n'
        f"Beats:\n{json.dumps(beats_for_prompt, indent=2)}\n\n"
        f"Assign a transition to every beat id above."
    )

    parsed = generate(SYSTEM_PROMPT, user_prompt, SCHEMA)
    transition_by_id = {beat["id"]: beat["transition"] for beat in parsed["beats"]}

    missing = [beat["id"] for beat in beats if beat["id"] not in transition_by_id]
    if missing:
        raise ValueError(f"Model didn't return a transition for beat ids: {missing}")

    for beat in beats:
        beat["transition"] = transition_by_id[beat["id"]]

    if beats:
        beats[0]["transition"] = "cut"  # no previous beat to transition from

    return {"topic": topic, "beats": beats}
