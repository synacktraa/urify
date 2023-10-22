FROM python:3.10-slim-bookworm

WORKDIR /app/

RUN pip install urify

ENTRYPOINT ["urify"]

CMD []