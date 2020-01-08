FROM python:3-slim

# Set pip to have cleaner logs and no saved cache
ENV PIP_NO_CACHE_DIR=false \
    PIPENV_HIDE_EMOJIS=1 \
    PIPENV_IGNORE_VIRTUALENVS=1 \
    PIPENV_NOSPIN=1

# Install pipenv
RUN pip install -U pipenv

# Copy project files into working directory
WORKDIR /bot
COPY . .

# Install project dependencies
RUN pipenv install --system --deploy

# Install wait-for-it
RUN apt-get update && apt-get install -y \
    wait-for-it \
    && rm -rf /var/lib/apt/lists/*

CMD [ "python", "./main.py" ]
