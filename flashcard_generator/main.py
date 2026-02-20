"""CLI entry point for the PowerPoint flashcard generator."""

import argparse
import json
import os
import sys

from .parser import extract_slides, format_slides_for_prompt
from .generator import generate_flashcards
from .study import run_study_session


def save_flashcards(flashcards: list[dict], path: str):
    """Save flashcards to a JSON file."""
    with open(path, "w") as f:
        json.dump({"flashcards": flashcards}, f, indent=2)
    print(f"Saved {len(flashcards)} flashcards to {path}")


def load_flashcards(path: str) -> list[dict]:
    """Load flashcards from a JSON file."""
    with open(path) as f:
        data = json.load(f)
    return data["flashcards"]


def main():
    parser = argparse.ArgumentParser(
        description="Generate study flashcards from PowerPoint presentations using Claude AI."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- generate ---
    gen_parser = subparsers.add_parser(
        "generate",
        help="Generate flashcards from a .pptx file."
    )
    gen_parser.add_argument(
        "pptx_file",
        help="Path to the PowerPoint (.pptx) file."
    )
    gen_parser.add_argument(
        "-o", "--output",
        help="Save flashcards to a JSON file instead of starting a study session."
    )
    gen_parser.add_argument(
        "--study",
        action="store_true",
        default=False,
        help="Start an interactive study session after generating."
    )

    # --- study ---
    study_parser = subparsers.add_parser(
        "study",
        help="Study from a previously saved flashcard JSON file."
    )
    study_parser.add_argument(
        "json_file",
        help="Path to a flashcard JSON file."
    )

    # --- view ---
    view_parser = subparsers.add_parser(
        "view",
        help="View all flashcards in a saved JSON file."
    )
    view_parser.add_argument(
        "json_file",
        help="Path to a flashcard JSON file."
    )

    args = parser.parse_args()

    if args.command == "generate":
        pptx_path = args.pptx_file
        if not os.path.isfile(pptx_path):
            print(f"Error: file not found: {pptx_path}", file=sys.stderr)
            sys.exit(1)
        if not pptx_path.lower().endswith(".pptx"):
            print("Warning: file does not have a .pptx extension.", file=sys.stderr)

        print(f"Parsing {pptx_path}...")
        slides = extract_slides(pptx_path)
        if not slides:
            print("No text content found in the presentation.", file=sys.stderr)
            sys.exit(1)
        print(f"Extracted content from {len(slides)} slides.")

        slide_text = format_slides_for_prompt(slides)

        print("Generating flashcards with Claude...")
        flashcards = generate_flashcards(slide_text)
        print(f"Generated {len(flashcards)} flashcards.")

        if args.output:
            save_flashcards(flashcards, args.output)

        if args.study or not args.output:
            run_study_session(flashcards)
        elif not args.study and args.output:
            print(f"Run `flashcard-generator study {args.output}` to study later.")

    elif args.command == "study":
        json_path = args.json_file
        if not os.path.isfile(json_path):
            print(f"Error: file not found: {json_path}", file=sys.stderr)
            sys.exit(1)

        flashcards = load_flashcards(json_path)
        print(f"Loaded {len(flashcards)} flashcards.")
        run_study_session(flashcards)

    elif args.command == "view":
        json_path = args.json_file
        if not os.path.isfile(json_path):
            print(f"Error: file not found: {json_path}", file=sys.stderr)
            sys.exit(1)

        flashcards = load_flashcards(json_path)
        print(f"\n{len(flashcards)} flashcards:\n")
        for i, card in enumerate(flashcards, 1):
            print(f"  [{i}] (Slide {card['slide']})")
            print(f"      Q: {card['front']}")
            print(f"      A: {card['back']}")
            print()


if __name__ == "__main__":
    main()
