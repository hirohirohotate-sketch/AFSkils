FROM python:3.12-slim

WORKDIR /app

ENV POETRY_VERSION=1.7.0 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

RUN pip install --no-cache-dir "poetry==${POETRY_VERSION}"

COPY pyproject.toml ./
RUN poetry install --only main --no-root

COPY . .

CMD ["poetry", "run", "dmm-affiliate", "generate-candidates", "--source", "data/products.csv", "--limit", "5"]
