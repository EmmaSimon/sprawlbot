#!/usr/bin/python3
import argparse
import json
import os
import random
import re
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
    command, term = split
    command = command.strip().lower()
    term = term.strip().lower()

    options = {
        ('tag', 'tags'): {
            'descriptions': tags,
            'output': '+*{key}*: {value}',
        },
        ('move', 'moves'): {
            'descriptions': moves,
        },
        ('cyber', 'cyberwear'): {
            'descriptions': cyberwear,
        },
        ('roll',): {
            'function': roll,
            'descriptions': moves,
            'output': '{mention} {function}'
        },
    }
    selected = None
    for command_set in options:
        if command in command_set:
            selected = options.get(command_set)
            break
    if not selected:
        return

    match = matcher(term, selected.get('descriptions', {}).keys())
    match_content = selected.get(
        'descriptions', {}
    ).get(match, 'Description not found')
    if isinstance(match_content, dict):
        match_content = format_rollable(move=match_content)
    if selected.get('function'):
        output = selected.get('output', '{function}').format(
            function=selected.get('function')(
                match=match, selected=selected, term=term
            ), key=match, value=match_content, mention=message.author.mention,
        )
    else:
        output = selected.get('output', '{value}').format(
            key=match, value=match_content, mention=message.author.mention,
        )

    if output.endswith('(range)'):
        output = output.lstrip('+')
    await client.send_message(
        message.channel, output
    )


def matcher(value, options):
    match = process.extractOne(value, options, scorer=fuzz.token_set_ratio)
    if not match:
        return None
    return match[0]


def format_rollable(move=None, roll=None):
    if not move:
        return ''
    outcome_order = ['7+', '10+', '7-9', '6-']
    include = []
    if roll:
        result = ''
        outcome_tests = {
            '7+': lambda x: x >= 7,
            '10+': lambda x: x >= 10,
            '7-9': lambda x: 7 <= x <= 9,
            '6-': lambda x: x <= 6,
        }
        for outcome in outcome_order:
            if outcome_tests.get(outcome)(roll):
                if outcome == '7+' and move.get('if_success'):
                    result = move.get('if_success')
                elif outcome == '6-' and outcome not in move.get('outcomes'):
                    result = '***Miss...***\n\n'
                if outcome not in move.get('outcomes'):
                    continue
                include.append(outcome)
    else:
        for outcome in outcome_order:
            if outcome not in move.get('outcomes'):
                continue
            include.append(outcome)
        result = move.get('if_success', '')

    return re.sub('\n{3,}', '\n\n', '{}\n\n{}\n\n{}\n\n{}'.format(
        move.get('before', None),
        '\n'.join([
            '**{}**: {}'.format(
                outcome, move.get('outcomes', {}).get(outcome)
            ) for outcome in include
        ]),
        result, move.get('after', '')
    ))


def roll(match=None, selected=None, term=''):
    dice = random.randint(1, 6), random.randint(1, 6)
    total = dice[0] + dice[1]
    modifier = re.search(r'^([+-]) *([0-9]+)|([+-]) *([0-9]+)$', term)
    modify_text = ''
    if modifier:
        sign = modifier.group(1) or modifier.group(3)
        num = modifier.group(2) or modifier.group(4)
        if sign == '-':
            total -= int(num)
        if sign == '+':
            total += int(num)
        modify_text = '{} {} '.format(sign, num)
    roll_text = '🎲 ({} + {}) {}= {}'.format(*dice, modify_text, total)
    move = selected.get('descriptions', {}).get(match)
    return '{}\n{}'.format(
        roll_text, format_rollable(move, roll=total)
    )


def get_config():
    default_prefix = '!'
    parser = argparse.ArgumentParser(description='Start up sprawlbot.')
    parser.add_argument('--token', '-t')
    parser.add_argument('--prefix', '-p', default=default_prefix)
    parser.add_argument('--reset', '-r', action='store_true')
    parser.add_argument('--setup', '-s', action='store_true')
    parser.add_argument('--no-prompt', action='store_true')
    args = parser.parse_args()

    if args.reset:
        os.remove('config.json')

    try:
        with open('config.json') as f:
            config = json.load(f)
            args.token = args.token or config.get('token')
            args.prefix = args.prefix or config.get('prefix')
    except:
        print('Config file not found.')

    if not args.no_prompt and args.setup or not args.token:
        conf = settings_dialog(default_prefix)
        args.token = conf.get('token')
        args.prefix = conf.get('prefix')
        with open('config.json', 'w') as f:
            json.dump({
                'token': args.token,
                'prefix': args.prefix,
            }, f, indent=4, sort_keys=True)

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
    with open('cyber.json') as f:
        cyberwear = json.load(f)

    try:
        print('Starting sprawlbot...')
        client.run(config.token)
    except discord.errors.LoginFailure:
        print('Could not log in to Discord. Check that your token is correct.')
        client.close()
