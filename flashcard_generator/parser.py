"""Extract text content from PowerPoint files."""

from pptx import Presentation
from pptx.util import Inches


def extract_slides(pptx_path: str) -> list[dict]:
    """Parse a .pptx file and return structured slide content.

    Returns a list of dicts with keys: slide_number, title, body.
    """
    prs = Presentation(pptx_path)
    slides = []

    for i, slide in enumerate(prs.slides, start=1):
        title = ""
        body_parts = []

        for shape in slide.shapes:
            if shape.has_text_frame:
                text = shape.text_frame.text.strip()
                if not text:
                    continue
                if shape == slide.shapes.title:
                    title = text
                else:
                    body_parts.append(text)

            if shape.has_table:
                table = shape.table
                rows = []
                for row in table.rows:
                    cells = [cell.text.strip() for cell in row.cells]
                    rows.append(" | ".join(cells))
                body_parts.append("\n".join(rows))

        body = "\n".join(body_parts)

        if title or body:
            slides.append({
                "slide_number": i,
                "title": title,
                "body": body,
            })

    return slides


def format_slides_for_prompt(slides: list[dict]) -> str:
    """Format extracted slides into a text representation for the AI prompt."""
    parts = []
    for slide in slides:
        header = f"--- Slide {slide['slide_number']}"
        if slide["title"]:
            header += f": {slide['title']}"
        header += " ---"
        parts.append(header)
        if slide["body"]:
            parts.append(slide["body"])
        parts.append("")
    return "\n".join(parts)
