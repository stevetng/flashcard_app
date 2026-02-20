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
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY environment variable is not set. "
            "Get your API key at https://console.anthropic.com/"
        )

    client = anthropic.Anthropic(api_key=api_key)

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=16000,
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
        )
    except anthropic.AuthenticationError:
        raise RuntimeError("Invalid ANTHROPIC_API_KEY. Check your key and try again.")
    except anthropic.APIConnectionError:
        raise RuntimeError("Could not connect to the Anthropic API. Check your internet connection.")

    text_blocks = [b.text for b in response.content if b.type == "text"]
    if not text_blocks:
        raise RuntimeError("No text response received from the API.")

    raw = text_blocks[0].strip()
    if not raw:
        raise RuntimeError("Empty response received from the API.")

    data = json.loads(raw)
    if "flashcards" in data:
        return data["flashcards"]

    # If the model returned a raw array
    if isinstance(data, list):
        return data

    raise RuntimeError("Unexpected response format from the API.")
