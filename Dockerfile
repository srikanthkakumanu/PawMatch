FROM python:3.15-slim AS build
ENV UV_PYTHON_DOWNLOADS=never
RUN pip install --no-cache-dir uv==0.13.9
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

FROM python:3.15-slim
RUN useradd --system --uid 10001 --no-create-home pawmatch
WORKDIR /app
COPY --from=build /app/.venv ./.venv
COPY pawmatch ./pawmatch
ENV PATH="/app/.venv/bin:$PATH" PYTHONUNBUFFERED=1
USER pawmatch
CMD ["sh", "-c", "exec uvicorn pawmatch.main:app --host 0.0.0.0 --port \"$PORT\""]
