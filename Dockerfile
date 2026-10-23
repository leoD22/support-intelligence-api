FROM python:3.10-slim
WORKDIR /workspace
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app/ ./app
RUN useradd -m apiuser
USER apiuser
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]