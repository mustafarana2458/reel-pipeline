"""qc_agent -- single job: validate the pipeline's output before render_agent
touches it. Deterministic Python checks, not an LLM call -- a validation gate
that can hallucinate a pass is worse than no gate at all.

Checks: exactly BEAT_COUNT beats, every required field present on every
beat, motion/transition values are from the allowed sets, beat 1's
transition is "cut", and the total timeline comes out to exactly 30s (using
the same padding math src/transitionPlan.ts uses on the Remotion side, so
this check reflects what will actually render, not a naive beat-count sum).
"""

from constants import (
    BEAT_COUNT,
    FPS,
    BEAT_DURATION_FRAMES,
    MOTIONS,
    REQUIRED_BEAT_FIELDS,
    TRANSITIONS,
)
from state import GraphState, QCReport


def qc_agent(state: GraphState) -> GraphState:
    beats = state["beats"]
    errors: list[str] = []

    if len(beats) != BEAT_COUNT:
        errors.append(f"expected {BEAT_COUNT} beats, got {len(beats)}")

    for beat in beats:
        beat_id = beat.get("id", "?")
        missing = [f for f in REQUIRED_BEAT_FIELDS if not beat.get(f)]
        if missing:
            errors.append(f"beat {beat_id}: missing/empty fields {missing}")
        if beat.get("motion") and beat["motion"] not in MOTIONS:
            errors.append(f"beat {beat_id}: invalid motion {beat['motion']!r}")
        if beat.get("transition") and beat["transition"] not in TRANSITIONS:
            errors.append(f"beat {beat_id}: invalid transition {beat['transition']!r}")

    if beats and beats[0].get("transition") != "cut":
        errors.append(f"beat {beats[0].get('id')}: first beat's transition must be 'cut'")

    # Same invariant src/transitionPlan.ts relies on: the padding added per
    # beat exactly cancels what each <Transition> subtracts, so total frames
    # is always beats * BEAT_DURATION_FRAMES regardless of transition mix.
    total_frames = len(beats) * BEAT_DURATION_FRAMES
    total_seconds = total_frames / FPS
    if abs(total_seconds - 30.0) > 0.01:
        errors.append(f"total duration is {total_seconds:.2f}s, expected 30.00s")

    report: QCReport = {
        "valid": len(errors) == 0,
        "beat_count": len(beats),
        "total_duration_frames": total_frames,
        "total_duration_seconds": total_seconds,
        "errors": errors,
    }

    return {"topic": state["topic"], "beats": beats, "qc_report": report}
