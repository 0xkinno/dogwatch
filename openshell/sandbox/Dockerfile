# Dogwatch sandbox image: Python venv, local OCR, and the Dogwatch core package. The vault is mounted read only at /vault.
FROM nvcr.io/nvidia/base/ubuntu:24.04
RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-venv curl ca-certificates tesseract-ocr \
 && rm -rf /var/lib/apt/lists/* \
 && (userdel -r ubuntu 2>/dev/null || true) && (groupdel ubuntu 2>/dev/null || true) && groupadd -g 1000 sandbox && useradd -m -u 1000 -g sandbox -s /bin/bash sandbox \
 && mkdir -p /sandbox /vault && chown -R 1000:1000 /sandbox
USER sandbox
WORKDIR /sandbox
RUN python3 -m venv .venv && .venv/bin/pip install --no-cache-dir openai httpx pydantic pyyaml python-dateutil pytesseract pillow
COPY --chown=1000:1000 core /sandbox/core
ENV PYTHONPATH=/sandbox/core PATH=/sandbox/.venv/bin:$PATH
