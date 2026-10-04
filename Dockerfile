FROM python:3.12-slim
WORKDIR /app
RUN pip install --no-cache-dir -U yt-dlp
COPY server.py index.html ./
ENV HOST=0.0.0.0
CMD ["python", "server.py"]
