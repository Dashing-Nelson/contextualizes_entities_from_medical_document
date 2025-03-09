import io
from unittest.mock import MagicMock, patch

import pypdf
import pytest

from app.util.pdf import parse_pdf


def test_parse_pdf_valid():
    # Create a mock PDF file with text
    pdf_writer = pypdf.PdfWriter()
    blank_page = pypdf.PageObject.create_blank_page(width=200, height=200)
    pdf_writer.add_page(blank_page)

    with io.BytesIO() as pdf_buffer:
        pdf_writer.write(pdf_buffer)
        pdf_buffer.seek(0)
        pdf_bytes = pdf_buffer.getvalue()

    # Mock PdfReader
    with patch("pypdf.PdfReader") as MockPdfReader:
        mock_reader = MockPdfReader.return_value
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Mock PDF Text"
        mock_reader.pages = [mock_page]

        text = parse_pdf(pdf_bytes)

    assert text.strip() == "Mock PDF Text"


def test_parse_pdf_empty():
    # Create an empty PDF
    pdf_writer = pypdf.PdfWriter()
    with io.BytesIO() as pdf_buffer:
        pdf_writer.write(pdf_buffer)
        pdf_buffer.seek(0)
        pdf_bytes = pdf_buffer.getvalue()

    with patch("pypdf.PdfReader") as MockPdfReader:
        mock_reader = MockPdfReader.return_value
        mock_reader.pages = []

        text = parse_pdf(pdf_bytes)

    assert text == ""


def test_parse_pdf_invalid():
    invalid_bytes = b"Not a real PDF file"

    with pytest.raises(ValueError, match="Failed to parse PDF file."):
        parse_pdf(invalid_bytes)
