def format_response_for_markdown(text):
    return (text or "").replace("$", r"\$")
