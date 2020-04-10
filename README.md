# Taribot #

Simple bot that spews pictures from the predetermined location.

## Configuration ##

Create a new file called `config.json` in the root directory. Copy the following json into that file (or just the parts that you care about).

```json
{
    "bot": true, // If the connection is made with a bot or normal user
    "token": "bottoken", // Token used to authenticate the bot
    "prefix": ";", // Prefix used to call the bot commands in discord
    "print_messages": false, // Print incoming (discord) messages to console/stdout
    "database": {
        "enabled": false,
        "database": "taribot.db" // Sqlite database name
    },
    "modules": {
        "Kitty": {
            "enabled": false,
            "keyword": "cat",
            "location": "/srv/taribot", // Location where the bot should find images to upload on the local filesystem
            "max_images": 5,
            "gfycat": {
                "enabled": false,
                "keyword": "catvid",
                "album_id": "",
                "token_data": {
                    "client_id": "",
                    "client_secret": "",
                    "username": "",
                    "password": "",
                    "grant_type": "password" // Only supports password right now
                }
            }
        },
        "Scheduler": {
            "enabled": false,
            "keyword": "schedule",
            "remove_keyword": "unschedule"
        }
    }
}
```

## Running the bot ##

### Docker ###

Copy `.env-dist` as just `.env`. And fill in the empty fields in there.

After configuring the bot, you just have to run `docker-compose up` and everything else gets installed/ran automatically.

### Poetry ###

If docker isn't your thing, another solution is to install [poetry](https://python-poetry.org/).

After installing poetry, run `poetry install` to install the required dependencies, then `poetry run python main.py` to run the bot.
