from pypdf import PdfReader


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text from a PDF file.

    Args:
        pdf_path (str): Path to the PDF file

    Returns:
        str: Extracted text from the PDF
    """

    text = ""

    try:
        reader = PdfReader(pdf_path)

        for page in reader.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

    except Exception as e:
        print(f"[ERROR] Failed to read PDF: {e}")

    return text


def extract_first_pages(pdf_path: str, max_pages: int = 5) -> str:
    """
    Extract text only from first few pages (faster for AI processing).
    """

    text = ""

    try:
        reader = PdfReader(pdf_path)

        pages = reader.pages[:max_pages]

        for page in pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

    except Exception as e:
        print(f"[ERROR] Failed to extract pages: {e}")

    return text


def count_pages(pdf_path: str) -> int:
    """
    Count number of pages in PDF.
    """

    try:
        reader = PdfReader(pdf_path)
        return len(reader.pages)

    except Exception:
        return 0


if __name__ == "__main__":

    sample_pdf = "data/sample.pdf"

    print("Reading PDF...\n")

    text = extract_first_pages(sample_pdf)

    print(text[:1000])  # print first 1000 characters