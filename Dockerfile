FROM python:3.10-slim-bookworm

RUN pip install urify

ENTRYPOINT ["urify"]

CMD []