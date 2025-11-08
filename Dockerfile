FROM python:3.10-slim

WORKDIR /app
RUN printf "nameserver 8.8.8.8\nnameserver 1.1.1.1\n" > /etc/resolv.conf

# System dependencies for unstructured, faiss, pymupdf, bs4, etc.
RUN apt-get update && apt-get install -y \
    build-essential \
    poppler-utils \
    libglib2.0-0 \
    git \
    ffmpeg \
    libgl1 \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_PORT=7860
ENV STREAMLIT_SERVER_ENABLECORS=false
ENV STREAMLIT_SERVER_ENABLEXsrfProtection=false

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

EXPOSE 7860

CMD ["streamlit", "run", "main.py", "--server.port=7860", "--server.address=0.0.0.0"]
