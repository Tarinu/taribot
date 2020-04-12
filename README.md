# Taribot #

Simple bot that spews pictures from the predetermined location.

## Configuration ##

Copy `config-dist.py` as `config.py` and make sure it has `config` variable in there.  
More info about the configuration is written there

## Running the bot ##

### Docker ###

Copy `.env-dist` as just `.env`. And fill in the empty fields in there.

After configuring the bot, you just have to run `docker-compose up` and everything else gets installed/ran automatically.

### Poetry ###

If docker isn't your thing, another solution is to install [poetry](https://python-poetry.org/).

After installing poetry, run `poetry install` to install the required dependencies, then `poetry run python main.py` to run the bot.
