import os
import pymupdf


def read_pdf(file_path: str) -> str:
    """
    Extracts text from a PDF file using PyMuPDF (fitz).

    Args:
        file_path (str): The path to the PDF file.

    Returns:
        str: The extracted text across all pages, preserving page boundaries.

    Raises:
        FileNotFoundError: If the file does not exist at the specified path.
        RuntimeError: If PyMuPDF encounters an error opening or processing the file.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF file not found: {file_path}")

    try:
        doc = pymupdf.open(file_path)
    except Exception as exc:
        raise RuntimeError(f"Failed to open PDF document '{file_path}': {exc}") from exc

    page_texts = []
    try:
        total_pages = len(doc)
        for page_num in range(total_pages):
            page = doc[page_num]
            text = page.get_text()
            # Mark page boundaries cleanly
            page_banner = f"--- PAGE {page_num + 1} OF {total_pages} ---"
            page_texts.append(f"{page_banner}\n{text}")
    except Exception as exc:
        raise RuntimeError(f"Error while reading pages from '{file_path}': {exc}") from exc
    finally:
        doc.close()

    return "\n\n".join(page_texts)
