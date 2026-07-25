"""LangGraph node: turn each beat's visualPrompt into an actual image file.

Uses Gemini's image-generation model. If generation fails for a beat --
quota, an unavailable model, a transient error -- that beat falls back to a
locally-drawn placeholder image instead of failing the whole pipeline, so a
handful of bad calls never blocks the run.
"""

import os
import time

from PIL import Image, ImageDraw, ImageFont

from config import GEMINI_IMAGE_MODEL
from state import GraphState

IMAGE_DIR = os.path.join(os.path.dirname(__file__), "output", "images")
IMAGE_SIZE = (540, 960)  # 1080x1920 at half-scale -- plenty for a placeholder/test asset
REQUEST_DELAY_SECONDS = 2  # be gentle with free-tier per-minute rate limits

PLACEHOLDER_COLORS = [
    "#1f2937",
    "#7c2d12",
    "#14532d",
    "#312e81",
    "#701a75",
]


def _draw_placeholder(beat_id: int, prompt: str) -> Image.Image:
    color = PLACEHOLDER_COLORS[beat_id % len(PLACEHOLDER_COLORS)]
    img = Image.new("RGB", IMAGE_SIZE, color=color)
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 28)
    except OSError:
        font = ImageFont.load_default()

    margin = 40
    words = prompt.split()
    lines: list[str] = []
    current = ""
    for word in words:
        trial = f"{current} {word}".strip()
        if draw.textlength(trial, font=font) > IMAGE_SIZE[0] - 2 * margin:
            lines.append(current)
            current = word
        else:
            current = trial
    if current:
        lines.append(current)

    line_height = 36
    total_height = len(lines) * line_height
    y = (IMAGE_SIZE[1] - total_height) // 2
    for line in lines:
        w = draw.textlength(line, font=font)
        x = (IMAGE_SIZE[0] - w) // 2
        draw.text((x, y), line, fill="white", font=font)
        y += line_height

    return img


def _generate_with_gemini(prompt: str) -> Image.Image | None:
    from google import genai
    from google.genai import types
    from io import BytesIO

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    response = client.models.generate_content(
        model=GEMINI_IMAGE_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(response_modalities=["TEXT", "IMAGE"]),
    )

    for candidate in response.candidates or []:
        for part in candidate.content.parts or []:
            inline_data = getattr(part, "inline_data", None)
            if inline_data is not None:
                return Image.open(BytesIO(inline_data.data))
    return None


def asset_agent(state: GraphState) -> GraphState:
    os.makedirs(IMAGE_DIR, exist_ok=True)
    beats = state["beats"]

    for index, beat in enumerate(beats):
        filename = f"beat_{beat['id']:02d}.png"
        path = os.path.join(IMAGE_DIR, filename)

        image: Image.Image | None = None
        try:
            image = _generate_with_gemini(beat["visualPrompt"])
        except Exception as exc:
            print(f"[asset_agent] beat {beat['id']:02d}: Gemini image gen failed ({exc}); using placeholder")

        if image is None:
            image = _draw_placeholder(beat["id"], beat["visualPrompt"])

        image.save(path)
        beat["image"] = f"images/{filename}"

        if index < len(beats) - 1:
            time.sleep(REQUEST_DELAY_SECONDS)

    return {"topic": state["topic"], "beats": beats}
