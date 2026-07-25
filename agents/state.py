from typing import NotRequired, TypedDict


class Beat(TypedDict):
    id: int
    text: str
    # Filled in by later agents -- absent until that stage runs.
    visualPrompt: NotRequired[str]
    motion: NotRequired[str]
    transition: NotRequired[str]
    image: NotRequired[str]


class QCReport(TypedDict):
    valid: bool
    beat_count: int
    total_duration_frames: int
    total_duration_seconds: float
    errors: list[str]


class GraphState(TypedDict):
    topic: str
    beats: list[Beat]
    # Filled in by qc_agent / render_agent -- absent until those stages run.
    qc_report: NotRequired[QCReport]
    render_output_path: NotRequired[str]
