# Add new cog

- main.py
    - import cog
    - add line `await self.add_cog(<NEW_COG>(self))` in `on_ready` function

- create new directory in /data
- config.py
    - `<NEW_COG> = os.path.join(ROOT_DIR, "data/<NEW_DIR>")`

# How to run

## Docker compose

```yml
services:
  bot:
    image: desipeli/discord-bot:latest
    environment:
      - DISCORD_TOKEN=<YOUR_DISCORD_TOKEN>
      - GPT_TOKEN=<YOUR_OPENAI_TOKEN>
    volumes:
      - data:/app/data
    restart: on-failure:5
    
volumes:
  data:
```