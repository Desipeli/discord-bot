# Add new cog

- main.py
    - import cog
    - add line `await self.add_cog(<NEW_COG>(self))` in `on_ready` function

- create new directory in /data
- config.py
    - `<NEW_COG> = os.path.join(ROOT_DIR, "data/<NEW_DIR>")`