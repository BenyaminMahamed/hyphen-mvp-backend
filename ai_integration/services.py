def generate_summary_and_actions(raw_text: str) -> dict:
    """
    Mock AI integration. Structured as though calling a real provider
    (e.g. an LLM API) so it can be swapped for a real call later without
    changing anything upstream.
    """
    sentences = [s.strip() for s in raw_text.split(".") if s.strip()]

    summary = f"Meeting covered {len(sentences)} key points." if sentences else "No notes provided."

    action_items = [
        f"Follow up: {s}" for s in sentences if "to" in s.lower() or "follow" in s.lower()
    ][:5]

    return {
        "summary": summary,
        "action_items": action_items,
    }
