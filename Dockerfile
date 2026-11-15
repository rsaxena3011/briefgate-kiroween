# BriefGate — multi-stage: build the React frontend, then ship one Python
# service (FastAPI serves the API + the built bundle + evidence frames).
# Run: docker build -t briefgate . && docker run -p 8000:8000 briefgate
FROM node:20-slim AS frontend
WORKDIR /build
COPY app/frontend/package.json app/frontend/package-lock.json* ./frontend/
RUN cd frontend && npm install --no-audit --no-fund
COPY app/frontend ./frontend
RUN cd frontend && npm run build

FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
COPY mcp-server ./mcp-server
COPY sample-pack ./sample-pack
COPY scripts ./scripts
COPY --from=frontend /build/frontend/dist ./app/frontend/dist
ENV PORT=8000
EXPOSE 8000
CMD ["sh", "-c", "uvicorn app.backend.main:app --host 0.0.0.0 --port ${PORT}"]
