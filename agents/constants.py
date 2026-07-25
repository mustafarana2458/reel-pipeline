"""Shared constants used by multiple agents -- one source of truth so
script_agent, motion_agent, transition_agent, and qc_agent never drift apart
on what a valid beat looks like.
"""

BEAT_COUNT = 60
HOOK_BEAT_COUNT = 3  # how many opening beats hook_agent is allowed to rewrite

MOTIONS = ["zoom-in", "pan-left", "shake", "tilt"]
TRANSITIONS = ["cut", "whip", "glitch"]

FPS = 30
BEAT_DURATION_FRAMES = 15  # 0.5s per beat at 30fps

# Mirrors src/transitionPlan.ts on the Remotion side: "cut" costs no frames,
# "whip"/"glitch" overlap adjacent beats for their duration (padded out by
# Remotion so the total stays exactly BEAT_COUNT * BEAT_DURATION_FRAMES).
TRANSITION_DURATIONS = {"cut": 0, "whip": 6, "glitch": 8}

REQUIRED_BEAT_FIELDS = ["id", "text", "visualPrompt", "motion", "transition", "image"]
