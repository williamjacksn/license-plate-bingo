FROM ghcr.io/astral-sh/uv:0.9.4-trixie-slim

RUN /usr/sbin/useradd --create-home --shell /bin/bash --user-group python
USER python


WORKDIR /app
COPY --chown=python:python .python-version pyproject.toml uv.lock ./
RUN uv sync --frozen

ENV PATH="/app/.venv/bin:${PATH}" \
    PYTHONDONTWRITEBYTECODE="1" \
    PYTHONUNBUFFERED="1" \
    TZ="Etc/UTC"

ENTRYPOINT ["uv", "run", "run.py"]

LABEL org.opencontainers.image.authors="William Jackson <william@subtlecoolness.com>" \
      org.opencontainers.image.source="https://github.com/williamjacksn/license-plate-bingo/"

COPY --chown=python:python run.py ./
COPY --chown=python:python license_plate_bingo ./license_plate_bingo
