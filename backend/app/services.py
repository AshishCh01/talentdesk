import pdfplumber
import io

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extracts text from a PDF file, including hidden/invisible text.
    pdfplumber is great for this because it reads the raw text objects
    regardless of color (e.g. white text) or size (e.g. 1pt font).
    """
    text_content = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_content.append(page_text)
                
    return "\n".join(text_content)
