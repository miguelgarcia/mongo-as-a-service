FROM python:3.12-slim AS base
FROM base AS builder

COPY --from=ghcr.io/astral-sh/uv:0.4.9 /uv /bin/uv
WORKDIR /app
COPY uv.lock pyproject.toml /app/
RUN --mount=type=cache,target=/root/.cache/uv \
  uv sync --frozen --no-install-project --no-dev
COPY src/ /app
RUN --mount=type=cache,target=/root/.cache/uv \
  uv sync --frozen --no-dev

FROM base
COPY --from=builder /app /app
ENV PATH="/app/.venv/bin:$PATH"
ENTRYPOINT ["uv", "run", "poe", "run"]
