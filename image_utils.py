import os
import re
import cv2
import pytesseract
from PIL import Image
import numpy as np

# Optional: specify tesseract path (uncomment if needed)
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def natural_key(filename):
    """Sort filenames in human order, e.g. 1.jpg < 2.jpg < 10.jpg"""
    return [int(s) if s.isdigit() else s.lower() for s in re.split(r'(\d+)', filename)]

def preprocess_image(image_path):
    """Convert image to grayscale, denoise, and apply thresholding"""
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Could not read image: {image_path}")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    denoised = cv2.fastNlMeansDenoising(gray, h=30)
    _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return thresh

def extract_text_from_image(img):
    """Extract text from an OpenCV image using Tesseract"""
    config = r'--oem 3 --psm 6'
    return pytesseract.image_to_string(img, config=config)

def extract_text_preserve_all(folder_path):
    """OCR all images in a folder, preserving all text lines and order"""
    supported_exts = {".png", ".jpg", ".jpeg", ".bmp", ".tiff"}
    try:
        filenames = os.listdir(folder_path)
    except FileNotFoundError:
        print(f"[ERROR] Folder not found: {folder_path}")
        return []

    images = sorted(
        [f for f in filenames if os.path.splitext(f)[1].lower() in supported_exts],
        key=natural_key
    )

    if not images:
        print(f"[WARNING] No image files found in: {folder_path}")
        return []

    print(f"[DEBUG] Found {len(images)} images in folder '{folder_path}': {images}")

    final_lines = []
    for filename in images:
        image_path = os.path.join(folder_path, filename)
        try:
            img_cv = preprocess_image(image_path)
            text = extract_text_from_image(img_cv)
        except Exception as e:
            print(f"[WARNING] Failed to process {filename}: {e}")
            continue

        print(f"[INFO] Processed image: {filename}")
        lines = [line.strip() for line in text.splitlines()]
        final_lines.extend(lines)
        final_lines.append("")  # blank line after each image

    return final_lines
