# `python-base` sets up all shared environment variables
FROM python:3.11-buster AS python-base

# python environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=2.1.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"

# prepend poetry and venv to path
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"


# `builder-base` stage to install dependencies
FROM python-base AS builder-base
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        curl \
        build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# install poetry
RUN curl -sSL https://install.python-poetry.org | python3 - --version $POETRY_VERSION

# copy project requirement files for caching
WORKDIR $PYSETUP_PATH
COPY poetry.lock pyproject.toml ./

# install runtime dependencies
RUN poetry install --without dev


# **New stage: `model-base` (Caches Hugging Face Model)**
FROM python-base AS model-base

ARG HUGGING_FACE_MODEL_PATH

COPY ./download_model.sh ./download_model.sh

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN ./download_model.sh $HUGGING_FACE_MODEL_PATH


# `development` image (used for local dev)
FROM python-base AS development
ENV FASTAPI_ENV=development
ENV STAGE=dev

WORKDIR $PYSETUP_PATH

# copy in our built poetry + venv
COPY --from=builder-base $POETRY_HOME $POETRY_HOME
COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH
COPY --from=model-base /models $PYSETUP_PATH/models

# install development dependencies
RUN poetry install --with=dev

# copy application code
COPY ./app $PYSETUP_PATH/app

EXPOSE 8000

CMD ["uvicorn", "--reload", "--port", "8000", "--host", "0.0.0.0", "app.main:app"]


# `production` image used for runtime
FROM python-base AS production

ENV FASTAPI_ENV=production
ENV STAGE=prod

COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH
COPY --from=model-base /models /models

COPY ./app /app/

EXPOSE 8000

# uses 2 workers per CPU as the task is CPU intensive.
CMD ["sh", "-c", "gunicorn -k uvicorn.workers.UvicornWorker -w $(( 2 * $(nproc) )) -b 0.0.0.0:8000 app.main:app"]