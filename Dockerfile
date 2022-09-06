# Base container image used for both build and runtime
FROM python:3.9-slim AS base

SHELL ["/bin/bash", "-c"]

# Update packages
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get upgrade -y \
    && apt-get clean \
    && python -m pip install --upgrade pip

# Container image used to build the project
FROM base as builder

# Disable pip version check and cache, set poetry version
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VERSION=1.2.0

# Build code using poetry
RUN apt-get install -y --no-install-recommends gcc
RUN pip install "poetry==$POETRY_VERSION"
RUN python -m venv /venv
# Install wheel into virtual environment to make it easy to copy
COPY . .
RUN poetry build && /venv/bin/pip install dist/*.whl

# Container image used at runtime
FROM base as final

# Need jq at runtime
RUN apt-get install -y --no-install-recommends jq \
    && apt-get clean
# Copy virtual environment with software installed
COPY --from=builder /venv /venv
ENV PATH="/venv/bin:${PATH}" \
    VIRTUAL_ENV="/venv"
COPY entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
