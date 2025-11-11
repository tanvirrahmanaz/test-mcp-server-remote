FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install only the runtime dependencies that main.py needs.
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir \
        "fastmcp>=2.13.0.2" \
        "aiosqlite>=0.21.0"

COPY main.py categories.json ./

# The MCP server starts as soon as the container runs.
CMD ["python", "main.py"]
