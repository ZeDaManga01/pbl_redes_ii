FROM python:3.12.5-slim
ENV POETRY_VIRTUALENVS_CREATE=false


WORKDIR /app
COPY . . 

RUN pip install poetry

RUN poetry install --no-interaction --no-ansi

EXPOSE 8004
CMD poetry run fastapi dev server_a.py --host 0.0.0.0 --port 8004
