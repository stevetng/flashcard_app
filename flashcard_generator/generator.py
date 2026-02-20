"""Generate flashcards from slide content using the Claude API."""

import json
import os
import sys

import anthropic

SYSTEM_PROMPT = """\
You are an expert educator who creates effective study flashcards. Given the \
content of a PowerPoint presentation, generate flashcards that cover the key \
concepts, definitions, facts, and relationships presented in the slides.

Guidelines:
- Create concise, focused flashcards — one concept per card.
- Front side should be a clear question or prompt.
- Back side should be a direct, accurate answer.
- Cover the most important and testable material.
- Use varied question formats: definitions, comparisons, cause/effect, \
fill-in-the-blank, etc.
- Do not create trivial or obvious flashcards.
- If slides contain formulas, include them on the appropriate side.
- Aim for 2-4 flashcards per content-rich slide, fewer for light slides."""

OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "flashcards": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "front": {
                        "type": "string",
                        "description": "The question or prompt on the front of the card."
                    },
                    "back": {
                        "type": "string",
                        "description": "The answer on the back of the card."
                    },
                    "slide": {
                        "type": "integer",
                        "description": "The slide number this card relates to."
                    }
                },
                "required": ["front", "back", "slide"],
                "additionalProperties": False
            }
        }
    },
    "required": ["flashcards"],
    "additionalProperties": False
}


def generate_flashcards(slide_text: str) -> list[dict]:
    """Send slide content to Claude and return a list of flashcard dicts.

    Each dict has keys: front, back, slide.
    Requires the ANTHROPIC_API_KEY environment variable to be set.
    """
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print(
            "Error: ANTHROPIC_API_KEY environment variable is not set.\n"
            "Get your API key at https://console.anthropic.com/ and run:\n"
            "  export ANTHROPIC_API_KEY='your-key-here'",
            file=sys.stderr,
        )
        sys.exit(1)

    client = anthropic.Anthropic()

    try:
        with client.messages.stream(
            model="claude-opus-4-6",
            max_tokens=16000,
            thinking={"type": "adaptive"},
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": (
                        "Here is the content extracted from a PowerPoint presentation. "
                        "Generate study flashcards covering the key material.\n\n"
                        f"{slide_text}"
                    ),
                }
            ],
            output_config={
                "format": {
                    "type": "json_schema",
                    "schema": OUTPUT_SCHEMA,
                }
            },
        ) as stream:
            response = stream.get_final_message()
    except anthropic.AuthenticationError:
        print("Error: Invalid ANTHROPIC_API_KEY. Check your key and try again.",
              file=sys.stderr)
        sys.exit(1)
    except anthropic.APIConnectionError:
        print("Error: Could not connect to the Anthropic API. Check your internet connection.",
              file=sys.stderr)
        sys.exit(1)

    text = next(b.text for b in response.content if b.type == "text")
    data = json.loads(text)
    return data["flashcards"]
