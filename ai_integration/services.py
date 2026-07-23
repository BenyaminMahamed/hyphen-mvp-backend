import re


def generate_summary_and_actions(raw_text: str) -> dict:
    """
    Mock AI integration. Structured as though calling a real provider
    (e.g. an LLM API) so it can be swapped for a real call later without
    changing anything upstream.
    """
    # Split on line breaks first, then on periods within each line, so notes
    # written as separate lines (no trailing periods) are still broken into
    # distinct points rather than treated as one long sentence.
    lines = re.split(r"\n+", raw_text)
    sentences = [s.strip() for line in lines for s in line.split(".") if s.strip()]

    if not sentences:
        summary = "No notes provided."
    else:
        point_word = "key point" if len(sentences) == 1 else "key points"
        summary = f"Meeting covered {len(sentences)} {point_word}."

    action_items = [
        f"Follow up: {s}" for s in sentences if "to" in s.lower() or "follow" in s.lower()
    ][:5]

    return {
        "summary": summary,
        "action_items": action_items,
    }