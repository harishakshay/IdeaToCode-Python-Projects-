	import sys
import os
from pathlib import Path
from typing import Optional

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    raise ImportError("Pillow is required. Install with 'pip install pillow'.")

try:
    import pytesseract
except ImportError:
    raise ImportError("pytesseract is required. Install with 'pip install pytesseract'.")


def extract_text(image_path: str) -> str:
    """Run OCR on the given image and return extracted text."""
    if not Path(image_path).is_file():
        raise FileNotFoundError(f"Image file not found: {image_path}")
    img = Image.open(image_path)
    # pytesseract may require tesseract binary in PATH; let it raise if unavailable
    text = pytesseract.image_to_string(img)
    return text.strip()


def generate_commit_message(extracted_text: str) -> str:
    """Create a concise commit message from OCR text.
    Simple heuristic: use the first non‑empty line, capitalize, and prefix.
    """
    if not extracted_text:
        return "Update: No recognizable text found"
    # Take first non‑empty line
    for line in extracted_text.splitlines():
        line = line.strip()
        if line:
            # Ensure the line ends without a period for consistency
            line = line.rstrip('.').strip()
            return f"Update: {line}"  # Basic prefix
    return "Update: (empty OCR result)"


def create_sample_image(path: str, text: str = "Fixed bug in login flow") -> None:
    """Generate a minimal PNG with the provided text for demo purposes."""
    # Create a white image
    img = Image.new('RGB', (400, 100), color='white')
    d = ImageDraw.Draw(img)
    try:
        # Try a common TrueType font; fallback to default if unavailable
        font = ImageFont.truetype('arial.ttf', 20)
    except Exception:
        font = ImageFont.load_default()
    # Center the text
    text_width, text_height = d.textsize(text, font=font)
    x = (img.width - text_width) / 2
    y = (img.height - text_height) / 2
    d.text((x, y), text, fill='black', font=font)
    img.save(path)
    print(f"Sample image created at {path}")


def main() -> None:
    """Entry point: extract text from an image and produce a commit message.
    Usage: python ImageToTextExtractor.py <image_path>
    If no argument is supplied, a sample image is generated and used.
    """
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        # Create and use a sample image in the current directory
        image_path = "sample_image.png"
        if not Path(image_path).exists():
            create_sample_image(image_path)
    try:
        text = extract_text(image_path)
        print("--- OCR Extracted Text ---")
        print(text if text else "[No text detected]")
        commit_msg = generate_commit_message(text)
        print("--- Generated Commit Message ---")
        print(commit_msg)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
}