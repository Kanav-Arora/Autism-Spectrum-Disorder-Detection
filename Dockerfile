FROM python:3.10-slim

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=1.2.2

# System deps:
RUN pip install "poetry==$POETRY_VERSION"

# Copy only requirements to cache them in docker layer
WORKDIR /code
COPY poetry.lock pyproject.toml /code/

# Project initialization:
RUN poetry config virtualenvs.create false \
  && poetry install --no-root --no-interaction --no-cache --no-ansi --only main

# Creating folders, and files for a project:
COPY . /code

ENTRYPOINT streamlit run Main.py --server.port=80 --server.address=0.0.0.0
