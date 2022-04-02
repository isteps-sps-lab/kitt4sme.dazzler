FROM python:3.8

RUN pip install poetry
RUN mkdir /app
WORKDIR /app

COPY poetry.lock pyproject.toml /app/
RUN poetry config virtualenvs.create false \
  && poetry install --no-dev --no-interaction --no-ansi

COPY dazzler /app/dazzler

ENV PYTHONPATH=$PWD:$PYTHONPATH

EXPOSE 8000

ENTRYPOINT ["uvicorn", "dazzler.main:app", \
            "--host", "0.0.0.0", "--port", "8000"]
