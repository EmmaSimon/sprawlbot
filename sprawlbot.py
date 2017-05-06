#!/usr/bin/python3
import argparse
import json
import os
import sys

import discord
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

client = discord.Client()


@client.event
async def on_ready():
    print('Started successfully.')
    url = discord.utils.oauth_url(client.user.id)
    client.oauth_url = url
    print('Use this link to invite {} to a server:\n{}'.format(
        client.user.name, url
    ))


@client.event
async def on_message(message):
    message_text = message.content
    if not message_text.startswith(config.prefix):
        return

    split = message_text.lstrip(config.prefix).lower().split(maxsplit=1)
    if len(split) < 2:
        return
    key, value = split
    key = key.strip().lower()
    value = value.strip().lower()

    if key in ['tag', 'tags']:
        tmp = await client.send_message(
            message.channel, 'Looking through tags...'
        )
        match = matcher(value, tags.keys())
        output = 'Couldn\'t find that tag'
        output = '+*{}*: {}'.format(
            match, tags.get(match, 'Description not found')
        )
        if output.endswith('(range)'):
            output = output.lstrip('+')
        await client.edit_message(tmp, output)
    elif key in ['move', 'moves']:
        tmp = await client.send_message(
            message.channel, 'Looking through moves...'
        )
        match = matcher(value, moves.keys())
        output = 'Couldn\'t find that move'
        if match:
            output = '{}'.format(
                moves.get(match, 'Couldn\'t find that move')
            )
        await client.edit_message(tmp, output)


def matcher(value, options):
    match = process.extractOne(value, options, scorer=fuzz.token_set_ratio)
    if not match:
        return None
    return match[0]


def get_config():
    default_prefix = '!'
    parser = argparse.ArgumentParser(description='Start up sprawlbot.')
    parser.add_argument('--token', '-t')
    parser.add_argument('--prefix', '-p', default=default_prefix)
    parser.add_argument('--reset', '-r', action='store_true')
    parser.add_argument('--setup', '-s', action='store_true')
    args = parser.parse_args()

    if args.reset:
        os.remove('config.json')
    del args.reset

    try:
        with open('config.json') as f:
            config = json.load(f)
            args.token = args.token or config.get('token')
            args.prefix = args.prefix or config.get('prefix')
    except:
        print('Config file not found.')

    if args.setup or not args.token:
        conf = settings_dialog(default_prefix)
        del args.setup
        args.token = conf.get('token')
        args.prefix = conf.get('prefix')
        with open('config.json', 'w') as f:
            json.dump(vars(args), f, indent=4, sort_keys=True)

    if not args.token:
        print('Error: Token not found.')
        sys.exit()
    if not args.prefix:
        args.prefix = default_prefix

    return args


def settings_dialog(default_prefix):
    print(
        'Please enter your bot\'s token ' +
        '(from https://discordapp.com/developers/applications/me)'
    )
    token = input('> ').strip()
    if not token:
        print('No token entered...')
        sys.exit()
    prefix = input(
        'Enter the bot\'s command prefix ' +
        '(leave blank for "{}"): '.format(default_prefix)
    ).strip()

    return {
        'token': token,
        'prefix': prefix or default_prefix,
    }


if __name__ == '__main__':
    config = get_config()

    with open('tags.json') as f:
        tags = json.load(f)

    with open('moves.json') as f:
        moves = json.load(f)

    try:
        print('Starting sprawlbot...')
        client.run(config.token)
    except discord.errors.LoginFailure:
        print('Could not log in to Discord. Check that your token is correct.')
        client.close()
