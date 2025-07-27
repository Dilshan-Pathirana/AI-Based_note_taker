import os
import re
import cv2
import pytesseract
from PIL import Image
import numpy as np

def natural_key(filename):
    """Sort filenames in human order, e.g. 1.jpg < 2.jpg < 10.jpg"""
    return [int(s) if s.isdigit() else s.lower() for s in re.split(r'(\d+)', filename)]

def preprocess_image(image_path):
    """Convert image to grayscale, denoise, and apply thresholding"""
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    denoised = cv2.fastNlMeansDenoising(gray, h=30)
    _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return thresh

def extract_text_from_image(img):
    config = r'--oem 3 --psm 6'
    return pytesseract.image_to_string(img, config=config)

def extract_text_preserve_all(folder_path):
    supported_exts = {".png", ".jpg", ".jpeg", ".bmp", ".tiff"}
    images = sorted(
        [f for f in os.listdir(folder_path) if f.lower().endswith(tuple(supported_exts))],
        key=natural_key
    )

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
