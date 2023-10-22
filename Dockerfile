FROM python:3.10-slim-bookworm

RUN pip install --no-cache-dir urify

ENTRYPOINT ["urify"]