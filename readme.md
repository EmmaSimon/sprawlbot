# sprawlbot

A Discord bot to help with playing [The Sprawl](https://www.drivethrurpg.com/product/171286/) by Hamish Cameron.

## Usage

You can use the bot to search for tags, moves, and cyberwear.

Searching uses [fuzzy string matching](https://github.com/seatgeek/fuzzywuzzy), so don't worry about being too exact.

`!tag high cap`

`!move mix`

`!cyber legs`

### Rolls

The bot can also roll moves.

`!roll pressure +1`

Only the results relevant to the roll will be displayed (ie. if the roll is an 11, 7+ and 10+ are shown, but not 7-9).


## Setup

The bot only works with python 3.5+. It's been tested on Debian and Windows 10, but it should work on most OSes.

It requires [discord.py](https://github.com/Rapptz/discord.py) and [FuzzyWuzzy](https://github.com/seatgeek/fuzzywuzzy).

To install:
```
pip3 install discord.py fuzzywuzzy[speedup]
```

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
