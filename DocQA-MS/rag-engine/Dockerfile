FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY DocQA-MS/rag-engine/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY DocQA-MS/rag-engine/src/ ./src/
COPY DocQA-MS/rag-engine/init_faiss.py .
COPY DocQA-MS-Backend/database ./database

ENV PYTHONPATH=/app/src:/app:/app/database:$PYTHONPATH

EXPOSE 8004

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8004"]
