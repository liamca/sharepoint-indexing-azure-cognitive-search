import io
from typing import Optional

import PyPDF2

# load logging
from utils.ml_logging import get_logger

logger = get_logger()


def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> Optional[str]:
    """
    Extracts text from a PDF file provided as a bytes object.

    :param pdf_bytes: Bytes object containing the PDF file data.
    :return: Extracted text from the PDF as a string, or None if extraction fails.
    """
    try:
        with io.BytesIO(pdf_bytes) as pdf_stream:
            pdf_reader = PyPDF2.PdfReader(pdf_stream)
            text = []
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text.append(page.extract_text())

            extracted_text = "\n".join(text)
            logger.info("Text extraction from PDF bytes was successful.")
            return extracted_text
    except Exception as e:
        logger.error(f"An unexpected error occurred during PDF text extraction: {e}")

    return None
