import logging

from fastapi import FastAPI

from app.api.router import api_router
from app.util.config import Stage, stage
from app.util.log import set_log_level
from app.util.middleware import add_request_id

app = FastAPI(
    title="Medical Entity Extraction API",
    version="1.0.0",
    description="This API allows users to extract medically relevant entities from PDF documents using a pre-trained "
    "NER model.",
)

LOG_LEVEL = logging.INFO if stage == Stage.PROD else logging.DEBUG

set_log_level(LOG_LEVEL)

# Middleware
app.middleware("http")(add_request_id)

# Routers
app.include_router(api_router)
