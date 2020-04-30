# BakedBeansBot

BakedBeansBot is a Discord bot built for the RSFA / Genericon Server.
The bot was initially designed to provide club management services for RSFA via Discord.
We are looking into extending the bot to provide multi-club (and multi-server) management.

## Requirements

- [Python 3.8](https://www.python.org/downloads/)
- Pipenv
    - `pip install pipenv`
- [PostgreSQL](https://www.postgresql.org/)

### Using Docker

Using Docker is generally recommended (but not stricly required) because it abstracts away some additional set up work.

The requirements for Docker are:

- [Docker CE](https://docs.docker.com/install/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Run the project

TODO

### Run with Docker

```
docker-compose up
docker-compose up --no-deps bot
```

### Run on the host

```
pipenv run start
```

# Notes

The setup of the PostgreSQL database is very hard to replicate at this time.
We're planning to migrate to [Tortoise ORM](https://tortoise.github.io/) to simplify this.
