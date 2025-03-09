from pydantic import BaseModel, Field

from app.schema.error.response_model import (
    BadRequestError,
    ServerError,
    UnsupportedMediaTypeError,
)


class ExtractResponse(BaseModel):
    entity: str = Field(
        ..., description="The identified medical entity.", example="CCR5"
    )
    context: str = Field(
        ...,
        description=(
            "Context where the entity was found, including text surrounding the entity for clarity. "
            "For example: '... uses on the relief of symptoms rather than on a biological ‘cure’. have identified rare "
            "mutations in CCR5 that confer resilience against ...'"
        ),
        example="... uses on the relief of symptoms rather than on a biological ‘cure’. have identified rare mutations "
        "in CCR5 that confer resilience against ...",
    )
    start: int = Field(
        ...,
        description="The start position of the entity in the context with respect to the original text.",
        example=25,
    )
    end: int = Field(
        ...,
        description="The end position of the entity in the context with respect to the original text.",
        example=34,
    )


error_response = {
    400: {
        "model": BadRequestError,
        "description": "Bad request, file not included or empty filename.",
    },
    415: {
        "model": UnsupportedMediaTypeError,
        "description": "Unsupported file type.",
    },
    500: {
        "model": ServerError,
        "description": "Server error during entity extraction.",
    },
}
