from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from app.schema.api.v1.response_model import ExtractResponse, error_response
from app.util.auth import http_basic_auth
from app.util.log import logger
from app.util.middleware import get_request_id
from app.util.pdf import parse_pdf
from app.util.text_context import extract_entities

router = APIRouter(prefix="/v1")


@router.post(
    "/extract",
    summary="Extract medical entities from a PDF document.",
    response_model=ExtractResponse,
    responses=error_response,
)
async def extract_from_pdf(
    username: Annotated[str, Depends(http_basic_auth)],
    content: UploadFile = File(description="PDF file to be processed"),
):
    logger.info(
        "API accessed", extra={"request_id": get_request_id(), "username": username}
    )
    if not content:
        logger.error(
            "No content found",
            extra={"request_id": get_request_id(), "username": username},
        )
        raise HTTPException(status_code=400, detail="No file uploaded.")
    if content.content_type != "application/pdf":
        logger.error(
            "Unsupported content type",
            extra={"request_id": get_request_id(), "username": username},
        )
        raise HTTPException(status_code=415, detail="Unsupported file type.")
    if content.filename == "":
        logger.error(
            "No filename found",
            extra={"request_id": get_request_id(), "username": username},
        )
        raise HTTPException(
            status_code=400, detail="Bad request, file not included or empty filename."
        )
    try:
        logger.info(
            "Processing file",
            extra={
                "request_id": get_request_id(),
                "username": username,
                "content": content.filename,
            },
        )
        file_bytes = await content.read()
        if not file_bytes:
            logger.error(
                "No content found",
                extra={"request_id": get_request_id(), username: username},
            )
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")
        text = parse_pdf(file_bytes)
        if not text.strip():
            raise HTTPException(
                status_code=400, detail="No extractable text found in the PDF."
            )
        entities = extract_entities(text)
        return JSONResponse(content=entities, status_code=200)
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.exception("Unexpected error during processing.")
        raise HTTPException(status_code=500, detail="Server error") from e
