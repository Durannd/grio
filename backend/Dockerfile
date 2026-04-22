FROM python:3.11
WORKDIR /app
COPY backend/requirements.txt .
RUN apt-get update && apt-get install -y libpq-dev && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PYTHONPATH=/usr/local/lib/python3.11/site-packages:/app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
