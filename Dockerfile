FROM python:3.9.6-alpine

WORKDIR /usr/src/app

ARG DEBUG
ARG POETRY_VERSION

# environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies
RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev libffi-dev openssl-dev cargo

# install dependencies
RUN pip install --upgrade pip
RUN pip install "poetry==$POETRY_VERSION"
COPY poetry.lock pyproject.toml ./
RUN poetry config virtualenvs.create false \
    && poetry install $(test "$DEBUG" == 1 && echo "--no-dev") --no-interaction --no-ansi

# Copy entire project
COPY . .

ENTRYPOINT ["/usr/src/app/entrypoint.sh"]