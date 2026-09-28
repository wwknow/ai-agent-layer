FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir fastapi uvicorn httpx pydantic

COPY main.py /app/main.py
COPY support_api.py /app/support_api.py
COPY runtime.py /app/runtime.py

CMD ["uvicorn", "runtime:app", "--host", "0.0.0.0", "--port", "8088"]
