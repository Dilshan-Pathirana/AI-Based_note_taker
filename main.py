import os
from openai import OpenAI
from dotenv import load_dotenv
from image_utils import extract_text_preserve_all
from refiner import refine_notes_with_ai
from pdf_generator import generate_pdf_from_markdown

load_dotenv() 

client = OpenAI(
    base_url=os.getenv("OPENAI_BASE_URL"),
    api_key=os.getenv("OPENAI_API_KEY")
)

def scan_images(folder_path):
    """
    Scan images folder and return extracted raw text as a single string.
    Raises exception on failure.
    """
    lines = extract_text_preserve_all(folder_path)
    return "\n".join(lines)

def generate_pdf_raw(text, output_folder):
    """
    Generate OCR-only PDF from raw text, saved in output_folder.
    Returns path to saved PDF.
    """
    output_path = os.path.join(output_folder, "ocr_notes.pdf")
    generate_pdf_from_markdown(text, output_path)
    return output_path

def generate_pdf_ai(text, output_folder):
    """
    Generate AI-refined PDF and OCR PDF, both saved in output_folder.
    Returns tuple (ocr_pdf_path, ai_pdf_path).
    Raises exception on AI failure.
    """
    refined_text = refine_notes_with_ai(text)
    ocr_pdf_path = os.path.join(output_folder, "ocr_notes.pdf")
    ai_pdf_path = os.path.join(output_folder, "ai_notes.pdf")

    generate_pdf_from_markdown(text, ocr_pdf_path)
    generate_pdf_from_markdown(refined_text, ai_pdf_path)

    return ocr_pdf_path, ai_pdf_path
