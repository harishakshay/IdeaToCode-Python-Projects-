	import os
import sys
from typing import List

try:
    import fitz  # PyMuPDF
except ImportError:
    sys.exit('PyMuPDF (fitz) is required. Install with: pip install pymupdf')

try:
    from reportlab.pdfgen import canvas
except ImportError:
    sys.exit('ReportLab is required to generate a sample PDF. Install with: pip install reportlab')


def create_sample_pdf(path: str) -> None:
    """Create a minimal PDF with some example text for demonstration purposes."""
    c = canvas.Canvas(path)
    text = (
        "Artificial intelligence and natural language processing are transforming industries.\n"
        "Python is a versatile language for data science, web development, and automation.\n"
        "Highlighting keywords in PDFs can improve readability and information extraction."
    )
    text_obj = c.beginText(40, 800)
    for line in text.split('\n'):
        text_obj.textLine(line)
    c.drawText(text_obj)
    c.showPage()
    c.save()


def highlight_keywords(input_pdf: str, output_pdf: str, keywords: List[str]) -> None:
    """Add highlight annotations for each occurrence of the given keywords.

    Args:
        input_pdf: Path to the source PDF.
        output_pdf: Path where the highlighted PDF will be saved.
        keywords: List of words or phrases to highlight.
    """
    doc = fitz.open(input_pdf)
    for page_num in range(len(doc)):
        page = doc[page_num]
        for kw in keywords:
            # search_for returns a list of rectangles where the text is found
            rects = page.search_for(kw, hit_max=0)
            for rect in rects:
                # add a highlight annotation with a semi‑transparent yellow color
                annot = page.add_highlight_annot(rect)
                annot.set_colors(stroke=(1, 1, 0))  # RGB yellow
                annot.update()
    doc.save(output_pdf, garbage=4, deflate=True)
    doc.close()


def main() -> None:
    sample_path = "sample.pdf"
    highlighted_path = "sample_highlighted.pdf"
    # Create a sample PDF if it does not exist
    if not os.path.exists(sample_path):
        create_sample_pdf(sample_path)
        print(f"Created sample PDF: {sample_path}")
    # Define keywords/phrases to highlight
    keywords = [
        "Artificial intelligence",
        "Python",
        "highlighting",
        "data science",
    ]
    highlight_keywords(sample_path, highlighted_path, keywords)
    print(f"Highlights added. Output saved to: {highlighted_path}")

if __name__ == "__main__":
    main()
}