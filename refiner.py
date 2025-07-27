import os
import re
import tiktoken
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# Ensure the required environment variables are set
base_url = os.getenv("OPENAI_BASE_URL")
api_key = os.getenv("OPENAI_API_KEY")
if not base_url or not api_key:
    raise EnvironmentError("Missing OPENAI_BASE_URL or OPENAI_API_KEY in .env")

# Initialize OpenAI client
client = OpenAI(
    base_url=base_url,
    api_key=api_key
)

def clean_ai_output(text: str) -> str:
    """Clean unnecessary formatting artifacts from AI response"""
    text = re.sub(r'\*{2,}|~{2,}', '', text)  # remove excessive ** or ~~
    text = re.sub(r'-{3,}|_{3,}', '', text)   # remove decorative dividers
    text = re.sub(r'^(Here are the notes:|Summary:|Let me help you.*?)\n+', '', text, flags=re.IGNORECASE)
    return text.strip()

def estimate_token_count(text: str) -> int:
    """Estimate token count using tiktoken encoding"""
    enc = tiktoken.encoding_for_model("gpt-3.5-turbo")  # good approximation for Mistral
    return len(enc.encode(text))

def split_into_chunks(text: str, max_tokens: int = 1800) -> list[str]:
    """Split text into token-safe chunks"""
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
    """Format notes using OpenAI with strict Markdown rules (no content changes)"""
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
        try:
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
        except Exception as e:
            print(f"[ERROR] Failed to process chunk {i+1}: {e}")
            continue

    return "\n\n".join(formatted_chunks)
