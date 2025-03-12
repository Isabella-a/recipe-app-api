FROM python:3.9-alpine3.13
LABEL maintainer="isabella24"

# Define que o Python não irá armazenar o buffer de saída (melhor para logs)
ENV PYTHONUNBUFFERED 1

# Copia os arquivos de dependências para a pasta temporária dentro do container
COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt

# Copia o código do aplicativo
COPY ./app /app
WORKDIR /app
EXPOSE 8000

# Define um argumento que pode ser passado no build
ARG DEV=false

# Instala o ambiente virtual e as dependências
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ "$DEV" = "true" ]; then \
      /py/bin/pip install -r /tmp/requirements.dev.txt; \
    fi && \
    rm -rf /tmp

# Adiciona um novo usuário para rodar o Django
RUN adduser \
        --disabled-password \
        --no-create-home \
        django-user

# Adiciona o ambiente virtual ao PATH
ENV PATH="/py/bin:$PATH"

# Define o usuário que rodará o container
USER django-user
