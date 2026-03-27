FROM python:3.12-slim AS base
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

FROM base AS dev
COPY . .
EXPOSE 8000
CMD ["sh", "-c", "alembic upgrade head && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"]

FROM base AS runner
COPY . .
EXPOSE 8000
CMD ["sh", "-c", "alembic upgrade head && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"]
