"""render_agent -- single job: hand the final beats to the Remotion project
and render the video. Only runs if qc_agent marked the state valid (wired up
in supervisor_agent's conditional edge) -- it doesn't re-validate anything
itself.
"""

import json
import os
import subprocess

from state import GraphState

REMOTION_PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
REMOTION_BEATS_PATH = os.path.join(REMOTION_PROJECT_DIR, "src", "beats.json")
RENDER_OUTPUT_PATH = os.path.join(REMOTION_PROJECT_DIR, "out", "video.mp4")
RENDER_TIMEOUT_SECONDS = 900


def _to_remotion_beats(beats: list[dict]) -> list[dict]:
    """Adapt pipeline beats to the exact shape src/beats.json (Remotion) reads."""
    return [
        {
            "id": beat["id"],
            "text": beat["text"],
            "image": beat.get("image", "placeholder"),
            "motion": beat["motion"],
            "transition": beat["transition"],
        }
        for beat in beats
    ]


def render_agent(state: GraphState) -> GraphState:
    beats = state["beats"]

    with open(REMOTION_BEATS_PATH, "w", encoding="utf-8") as f:
        json.dump(_to_remotion_beats(beats), f, indent=2)
    print(f"[render_agent] wrote {REMOTION_BEATS_PATH}")

    print("[render_agent] running `npm run build`...")
    try:
        result = subprocess.run(
            "npm run build",
            cwd=REMOTION_PROJECT_DIR,
            shell=True,
            capture_output=True,
            text=True,
            timeout=RENDER_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        print(f"[render_agent] render timed out after {RENDER_TIMEOUT_SECONDS}s")
        return {
            "topic": state["topic"],
            "beats": beats,
            "qc_report": state.get("qc_report"),
            "render_output_path": "",
        }

    if result.returncode != 0:
        print("[render_agent] render FAILED")
        print(result.stdout[-2000:])
        print(result.stderr[-2000:])
        return {
            "topic": state["topic"],
            "beats": beats,
            "qc_report": state.get("qc_report"),
            "render_output_path": "",
        }

    print(f"[render_agent] render OK -> {RENDER_OUTPUT_PATH}")
    return {
        "topic": state["topic"],
        "beats": beats,
        "qc_report": state.get("qc_report"),
        "render_output_path": RENDER_OUTPUT_PATH,
    }
