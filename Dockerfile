FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
COPY src/ src/
COPY data/ data/

RUN pip install --no-cache-dir .

EXPOSE 8000
EXPOSE 8501

CMD uvicorn src.api.main:app --host 0.0.0.0 --port 8000 & \
    streamlit run src/ui/app.py --server.address 0.0.0.0 --server.port 8501