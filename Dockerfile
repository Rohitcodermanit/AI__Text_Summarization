FROM python:3.10-slim

WORKDIR /app

# System dependencies for unstructured, faiss, pymupdf, bs4, etc.
RUN apt-get update && apt-get install -y \
    build-essential \
    poppler-utils \
    libglib2.0-0 \
    libgl1 \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

EXPOSE 7860

CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
