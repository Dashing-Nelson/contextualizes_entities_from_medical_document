from pydantic import BaseModel, Field


class BadRequestError(BaseModel):
    detail: str = Field(
        ...,
        description="Bad request, file not included or empty filename.",
        example="No file uploaded or empty filename.",
    )


class UnsupportedMediaTypeError(BaseModel):
    detail: str = Field(
        ...,
        description="Unsupported file type. Please upload a PDF file.",
        example="Unsupported file type. Please upload a PDF file.",
    )


class ServerError(BaseModel):
    detail: str = Field(
        ...,
        description="Server error during entity extraction.",
        example="Server error during entity extraction.",
    )
