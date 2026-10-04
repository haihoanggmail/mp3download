FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends curl unzip ca-certificates \
    && rm -rf /var/lib/apt/lists/*
# deno: runtime JavaScript mà yt-dlp cần để giải mã YouTube
ENV DENO_INSTALL=/usr/local
RUN curl -fsSL https://deno.land/install.sh | sh
WORKDIR /app
RUN pip install --no-cache-dir -U "yt-dlp[default]"
COPY server.py index.html ./
ENV HOST=0.0.0.0
CMD ["python", "server.py"]
