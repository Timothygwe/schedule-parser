FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends curl build-essential && rm -rf /var/lib/apt/lists/*
RUN curl -sSL https://install.python-poetry.org | python3 -

ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

COPY pyproject.toml /app/
RUN poetry config virtualenvs.create false && poetry install

COPY . /app

EXPOSE 8000

CMD ["python", "main.py"]
