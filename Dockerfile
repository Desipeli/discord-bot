FROM --platform=$TARGETPLATFORM python:3.10.12-alpine

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt && \
    adduser -D appuser

CMD ["python3", "main.py"]