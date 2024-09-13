FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python3 -

ENV PATH="/root/.local/bin:$PATH"

RUN pip install --upgrade pip setuptools

WORKDIR /src

COPY pyproject.toml poetry.lock* ./

RUN poetry install --no-dev --no-interaction --no-ansi

COPY . .

RUN chmod +x /src/entrypoint.sh

EXPOSE 8000

# ENTRYPOINT ["poetry", "run"]
