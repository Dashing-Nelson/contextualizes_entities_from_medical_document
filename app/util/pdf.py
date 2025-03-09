import io

import pypdf

from app.util.log import logger
from app.util.middleware import get_request_id


def parse_pdf(file_bytes: bytes) -> str:
    try:
        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        text = ""
        # Iterate through each page of the PDF
        for page in reader.pages:
            # Extract text from the current page
            page_text = page.extract_text()
            # If text is found, append it to the result with a newline
            if page_text:
                text += page_text + "\n"
        return text
    except Exception as e:
        logger.error(
            "No content found",
            extra={
                "request_id": get_request_id(),
            },
        )
        raise ValueError("Failed to parse PDF file.") from e
