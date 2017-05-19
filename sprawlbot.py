#!/usr/bin/python3
import argparse
import json
import os
from pathlib import Path
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
    message_text = message.content.strip()
    if not message_text.startswith(config.prefix):
        return

    command, *term = (
        message_text.lstrip(config.prefix).lower().split(maxsplit=1)
    )

    selected = None
    for command_set in options:
        if command in command_set:
            selected = options.get(command_set)
            break
    if not selected:
        return

    if not term:
        await client.send_message(
            message.channel, selected.get('usage').format(prefix=config.prefix)
        )
        return

    term = term[0]

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

    data = {}
    data_dir = Path('data')
    data_files = ['tags', 'moves', 'cyber']
    for file in data_files:
        with open(str(data_dir / '{}.json'.format(file))) as f:
            data[file] = json.load(f)

    options = {
        ('tag', 'tags'): {
            'descriptions': data.get('tags', {}),
            'output': '+*{key}*: {value}',
            'usage': (
                '```{prefix}tag[s] {{tag name}}\n\n'
                'Search the tag list for the specified tag.\n'
                'This includes weapon and gear tags. The tag name you search '
                'for does not need to be exact, fuzzy finding is used.\n'
                'ex: {prefix}tag encrypt'
                '```'
            )
        },
        ('move', 'moves'): {
            'descriptions': data.get('moves', {}),
            'usage': (
                '```{prefix}move[s] {{move name}}\n\n'
                'Search the move list for the specified move.\n'
                'This displays the full move text. The move name you search '
                'for does not need to be exact, fuzzy finding is used.\n'
                'ex: {prefix}move pressure'
                '```'
            )
        },
        ('cyber', 'cyberwear'): {
            'descriptions': data.get('cyber', {}),
            'usage': (
                '```{prefix}cyber[wear] {{cyberwear name}}\n\n'
                'Search the cyberwear list for the specified one.\n'
                'This displays the information about that cyberware. '
                'The name you search for does not need to be exact, '
                'fuzzy finding is used.\n'
                'ex: {prefix}cyber arm'
                '```'
            )
        },
        ('roll',): {
            'function': roll,
            'descriptions': data.get('moves', {}),
            'output': '{mention} {function}',
            'usage': (
                '```{prefix}roll {{move name}} [+/- modifier]\n\n'
                'Roll the specified move.\n'
                'This rolls 2d6, then adds or subtracts any provided modifier '
                'and displays relevant move text. Only the parts of the move '
                'applicable to the roll will be shown.\n'
                'ex: {prefix}roll mix +2'
                '```'
            )
        },
    }

    try:
        print('Starting sprawlbot...')
        client.run(config.token)
    except discord.errors.LoginFailure:
        print('Could not log in to Discord. Check that your token is correct.')
        client.close()
