FROM python:3.12-alpine

LABEL maintainer="isabella24"

ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY ./requirements.txt ./requirements.txt
COPY ./requirements.dev.txt ./requirements.dev.txt
COPY ./app /app

RUN apk add --no-cache gcc musl-dev libffi-dev && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

ARG DEV=false

RUN if [ "$DEV" = "true" ]; then \
      pip install --no-cache-dir -r requirements.dev.txt && \
      pip install --upgrade importlib-metadata; \
    fi

RUN adduser --disabled-password --no-create-home django-user

USER django-user

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
