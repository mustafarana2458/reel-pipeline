import os

# Single switch for which backend script_agent.py calls. Flip back to Opus
# later by setting MODEL_PROVIDER=anthropic (in agents/.env) -- no code changes.
MODEL_PROVIDER = os.environ.get("MODEL_PROVIDER", "gemini").lower()

ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-opus-4-8")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-flash-latest")

# Used by asset_agent.py for image generation. Falls back to a drawn
# placeholder per-beat if this model 404s/429s on the configured key.
GEMINI_IMAGE_MODEL = os.environ.get("GEMINI_IMAGE_MODEL", "gemini-2.5-flash-image")
