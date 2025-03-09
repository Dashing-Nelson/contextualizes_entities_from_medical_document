import time
import uuid
from contextvars import ContextVar

from fastapi import Request

from app.util.log import logger

# Create a context variable to store the request_id per request
request_id_ctx = ContextVar("request_id", default="N/A")


async def add_request_id(request: Request, call_next):
    # usually load balancers add the request_id. For local, we would generate on our own.
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request_id_ctx.set(request_id)
    logger.info("Processing request", extra={"request_id": request_id})
    start_time = time.time()
    response = await call_next(request)
    end_time = time.time()
    total_time_in_seconds = end_time - start_time
    logger.info(
        "Request finished",
        extra={
            "request_id": request_id,
            "total_time_in_seconds": total_time_in_seconds,
        },
    )
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Total-Time-In-Seconds"] = str(total_time_in_seconds)
    return response


def get_request_id():
    return request_id_ctx.get()
