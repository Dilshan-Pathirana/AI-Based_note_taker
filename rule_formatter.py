import re

def format_text(raw_text: str) -> str:
    lines = raw_text.splitlines()
    formatted = []

    for line in lines:
        line = line.strip()

        # Bold topic headings
        if re.match(r'^(lesson|chapter)\b.*', line, re.IGNORECASE):
            formatted.append(f"## **{line}**")
            continue

        # Numbered list correction
        line = re.sub(r'^(\d+)[\.\)]\s*', r'\1. ', line)

        # Bullet list normalization
        line = re.sub(r'^[-•*]\s*', '- ', line)

        # Highlight case laws and examples
        line = re.sub(r'(eg|e\.g\.|example)\b[:,]?', r'**Example:**', line, flags=re.IGNORECASE)
        line = re.sub(r'([A-Z][a-z]+ v\. [A-Z][a-z]+)', r'**\1**', line)  # Case law highlighting

        formatted.append(line)

    return "\n".join(formatted)
