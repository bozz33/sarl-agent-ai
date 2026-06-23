FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    SARL_MEMORY_MCP_TRANSPORT=streamable-http \
    SARL_MEMORY_MCP_HOST=0.0.0.0 \
    SARL_MEMORY_MCP_PORT=8000

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src

RUN pip install --no-cache-dir .

USER 10010:10010

EXPOSE 8000

CMD ["python", "-m", "sarl_project_memory_mcp.server"]
