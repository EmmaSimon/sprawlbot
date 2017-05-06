# sprawlbot

A Discord bot to help with playing [The Sprawl](https://www.drivethrurpg.com/product/171286/) by Hamish Cameron.

## Usage

You can currently use the bot to search for tags and moves.

Searching uses [fuzzy string matching](https://github.com/seatgeek/fuzzywuzzy), so don't worry about being too exact.

`!tag high cap`

`!move act`


## Setup

Clone this repo to a directory on your server:

```
git clone git@github.com:EmmaSimon/sprawlbot.git
```

Run `sprawlbot.py`

```
python3 sprawlbot.py
```

To use the bot, you'll need a bot token from <https://discordapp.com/developers/applications/me>. Create a new application, then in that application, create a bot user. The token you'll need is underneath the bot's username.

The first time you run the script, it will ask you for your token and preferred command prefix (defaults to !), and save them into config.json.

You can also edit config.json directly, or you can run the script with the token and prefix arguments.

```
python3 sprawlbot.py --token <token> --prefix #
```

If the bot connects successfully to Discord, it will give you a link that you can use to invite the bot to your server. Once it's been invited once, and the server is online, it will respond to any commands that it hears.

### systemd

There's a `sprawlbot.service` file for setting up the bot as a service. Edit it to include your username and install path, then do the following:
```
sudo cp sprawlbot.service /etc/systemd/system/
sudo systemctl enable sprawlbot
sudo systemctl start sprawlbot
```
