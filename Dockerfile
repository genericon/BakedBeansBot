FROM python:3-slim

# Set pip to have cleaner logs and no saved cache
ENV PIP_NO_CACHE_DIR=false \
    PIPENV_HIDE_EMOJIS=1 \
    PIPENV_IGNORE_VIRTUALENVS=1 \
    PIPENV_NOSPIN=1

# Install git
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install pipenv
RUN pip install -U pipenv

WORKDIR /bot

# Copy Pipfiles
COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock

# Install project dependencies
RUN pipenv install --system --deploy

# Install wait-for-it
RUN apt-get update && apt-get install -y \
    wait-for-it \
    && rm -rf /var/lib/apt/lists/*

# Copy project files into working directory
COPY . .

CMD [ "python", "./main.py" ]
