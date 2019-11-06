docker build -t baked-beans-bot .
docker run --env-file env.list -d baked-beans-bot
