FROM python:3.12-alpine

LABEL maintainer="isabella24"

ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Copia apenas os arquivos de dependências para aproveitar cache do Docker
COPY ./requirements.txt ./requirements.txt
COPY ./requirements.dev.txt ./requirements.dev.txt

# Instala dependências do sistema
RUN apk add --no-cache \
    gcc musl-dev libffi-dev \
    postgresql-client \
    && apk add --no-cache postgresql-client jpeg-dev \
    && apk add --no-cache --virtual .tmp-build-deps \
    build-base postgresql-dev musl-dev zlib zlib-dev \
    && pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && apk del .tmp-build-deps  # Remove dependências temporárias após a instalação

# Copia o restante do código da aplicação
COPY ./app /app

# Define se é ambiente de desenvolvimento e instala dependências extras
ARG DEV=false
RUN if [ "$DEV" = "true" ]; then \
      pip install --no-cache-dir -r requirements.dev.txt && \
      pip install --upgrade flake8 "importlib-metadata>=6.0.0"; \
    fi

# Criação do usuário não-root para segurança
RUN adduser --disabled-password --no-create-home django-user \
    && mkdir -p /vol/web/media \
    && mkdir -p /vol/web/static \
    && chown -R django-user:django-user /vol \
    && chmod -R 755 /vol

USER django-user

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
