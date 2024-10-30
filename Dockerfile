FROM python:3.12-slim

RUN /usr/sbin/useradd --create-home --shell /bin/bash --user-group python

USER python
RUN /usr/local/bin/python -m venv /home/python/venv

COPY --chown=python:python requirements.txt /home/python/license-plate-bingo/requirements.txt
RUN /home/python/venv/bin/pip install --no-cache-dir --requirement /home/python/license-plate-bingo/requirements.txt

ENV PATH="/home/python/venv/bin:${PATH}" \
    PYTHONDONTWRITEBYTECODE="1" \
    PYTHONUNBUFFERED="1" \
    TZ="Etc/UTC"

ENTRYPOINT ["/home/python/venv/bin/python", "/home/python/license-plate-bingo/run.py"]

LABEL org.opencontainers.image.authors="William Jackson <william@subtlecoolness.com>" \
      org.opencontainers.image.source="https://github.com/williamjacksn/license-plate-bingo/"

COPY --chown=python:python run.py /home/python/license-plate-bingo/run.py
COPY --chown=python:python license_plate_bingo /home/python/license-plate-bingo/license_plate_bingo
