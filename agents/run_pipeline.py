import argparse
import json
import os

from dotenv import load_dotenv

from config import MODEL_PROVIDER
from supervisor_agent import run_pipeline

REQUIRED_KEY_BY_PROVIDER = {
    "gemini": "GEMINI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
}

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")


def main() -> None:
    load_dotenv()

    parser = argparse.ArgumentParser(description="Run the full multi-agent pipeline on a topic")
    parser.add_argument(
        "topic",
        nargs="?",
        default="5 psychology tricks to make people like you instantly",
        help="Topic to generate the 60-beat video for",
    )
    args = parser.parse_args()

    required_key = REQUIRED_KEY_BY_PROVIDER.get(MODEL_PROVIDER)
    if required_key is None:
        raise SystemExit(
            f"Unknown MODEL_PROVIDER: {MODEL_PROVIDER!r} (expected 'gemini' or 'anthropic')"
        )
    if not os.environ.get(required_key):
        raise SystemExit(
            f"MODEL_PROVIDER={MODEL_PROVIDER!r} but {required_key} is not set. "
            f"Set it in agents/.env."
        )

    print(f"Topic: {args.topic}")
    print(f"Provider: {MODEL_PROVIDER}\n")

    result = run_pipeline(args.topic)
    beats = result["beats"]
    qc_report = result.get("qc_report")
    render_output_path = result.get("render_output_path")

    print(f"Generated {len(beats)} beats\n")
    for beat in beats:
        print(
            f"[{beat['id']:02d}] ({beat.get('motion', '?'):<8} / {beat.get('transition', '?'):<6}) "
            f"{beat['text']:<40} -> {beat.get('image', '(no image)')}"
        )

    print("\n--- QC report ---")
    if qc_report is None:
        print("qc_agent did not run")
    else:
        print(f"valid: {qc_report['valid']}")
        print(f"beat_count: {qc_report['beat_count']}")
        print(
            f"total_duration: {qc_report['total_duration_frames']} frames "
            f"({qc_report['total_duration_seconds']:.2f}s)"
        )
        for error in qc_report["errors"]:
            print(f"  ERROR: {error}")

    print("\n--- Render ---")
    if render_output_path:
        print(f"Rendered video: {render_output_path}")
    elif qc_report is not None and not qc_report["valid"]:
        print("Skipped -- QC failed, see errors above")
    else:
        print("Render did not produce an output path (check logs above)")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    raw_path = os.path.join(OUTPUT_DIR, "beats_raw.json")
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(beats, f, indent=2)
    print(f"\nWrote {raw_path}")

    if qc_report is not None:
        qc_path = os.path.join(OUTPUT_DIR, "qc_report.json")
        with open(qc_path, "w", encoding="utf-8") as f:
            json.dump(qc_report, f, indent=2)
        print(f"Wrote {qc_path}")


if __name__ == "__main__":
    main()
