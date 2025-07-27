from openai import OpenAI
import re
import tiktoken

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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"
)

def clean_ai_output(text: str) -> str:
    # Keep cleaning minimal to preserve full structure
    text = re.sub(r'\*{2,}|~{2,}', '', text)  # strip redundant asterisks/tilde
    text = re.sub(r'-{3,}|_{3,}', '', text)   # remove decorative dividers
    text = re.sub(r'^(Here are the notes:|Summary:|Let me help you.*?)\n+', '', text, flags=re.IGNORECASE)
    return text.strip()

def estimate_token_count(text: str) -> int:
    # Use tiktoken to estimate token count based on the model
    enc = tiktoken.encoding_for_model("gpt-3.5-turbo")  # close enough for Mistral
    return len(enc.encode(text))

def split_into_chunks(text: str, max_tokens=1800) -> list:
    paragraphs = text.split("\n\n")
    chunks = []
    current_chunk = []
    current_tokens = 0

    for para in paragraphs:
        token_count = estimate_token_count(para)
        if current_tokens + token_count > max_tokens:
            chunks.append("\n\n".join(current_chunk))
            current_chunk = [para]
            current_tokens = token_count
        else:
            current_chunk.append(para)
            current_tokens += token_count

    if current_chunk:
        chunks.append("\n\n".join(current_chunk))
    return chunks

def refine_notes_with_ai(text: str) -> str:
    prompt_system = (
        "You are a Markdown note formatter. Your task is to FORMAT the given educational note content strictly without altering or summarizing any content.\n\n"
        "✳️ DO NOT:\n"
        "- Remove or summarize any lines.\n"
        "- Shorten or combine paragraphs.\n"
        "- Skip or ignore any examples, references, or lists.\n\n"
        "✅ INSTEAD, apply these formatting rules:\n"
        "- Use proper **Markdown formatting**.\n"
        "- Make main headings and subheadings with ## or ###.\n"
        "- Bold key terms (e.g., **Contract**, **Offer**, **Acceptance**).\n"
        "- Use numbered lists (1., 2., 3.) and bullet points (- or *) where appropriate.\n"
        "- Format legal cases and examples using _italics_ or > blockquotes if needed.\n"
        "- Add line breaks and spacing to separate logical sections clearly.\n\n"
        "⚠️ Never change the original content, numbers, or ordering. Your output must contain the same amount of information in improved form only."
    )

    chunks = split_into_chunks(text)
    formatted_chunks = []

    for i, chunk in enumerate(chunks):
        print(f"[AI] Processing chunk {i+1}/{len(chunks)}...")
        response = client.chat.completions.create(
            model="mistralai/mistral-7b-instruct",
            messages=[
                {"role": "system", "content": prompt_system},
                {"role": "user", "content": chunk}
            ],
            temperature=0.0,
            max_tokens=2048,
        )
        ai_output = response.choices[0].message.content
        cleaned = clean_ai_output(ai_output)
        formatted_chunks.append(cleaned)

    return "\n\n".join(formatted_chunks)
