# -*- coding: utf-8 -*-
import asyncio
import datetime
import importlib
import json
import os
import random
import re
import sys
from functools import partial
from typing import TYPE_CHECKING, Awaitable, Callable, List, Optional, Union

from .colors import yellow

if TYPE_CHECKING:
    from .bot import Bot
    from .client import Client
    from .discord_client import DiscordClient

discord = importlib.import_module('discord')
fortnitepy = importlib.import_module('fortnitepy')


Clients = Union[
    'Bot',
    'Client'
]
Messages = Union[
    fortnitepy.FriendMessage,
    fortnitepy.PartyMessage,
    discord.Message
]
Users = Union[
    fortnitepy.User,
    fortnitepy.Friend,
    fortnitepy.PartyMember,
    discord.User,
    discord.Member
]


class PartyPrivacy(fortnitepy.Enum):
    PUBLIC = {
        'partyType': 'Public',
        'inviteRestriction': 'AnyMember',
        'onlyLeaderFriendsCanJoin': False,
        'presencePermission': 'Anyone',
        'invitePermission': 'Anyone',
        'acceptingMembers': True,
    }
    FRIENDS_ALLOW_FRIENDS_OF_FRIENDS = {
        'partyType': 'FriendsOnly',
        'inviteRestriction': 'AnyMember',
        'onlyLeaderFriendsCanJoin': False,
        'presencePermission': 'Anyone',
        'invitePermission': 'Anyone',
        'acceptingMembers': True,
    }
    FRIENDS = {
        'partyType': 'FriendsOnly',
        'inviteRestriction': 'LeaderOnly',
        'onlyLeaderFriendsCanJoin': True,
        'presencePermission': 'Leader',
        'invitePermission': 'Leader',
        'acceptingMembers': False,
    }
    PRIVATE_ALLOW_FRIENDS_OF_FRIENDS = {
        'partyType': 'Private',
        'inviteRestriction': 'AnyMember',
        'onlyLeaderFriendsCanJoin': False,
        'presencePermission': 'Noone',
        'invitePermission': 'Anyone',
        'acceptingMembers': False,
    }
    PRIVATE = {
        'partyType': 'Private',
        'inviteRestriction': 'LeaderOnly',
        'onlyLeaderFriendsCanJoin': True,
        'presencePermission': 'Noone',
        'invitePermission': 'Leader',
        'acceptingMembers': False,
    }


class FindUserMatchMethod(fortnitepy.Enum):
    FULL = 'full'
    CONTAINS = 'contains'
    STARTS = 'starts'
    ENDS = 'ends'


class FindUserMode(fortnitepy.Enum):
    DISPLAY_NAME = 'display_name'
    ID = 'id'
    NAME_ID = 'name_id'


class DummyUser:
    def __init__(self) -> None:
        self.display_name = 'Dummy'
        self.id = 'Dummy'


class DummyMessage:
    def __init__(self, client: Clients, message: Messages, *,
                 content: Optional[str] = None,
                 author: Optional[Users] = None) -> None:
        self.client = client

        self.message = (
            message
            if not isinstance(message, self.__class__) else
            message.message
        )
        self.content = content or message.content

        self.author = author or message.author
        self.created_at = (
            message.created_at
            if hasattr(message, 'created_at') else
            datetime.datetime.utcnow()
        )

        self.result = ''

    def reply(self, content: str) -> None:
        self.result += f'\n{content}'


class MyMessage:
    def __init__(self, client: Clients, message: Messages, *,
                 content: Optional[str] = None,
                 author: Optional[Users] = None,
                 discord_client: Optional['DiscordClient'] = None) -> None:
        self.client = client
        self.discord_client = discord_client or client.discord_client

        self.message = (
            message
            if not isinstance(message, self.__class__) else
            message.message
        )
        self.content = content or message.content
        self.content = self.content.strip('\r\n').strip('\r').strip('\n')

        self.args = re.split(r'\s', self.content)
        self.author = author or message.author
        self.user_type = (
            self.discord_client.get_user_type(message.author.id)
            if self.is_discord_message() else
            'owner'
            if not isinstance(self.message, (discord.Message, fortnitepy.message.MessageBase)) else
            self.client.get_user_type(message.author.id)
        )
        self.created_at = message.created_at
        self.prev = None

    def is_discord_message(self) -> bool:
        return isinstance(self.message, discord.Message)

    def is_friend_message(self) -> bool:
        return isinstance(self.message, fortnitepy.FriendMessage)

    def is_party_message(self) -> bool:
        return isinstance(self.message, fortnitepy.PartyMessage)

    async def reply(self, content: str) -> None:
        content = str(content)
        if isinstance(self.message, fortnitepy.message.MessageBase):
            await self.message.reply(content)
        elif isinstance(self.message, discord.Message):
            lines = content.split('\n')
            texts = []
            num = 0
            for line in lines:
                line += '\n'
                if self.client.bot.get_list_index(texts, num) is None:
                    texts.append('')
                if len(texts[num] + line) < 2000:
                    texts[num] += line
                else:
                    if texts[num] == '':
                        s = [line[i:i + 2000] for i in range(0, len(line), 2000)]
                        for l in s:
                            texts[num] = l
                            num += 1
                    else:
                        num += 1
                        texts[num] = line
            for text in texts:
                await self.message.channel.send(text)
        elif isinstance(self.message, DummyMessage):
            self.message.reply(content)


class Command:
    def __init__(self, coro: Awaitable, **kwargs) -> None:
        if not asyncio.iscoroutinefunction(coro):
            raise TypeError('Command callback must be a coroutine')

        async def callback(*args, **kwargs):
            await coro(self, *args, **kwargs)

        self.callback = callback

        self.name = kwargs.get('name') or coro.__name__
        self.usage = kwargs.get('usage')
        self.discord_required = kwargs.get('discord_required', False)


def command(name: Optional[str] = None,
            cls: Optional[Command] = None,
            **attrs: dict) -> callable:
    cls = cls or Command

    def deco(func):
        if isinstance(func, Command):
            raise TypeError('Callback is already a command.')
        return cls(func, name=name, **attrs)

    return deco


async def add_to_list(attr: str, message: MyMessage, user: fortnitepy.User):
    client = message.client

    if user.id in getattr(client, f'_{attr}'):
        await message.reply(
            client.l(
                'already_in_list',
                client.l(attr),
                client.name(user)
            )
        )
        return
    getattr(client, f'_{attr}')[user.id] = user
    client.config['fortnite'][attr].append(client.get_user_str(user))
    client.bot.save_json('config', client.bot.config)
    await message.reply(
        client.l(
            'add_to_list',
            client.l(attr),
            client.name(user)
        )
    )


async def remove_from_list(attr: str, message: MyMessage, user: fortnitepy.User):
    client = message.client

    if user.id not in getattr(client, f'_{attr}'):
        await message.reply(
            client.l(
                'not_in_list',
                client.l(attr),
                client.name(user)
            )
        )
        return
    getattr(client, f'_{attr}').pop(user.id)
    client.config['fortnite'][attr].remove(client.get_user_str(user))
    client.bot.save_json('config', client.bot.config)
    await message.reply(
        client.l(
            'remove_from_list',
            client.l(attr),
            client.name(user)
        )
    )


async def list_operation(func: Callable, attr: str, command: Command,
                         message: MyMessage) -> None:
    client = message.client
    if len(message.args) < 2:
        await client.show_help(command, message)
        return

    users = client.find_users(
        ' '.join(message.args[1:]),
        mode=FindUserMode.NAME_ID,
        method=FindUserMatchMethod.CONTAINS,
        me=message.author
    )
    user = await client.fetch_user(' '.join(message.args[1:]), cache=True)
    if user is not None and user not in users:
        users.append(user)

    if client.config['search_max'] and len(users) > client.config['search_max']:
        await message.reply(
            client.l('too_many', client.l('user'), len(users))
        )
        return

    if len(users) == 0:
        await message.reply(
            client.l(
                'not_found',
                client.l('user'),
                ' '.join(message.args[1:])
            )
        )
    elif len(users) == 1:
        await func(attr, message, users[0])
    else:
        client.select[message.author.id] = {
            'exec': f'await func(attr, message, user)',
            'globals': {**globals(), **locals()},
            'variables': [
                {'user': user, 'func': func}
                for user in users
            ]
        }
        await message.reply(
            ('\n'.join([f'{num}: {client.name(user)}'
                        for num, user in enumerate(users, 1)])
                + '\n' + client.l('enter_number_to_select', client.l(attr)))
        )


async def discord_add_to_list(attr: str, message: MyMessage, user: discord.User):
    client = message.client

    if user.id in getattr(message.discord_client, f'_{attr}'):
        await message.reply(
            client.l(
                'already_in_list',
                client.l(attr),
                client.name(user)
            )
        )
        return
    getattr(message.discord_client, f'_{attr}')[user.id] = user
    client.config['discord'][attr].append(user.id)
    client.bot.save_json('config', client.bot.config)
    await message.reply(
        client.l(
            'add_to_list',
            client.l(attr),
            message.discord_client.name(user)
        )
    )


async def discord_remove_from_list(attr: str, message: MyMessage, user: discord.User):
    client = message.client

    if user.id not in getattr(message.discord_client, f'_{attr}'):
        await message.reply(
            client.l(
                'not_in_list',
                client.l(attr),
                client.name(user)
            )
        )
        return
    getattr(message.discord_client, f'_{attr}').pop[user.id]
    client.config['discord'][attr].append(user.id)
    client.bot.save_json('config', client.bot.config)
    await message.reply(
        client.l(
            'remove_from_list',
            client.l(attr),
            client.discord_bot.name(user)
        )
    )


async def discord_list_operation(func: Callable, attr: str, command: Command,
                                 message: MyMessage) -> None:
    client = message.client
    if len(message.args) < 2 or not message.args[1].isdigit():
        await client.show_help(command, message)
        return

    user = message.discord_client.get_user(int(message.args[1]))
    if user is None:
        try:
            user = await message.discord_client.fetch_user(int(message.args[1]))
        except discord.NotFound:
            pass

    if user is None:
        await message.reply(
            client.l(
                'not_found',
                client.l('user'),
                message.args[1]
            )
        )
    else:
        await func(attr, message, user)


async def all_cosmetics(item: str, client: 'Client', message: MyMessage) -> None:
    attr = f'is_{client.bot.convert_backend_to_key(item)}_lock_for'
    if getattr(client, attr)(message.user_type):
        await message.reply(
            client.l('cosmetic_locked')
        )
        return

    async def all_cosmetics():
        cosmetics = [
            i for i in client.bot.main_items.values()
            if i['type']['backendValue'] == item
        ]
        for cosmetic in cosmetics:
            if getattr(client, attr)(message.user_type):
                await message.reply(
                    client.l('cosmetic_locked')
                )
                return

            await client.party.me.change_asset(
                cosmetic['type']['backendValue'],
                cosmetic['path'],
                keep=False
            )
            await message.reply(
                f'{cosmetic["type"]["displayValue"]}: {client.name_cosmetic(cosmetic)}'
            )
            await asyncio.sleep(5)
        await message.reply(
            client.l(
                'has_end',
                client.bot.l(client.bot.convert_backend_to_key(item))
            )
        )

    task = client.loop.create_task(all_cosmetics())
    client.stoppable_tasks.append(task)


async def cosmetic_search(item: Optional[str], mode: str, command: Command,
                          client: 'Client', message: MyMessage) -> None:
    if len(message.args) < 2:
        await client.show_help(command, message)
        return

    async def set_cosmetic(cosmetic):
        item = cosmetic['type']['backendValue']
        attr = f'is_{client.bot.convert_backend_to_key(item)}_lock_for'
        if getattr(client, attr)(message.user_type):
            await message.reply(
                client.l('cosmetic_locked')
            )
            return
        await client.party.me.change_asset(item, cosmetic['path'])
        await message.reply(
            client.l(
                'set_to',
                cosmetic['type']['displayValue'],
                client.name_cosmetic(cosmetic)
            )
        )

    cosmetics = client.searcher.search_item(mode, ' '.join(message.args[1:]), item)

    if client.config['search_max'] and len(cosmetics) > client.config['search_max']:
        await message.reply(
            client.l('too_many', client.l('item'), len(cosmetics))
        )
        return

    if len(cosmetics) == 0:
        await message.reply(
            client.l(
                'not_found',
                client.l('item'),
                ' '.join(message.args[1:])
            )
        )
        return

    if len(cosmetics) == 1:
        await set_cosmetic(cosmetics[0])
    else:
        client.select[message.author.id] = {
            'exec': 'await set_cosmetic(cosmetic)',
            'globals': {**globals(), **locals()},
            'variables': [
                {'cosmetic': cosmetic}
                for cosmetic in cosmetics
            ]
        }
        if item is None:
            await message.reply(
                ('\n'.join([f'{num}: {client.name_cosmetic(cosmetic)} ({cosmetic["type"]["displayValue"]})'
                            for num, cosmetic in enumerate(cosmetics, 1)])
                    + '\n' + client.l('enter_number_to_select', client.l('item')))
            )
        else:
            await message.reply(
                ('\n'.join([f'{num}: {client.name_cosmetic(cosmetic)}'
                            for num, cosmetic in enumerate(cosmetics, 1)])
                    + '\n' + client.l('enter_number_to_select', client.l('item')))
            )


async def random_cosmetic(item: Optional[str], command: Command, client: 'Client',
                          message: MyMessage) -> None:
    attr = f'is_{client.bot.convert_backend_to_key(item)}_lock_for'
    if not getattr(client, attr)(message.user_type):
        cosmetic = client.bot.searcher.random_item(item)
        await client.party.me.change_asset(cosmetic['type']['backendValue'], cosmetic['path'])
        await message.reply(
            client.l(
                'set_to',
                cosmetic['type']['displayValue'],
                client.name_cosmetic(cosmetic)
            )
        )
    else:
        await message.reply(
            client.l('cosmetic_locked')
        )


async def playlist_search(mode: str, command: Command,
                          client: 'Client', message: MyMessage) -> None:
    if len(message.args) < 2:
        await client.show_help(command, message)
        return

    async def set_playlist(message, playlist):
        if not client.party.leader:
            await message.reply(
                client.l('not_a_party_leader')
            )
            return
        try:
            await client.party.set_playlist(playlist['id'])
        except fortnitepy.Forbidden:
            await message.reply(
                client.l('not_a_party_leader')
            )
            return
        await message.reply(
            client.l(
                'set_to',
                client.bot.l('playlist'),
                client.name_cosmetic(playlist)
            )
        )

    playlists = client.searcher.search_playlist(
        mode,
        ' '.join(message.args[1:])
    )

    if client.config['search_max'] and len(playlists) > client.config['search_max']:
        await message.reply(
            client.l('too_many', client.l('playlist'), len(playlists))
        )
        return

    if len(playlists) == 0:
        await message.reply(
            client.l(
                'not_found',
                client.l('playlist'),
                ' '.join(message.args[1:])
            )
        )
    elif len(playlists) == 1:
        await set_playlist(message, playlists[0])
    else:
        client.select[message.author.id] = {
            'exec': 'await set_playlist(message, playlist)',
            'globals': {**globals(), **locals()},
            'variables': [
                {'playlist': playlist}
                for playlist in playlists
            ]
        }
        await message.reply(
            ('\n'.join([f'{num}: {client.name_cosmetic(playlist)}'
                        for num, playlist in enumerate(playlists, 1)])
                + '\n' + client.l('enter_number_to_select', client.bot.l('playlist')))
        )


async def set_config_for(keys: List[str], command: Command,
                         message: MyMessage) -> None:
    client = message.client

    if len(message.args) < 2:
        await client.show_help(command, message)
        return


    user_types = [(i, client.commands[i['value']]) for i in client.bot.multiple_select_user_type]

    final = []
    for arg in message.args[1:]:
        for value, values in user_types:
            if arg in values:
                final.append(value)
                break
        else:
            await message.reply(client.l(
                'must_be_one_of',
                client.l('user_type'),
                ', '.join([i[0] for _, i in user_types])
            ))
            return

    if client.bot.none_data in final:
        final = client.bot.none_data

    client.bot.set_dict_key(
        client.config,
        keys,
        [i['real_value'] for i in final]
    )
    client.bot.save_json('config', client.bot.config)
    await message.reply(
        client.l(
            'set_to',
            client.bot.web.l(f'editor_{"_".join(keys)}'),
            ', '.join([i['display_value'].get_text() for i in final])
        )
    )


async def set_config_operation(keys: List[str], command: Command,
                         message: MyMessage) -> None:
    client = message.client

    if len(message.args) < 2:
        await client.show_help(command, message)
        return


    operations = [(i, client.commands.get(f'operation_{i["value"]}') or client.commands[i['value']])
                  for i in client.bot.multiple_select_user_operation]

    final = []
    for arg in message.args[1:]:
        for value, values in operations:
            if arg in values:
                final.append(value)
                break
        else:
            await message.reply(client.l(
                'must_be_one_of',
                client.l('operation'),
                ', '.join([i[0] for _, i in operations])
            ))
            return

    if client.bot.none_data in final:
        final = client.bot.none_data

    client.bot.set_dict_key(
        client.config,
        keys,
        [i['real_value'] for i in final]
    )
    client.bot.save_json('config', client.bot.config)
    await message.reply(
        client.l(
            'set_to',
            client.bot.web.l(f'editor_{"_".join(keys)}'),
            ', '.join([i['display_value'].get_text() for i in final])
        )
    )


async def set_mimic(attr: str, keys: List[str], command: Command,
                    message: MyMessage) -> None:
    client = message.client

    if len(message.args) < 2:
        await client.show_help(command, message)
        return

    if message.args[1] in [*client.commands['add'], *client.commands['remove']]:
        users = client.find_users(
            ' '.join(message.args[2:]),
            mode=FindUserMode.NAME_ID,
            method=FindUserMatchMethod.CONTAINS,
            me=message.author
        )

        async def operation(user):
            mimic = getattr(client, attr)
            if message.args[1] in client.commands['add']:
                if user.id in mimic:
                    await message.reply(
                        client.l(
                            'already_in_list',
                            client.l(attr),
                            client.name(user)
                        )
                    )
                    return
                mimic.append(user.id)
                key = 'add_to_list'
            else:
                if user.id not in mimic:
                    await message.reply(
                        client.l(
                            'not_in_list',
                            client.l(attr),
                            client.name(user)
                        )
                    )
                    return
                mimic.remove(user.id)
                key = 'remove_from_list'

            await message.reply(
                client.l(
                    key,
                    client.l(attr),
                    client.name(user)
                )
            )

        if client.config['search_max'] and len(users) > client.config['search_max']:
            await message.reply(
                client.l('too_many', client.l('user'), len(users))
            )
            return

        if len(users) == 0:
            await message.reply(
                client.l(
                    'not_found',
                    client.l('user'),
                    ' '.join(message.args[2:])
                )
            )
        elif len(users) == 1:
            await operation(users[0])
        else:
            client.select[message.author.id] = {
                'exec': 'await operation(user)',
                'globals': {**globals(), **locals()},
                'variables': [
                    {'user': user}
                    for user in users
                ]
            }
            await message.reply(
                ('\n'.join([f'{num}: {client.name(user)}'
                            for num, user in enumerate(users, 1)])
                    + '\n' + client.l('enter_number_to_select', client.l('user')))
            )
    else:
        await set_config_for(keys, command, message)


class DefaultCommands:
    @command(
        name='exec',
        usage='{name} [code]'
    )
    async def exec(command: Command, client: 'Client', message: MyMessage) -> None:
        var = globals()
        var.update(locals())
        var.update(client.variables)
        result, out, err = await client.bot.aexec(' '.join(message.content.split(' ')[1:]), var)
        if out:
            client.send(out)
        if err:
            client.send(
                err,
                file=sys.stderr
            )
        client.send(
            str(result),
            add_p=client.time
        )
        await message.reply(str(result))

    @command(
        name='clear',
        usage='{name}'
    )
    async def clear(command: Command, client: 'Client', message: MyMessage) -> None:
        if sys.platform == 'win32':
            os.system('cls')
        else:
            os.system('clear')
        await message.reply(
            client.l('console_clear')
        )

    @command(
        name='help',
        usage='{name} [{client.l("command")}]'
    )
    async def help(command: Command, client: 'Client', message: MyMessage) -> None:
        if len(message.args) < 2:
            await client.show_help(command, message)
            return

        cmd = client.all_commands.get(message.args[1])
        if cmd is None:
            for identifier, words in client.commands['commands'].items():
                if message.args[1] in words:
                    cmd = client.all_commands[identifier]
                    break
            else:
                await message.reply(
                    client.l('please_enter_valid_number')
                )
                return

        await client.show_help(cmd, message)

    @command(
        name='check_update',
        usage='{name}'
    )
    async def check_update(command: Command, client: 'Client', message: MyMessage) -> None:
        await message.reply(client.l('checking_update'))
        if await client.bot.updater.check_updates(client.bot.dev):
            await message.reply(client.l('updated'))
        else:
            await message.reply(client.l('no_update'))

    @command(
        name='stat',
        usage='{name} [{client.l("stat_usage", **client.variables_without_self)}] [{client.l("command")}/{client.l("ng_word")}]'
    )
    async def stat(command: Command, client: 'Client', message: MyMessage) -> None:
        if len(message.args) < 2:
            await client.show_help(command, message)
            return

        def get_stats(key):
            stats = {}
            for user_id, user_stat in client.bot.command_stats[client.user.id][key].items():
                for word, number in user_stat.items():
                    if word not in stats:
                        stats[word] = {
                            'count': 0,
                            'most_user': {
                                'id': None,
                                'count': 0
                            }
                        }
                    
                    stats[word]['count'] += number
                    if number > stats[word]['most_user']['count']:
                        stats[word]['most_user'] = {
                            'id': user_id,
                            'count': number
                        }
            return stats

        async def get_user(data):
            user = None
            name = None
            if client.is_id(data['id']):
                user = await client.fetch_user(data['id'], cache=True)
                name = client.name(user)
            elif client.discord_client is not None and client.discord_client.is_ready():
                user = await client.discord_client.fetch_user(int(data['id']))
                name = client.discord_client.name(user)
            elif client.bot.discord_client is not None and client.bot.discord_client.is_ready():
                user = await client.bot.discord_client.fetch_user(int(data['id']))
                name = client.bot.discord_client.name(user)
            return user, name

        if message.args[1] in client.commands['command']:
            if len(message.args) < 3:
                await client.show_help(command, message)
                return

            cmd = client.all_commands.get(message.args[2])
            if cmd is None:
                for identifier, words in client.commands['commands'].items():
                    if message.args[2] in words:
                        cmd = client.all_commands[identifier]
                        break
                else:
                    await message.reply(
                        client.l('please_enter_valid_number')
                    )
                    return

            stat = client.bot.command_stats.get(client.user.id)
            if stat is None:
                await message.reply(
                    client.l('no_stat')
                )
                return

            stats = get_stats('commands')

            command_stat = stats.get(cmd.name)
            if command_stat is None:
                await message.reply(
                    client.l(
                        'no_stat_command',
                        cmd.name
                    )
                )
                return

            most_user = command_stat['most_user']
            user = None
            name = None
            if most_user is not None:
                user, name = await get_user(most_user)
            if user is None:
                await message.reply(
                    client.l(
                        'stat_command',
                        cmd.name,
                        command_stat['count']
                    )
                )
            else:
                await message.reply(
                    client.l(
                        'stat_command_user',
                        cmd.name,
                        command_stat['count'],
                        name,
                        most_user['count']
                    )
                )
        elif message.args[1] in client.commands['ng_word']:
            if len(message.args) < 3:
                await client.show_help(command, message)
                return

            text = ' '.join(message.args[2:])
            for ng in client.config['ng_words']:
                if text in ng['words']:
                    break
            else:
                await message.reply(
                    client.l('please_enter_valid_number')
                )
                return

            stat = client.bot.command_stats.get(client.user.id)
            if stat is None:
                await message.reply(
                    client.l('no_stat')
                )
                return

            stats = get_stats('ngs')

            ng_word_stat = stats.get(text)
            if ng_word_stat is None:
                await message.reply(
                    client.l(
                        'no_stat_ng_word',
                        text
                    )
                )
                return

            most_user = ng_word_stat['most_user']
            user = None
            name = None
            if most_user is not None:
                user, name = await get_user(most_user)
            if user is None:
                await message.reply(
                    client.l(
                        'stat_ng_word',
                        text,
                        ng_word_stat['count']
                    )
                )
            else:
                await message.reply(
                    client.l(
                        'stat_ng_word_user',
                        text,
                        ng_word_stat['count'],
                        name,
                        most_user['count']
                    )
                )
        elif message.args[1] in client.commands['most']:
            stats = get_stats('commands')
            identifier, data = max(stats.items(), key=lambda x: x[1]['count'])

            stats_ng_word = get_stats('ngs')
            text, data_ng_word = max(stats_ng_word.items(), key=lambda x: x[1]['count'])

            await message.reply(
                client.l(
                    'stat_most',
                    identifier,
                    data['count'],
                    text,
                    data_ng_word['count']
                )
            )

    @command(
        name='ping',
        usage='{name}'
    )
    async def ping(command: Command, client: 'Client', message: MyMessage) -> None:
        latency = abs((datetime.datetime.utcnow() - message.created_at).total_seconds())
        await message.reply(
            client.l('ping', int(latency * 1000))
        )

    @command(
        name='prev',
        usage='{name}'
    )
    async def prev(command: Command, client: 'Client', message: MyMessage) -> None:
        if message.prev is not None:
            await client.process_command(message.prev, None)

    @command(
        name='send_all',
        usage='{name} [{client.l("message")}]'
    )
    async def send_all(command: Command, client: 'Client', message: MyMessage) -> None:
        if len(message.args) < 2:
            await client.show_help(command, message)
            return

        tasks = []
        for c in client.bot.clients:
            mes = DummyMessage(c, message, content=' '.join(message.args[1:]))
            c.send(
                mes.content,
                user_name=c.name(mes.author),
                add_p=[lambda x: f'{c.name(mes.author)} | {x}', c.time]
            )
            task = client.loop.create_task(c.process_command(MyMessage(c, mes), None))
            tasks.append((c, mes, task))
        await asyncio.wait(
            [task for _, _, task in tasks],
            return_when=asyncio.ALL_COMPLETED
        )

        texts = []
        for c, mes, task in tasks:
            if mes.result:
                texts.append(f'[{client.name(c.user)}] {mes.result}')
        await message.reply('\n\n'.join(texts))

    @command(
        name='restart',
        usage='{name}'
    )
    async def restart(command: Command, client: 'Client', message: MyMessage) -> None:
        await message.reply(
            client.l('restarting')
        )
        await asyncio.sleep(1)
        await client.bot.reboot()

    @command(
        name='relogin',
        usage='{name}'
    )
    async def relogin(command: Command, client: 'Client', message: MyMessage) -> None:
        await message.reply(
            client.l('relogining')
        )
        await asyncio.sleep(1)
        await client.restart()
        await message.reply('done')

    @command(
        name='reload',
        usage='{name}'
    )
    async def reload(command: Command, client: 'Client', message: MyMessage) -> None:
        config, error_config = client.bot.load_config()
        if config is None and error_config is None:
            await message.reply(
                client.l('failed_to_load_config')
            )
            return
        if error_config:
            client.send(
                client.bot.l(
                    'error_keys',
                    '\n'.join(error_config),
                    default=(
                        '以下のキーに問題がありました\n{0}\n'
                        'There was an error on keys\n{0}\n'
                    )
                ),
                file=sys.stderr
            )
            await message.reply(
                client.l('failed_to_load_config')
            )
            return

        try:
            client_config = config['clients'][client.num]
        except IndexError:
            await message.reply(
                client.l('failed_to_load_config_index')
            )
            return

        client.bot.config['clients'][client.num].clear()
        client.bot.config['clients'][client.num].update(client_config)
        client.bot.fix_config(client.config)
        ret = await client.ready_init()
        if not ret:
            await message.reply(
                client.l('failed_to_load_config_init')
            )
            return
        await message.reply(
            client.l('load_config_success')
        )

        if client.config['fortnite']['refresh_on_reload']:
            coros = []

            items = [
                'AthenaCharacter',
                'AthenaBackpack',
                'AthenaPickaxe',
                'AthenaDance'
            ]
            for item in items:
                conf = client.bot.convert_backend_type(item)
                variants = []
                if item != 'AthenaDance' and client.config['fortnite'][f'{conf}_style'] is not None:
                    for style in client.config['fortnite'][f'{conf}_style']:
                        variant = client.get_config_variant(style)
                        if variant is not None:
                            variants.extend(variant['variants'])
                coro = client.party.me.change_asset(
                    item,
                    (client.get_config_item_path(client.config['fortnite'][conf])
                     or client.config['fortnite'][conf]),
                    variants=variants
                )
                coro.__qualname__ = f'ClientPartyMember.set_{conf}'
                coros.append(coro)
            await client.party.me.edit(
                *coros
            )

        commands, error_commands = client.bot.load_commands()
        if commands is None and error_commands is None:
            await message.reply(
                client.l('failed_to_load_commands')
            )
            return
        if error_commands:
            client.send(
                client.bot.l(
                    'error_keys',
                    '\n'.join(error_commands),
                    default=(
                        '以下のキーに問題がありました\n{0}\n'
                        'There was an error on keys\n{0}\n'
                    )
                ),
                file=sys.stderr
            )
            await message.reply(
                client.l('failed_to_load_config')
            )
            return

        client.commands = commands
        client.error_commands = error_commands

        custom_commands, error_custom_commands = client.bot.load_custom_commands()
        if custom_commands is None and error_custom_commands is None:
            await message.reply(
                client.l('failed_to_load_custom_commands')
            )
            return
        if error_custom_commands:
            client.send(
                client.bot.l(
                    'error_keys',
                    '\n'.join(error_custom_commands),
                    default=(
                        '以下のキーに問題がありました\n{0}\n'
                        'There was an error on keys\n{0}\n'
                    )
                ),
                file=sys.stderr
            )
            await message.reply(
                client.l('failed_to_load_config')
            )
            return

        client.custom_commands = custom_commands
        client.error_custom_commands = error_custom_commands

        await message.reply(
            client.l('load_commands_success')
        )

    @command(
        name='reload_all',
        usage='{name}'
    )
    async def reload_all(command: Command, client: 'Client', message: MyMessage) -> None:
        config, error_config = client.bot.load_config()
        if config is None and error_config is None:
            await message.reply(
                client.l('failed_to_load_config')
            )
            return
        if error_config:
            client.send(
                client.bot.l(
                    'error_keys',
                    '\n'.join(error_config),
                    default=(
                        '以下のキーに問題がありました\n{0}\n'
                        'There was an error on keys\n{0}\n'
                    )
                ),
                file=sys.stderr
            )
            await message.reply(
                client.l('failed_to_load_config')
            )
            return

        client.bot.config.clear()
        client.bot.config.update(config)
        client.bot.error_config = error_config
        client.bot.fix_config_all()
        for c in client.bot.clients:
            try:
                ret = await c.ready_init()
                if not ret:
                    await message.reply(
                        c.l('failed_to_load_config_init')
                    )
                    return

                if c.config['fortnite']['refresh_on_reload']:
                    coros = []

                    items = [
                        'AthenaCharacter',
                        'AthenaBackpack',
                        'AthenaPickaxe',
                        'AthenaDance'
                    ]
                    for item in items:
                        conf = c.bot.convert_backend_type(item)
                        variants = []
                        if item != 'AthenaDance' and c.config['fortnite'][f'{conf}_style'] is not None:
                            for style in c.config['fortnite'][f'{conf}_style']:
                                variant = c.get_config_variant(style)
                                if variant is not None:
                                    variants.extend(variant['variants'])
                        coro = c.party.me.change_asset(
                            item,
                            (c.get_config_item_path(c.config['fortnite'][conf])
                             or c.config['fortnite'][conf]),
                            variants=variants
                        )
                        coro.__qualname__ = f'ClientPartyMember.set_{conf}'
                        coros.append(coro)
                    await c.party.me.edit(
                        *coros
                    )
            except IndexError as e:
                client.debug_print_exception(e)

        client.bot.save_json('config', config)

        await message.reply(
            client.l('load_config_success')
        )

        commands, error_commands = client.bot.load_commands()
        if commands is None and error_commands is None:
            await message.reply(
                client.l('failed_to_load_commands')
            )
            return
        if error_commands:
            client.send(
                client.bot.l(
                    'error_keys',
                    '\n'.join(error_commands),
                    default=(
                        '以下のキーに問題がありました\n{0}\n'
                        'There was an error on keys\n{0}\n'
                    )
                ),
                file=sys.stderr
            )
            await message.reply(
                client.l('failed_to_load_config')
            )
            return

        client.bot.commands = commands
        client.bot.error_commands = error_commands
        for client in client.bot.clients:
            client.commands = commands

        custom_commands, error_custom_commands = client.bot.load_custom_commands()
        if custom_commands is None and error_custom_commands is None:
            await message.reply(
                client.l('failed_to_load_custom_commands')
            )
            return
        if error_custom_commands:
            client.send(
                client.bot.l(
                    'error_keys',
                    '\n'.join(error_custom_commands),
                    default=(
                        '以下のキーに問題がありました\n{0}\n'
                        'There was an error on keys\n{0}\n'
                    )
                ),
                file=sys.stderr
            )
            await message.reply(
                client.l('failed_to_load_config')
            )
            return

        client.bot.custom_commands = custom_commands
        client.bot.error_custom_commands = error_custom_commands
        for client in client.bot.clients:
            client.custom_commands = custom_commands

        await message.reply(
            client.l('load_commands_success')
        )

    @command(
        name='add_blacklist',
        usage='{name} [{client.l("name_or_id")}]'
    )
    async def add_blacklist(command: Command, client: 'Client', message: MyMessage) -> None:
        await list_operation(add_to_list, 'blacklist', command, message)

    @command(
        name='remove_blacklist',
        usage='{name} [{client.l("name_or_id")}]'
    )
    async def remove_blacklist(command: Command, client: 'Client', message: MyMessage) -> None:
        await list_operation(remove_from_list, 'blacklist', command, message)

    @command(
        name='add_whitelist',
        usage='{name} [{client.l("name_or_id")}]'
    )
    async def add_whitelist(command: Command, client: 'Client', message: MyMessage) -> None:
        await list_operation(add_to_list, 'whitelist', command, message)

    @command(
        name='remove_whitelist',
        usage='{name} [{client.l("name_or_id")}]'
    )
    async def remove_whitelist(command: Command, client: 'Client', message: MyMessage) -> None:
        await list_operation(remove_from_list, 'whitelist', command, message)

    @command(
        name='discord_add_blacklist',
        usage='{name} [{client.l("name_or_id")}]',
        discord_required=True
    )
    async def discord_add_blacklist(command: Command, client: 'Client', message: MyMessage) -> None:
        await discord_list_operation(discord_add_to_list, 'blacklist', command, message)

    @command(
        name='discord_remove_blacklist',
        usage='{name} [{client.l("name_or_id")}]',
        discord_required=True
    )
    async def discord_remove_blacklist(command: Command, client: 'Client', message: MyMessage) -> None:
        await discord_list_operation(discord_remove_from_list, 'blacklist', command, message)

    @command(
        name='discord_add_whitelist',
        usage='{name} [{client.l("name_or_id")}]',
        discord_required=True
    )
    async def discord_add_whitelist(command: Command, client: 'Client', message: MyMessage) -> None:
        await discord_list_operation(discord_add_to_list, 'whitelist', command, message)

    @command(
        name='discord_remove_whitelist',
        usage='{name} [{client.l("name_or_id")}]',
        discord_required=True
    )
    async def discord_remove_whitelist(command: Command, client: 'Client', message: MyMessage) -> None:
        await discord_list_operation(discord_remove_from_list, 'whitelist', command, message)

    @command(
        name='add_invitelist',
        usage='{name} [{client.l("name_or_id")}]'
    )
    async def add_invitelist(command: Command, client: 'Client', message: MyMessage) -> None:
        await list_operation(add_to_list, 'invitelist', command, message)

    @command(
        name='remove_invitelist',
        usage='{name} [{client.l("name_or_id")}]'
    )
    async def remove_invitelist(command: Command, client: 'Client', message: MyMessage) -> None:
        await list_operation(remove_from_list, 'invitelist', command, message)

    @command(
        name='ng_outfit_for',
        usage='{name} [{client.l("user_types", **client.variables_without_self)}]'
    )
    async def ng_outfit_for(command: Command, client: 'Client', message: MyMessage) -> None:
        await set_config_for(['fortnite', 'ng_outfit_for'], command, message)

    @command(
        name='ng_outfit_operation',
        usage='{name} [{client.l("operations", **client.variables_without_self)}]'
    )
    async def ng_outfit_operation(command: Command, client: 'Client', message: MyMessage) -> None:
        await set_config_operation(['fortnite', 'ng_outfit_operation'], command, message)

    @command(
        name='outfit_mimic_for',
        usage='{name} [{client.commands[add][0]}/{client.commands[remove][0]}/{client.l("user_types", **client.variables_without_self)}] ({client.l("name_or_id")})'
    )
    async def outfit_mimic_for(command: Command, client: 'Client', message: MyMessage) -> None:
        await set_mimic('outfit_mimic', ['fortnite', 'outfit_mimic_for'], command, message)

    @command(
        name='ng_backpack_for',
        usage='{name} [{client.l("user_types", **client.variables_without_self)}]'
    )
    async def ng_backpack_for(command: Command, client: 'Client', message: MyMessage) -> None:
        await set_config_for(['fortnite', 'ng_backpack_for'], command, message)

    @command(
        name='ng_backpack_operation',
        usage='{name} [{client.l("operations", **client.variables_without_self)}]'
    )
    async def ng_backpack_operation(command: Command, client: 'Client', message: MyMessage) -> None:
        await set_config_operation(['fortnite', 'ng_backpack_operation'], command, message)

    @command(
        name='backpack_mimic_for',
        usage='{name} [{client.commands[add][0]}/{client.commands[remove][0]}/{client.l("user_types", **client.variables_without_self)}] ({client.l("name_or_id")})'
    )
    async def backpack_mimic_for(command: Command, client: 'Client', message: MyMessage) -> None:
        await set_mimic('backpack_mimic', ['fortnite', 'backpack_mimic_for'], command, message)

    @command(
        name='ng_pickaxe_for',
        usage='{name} [{client.l("user_types", **client.variables_without_self)}]'
    )
    async def ng_pickaxe_for(command: Command, client: 'Client', message: MyMessage) -> None:
        await set_config_for(['fortnite', 'ng_pickaxe_for'], command, message)

    @command(
        name='ng_pickaxe_operation',
        usage='{name} [{client.l("operations", **client.variables_without_self)}]'
    )
    async def ng_pickaxe_operation(command: Command, client: 'Client', message: MyMessage) -> None:
        await set_config_operation(['fortnite', 'ng_pickaxe_operation'], command, message)

    @command(
        name='pickaxe_mimic_for',
        usage='{name} [{client.commands[add][0]}/{client.commands[remove][0]}/{client.l("user_types", **client.variables_without_self)}] ({client.l("name_or_id")})'
    )
    async def pickaxe_mimic_for(command: Command, client: 'Client', message: MyMessage) -> None:
        await set_mimic('pickaxe_mimic', ['fortnite', 'pickaxe_mimic_for'], command, message)

    @command(
        name='ng_emote_for',
        usage='{name} [{client.l("user_types", **client.variables_without_self)}]'
    )
    async def ng_emote_for(command: Command, client: 'Client', message: MyMessage) -> None:
        await set_config_for(['fortnite', 'ng_emote_for'], command, message)

    @command(
        name='ng_emote_operation',
        usage='{name} [{client.l("operations", **client.variables_without_self)}]'
    )
    async def ng_emote_operation(command: Command, client: 'Client', message: MyMessage) -> None:
        await set_config_operation(['fortnite', 'ng_emote_operation'], command, message)

    @command(
        name='emote_mimic_for',
        usage='{name} [{client.commands[add][0]}/{client.commands[remove][0]}/{client.l("user_types", **client.variables_without_self)}] ({client.l("name_or_id")})'
    )
    async def emote_mimic_for(command: Command, client: 'Client', message: MyMessage) -> None:
        await set_mimic('emote_mimic', ['fortnite', 'emote_mimic_for'], command, message)

    @command(
        name='ng_platform_for',
        usage='{name} [{client.l("user_types", **client.variables_without_self)}]'
    )
    async def ng_platform_for(command: Command, client: 'Client', message: MyMessage) -> None:
        await set_config_for(['fortnite', 'ng_platform_for'], command, message)

    @command(
        name='ng_platform_operation',
        usage='{name} [{client.l("operations", **client.variables_without_self)}]'
    )
    async def ng_platform_operation(command: Command, client: 'Client', message: MyMessage) -> None:
        await set_config_operation(['fortnite', 'ng_platform_operation'], command, message)

    @command(
        name='ng_name_for',
        usage='{name} [{client.l("user_types", **client.variables_without_self)}]'
    )
    async def ng_name_for(command: Command, client: 'Client', message: MyMessage) -> None:
        await set_config_for(['fortnite', 'ng_name_for'], command, message)

    @command(
        name='ng_name_operation',
        usage='{name} [{client.l("operations", **client.variables_without_self)}]'
    )
    async def ng_name_operation(command: Command, client: 'Client', message: MyMessage) -> None:
        await set_config_operation(['fortnite', 'ng_name_operation'], command, message)

    @command(
        name='accept_invite_for',
        usage='{name} [{client.l("user_types", **client.variables_without_self)}]'
    )
    async def accept_invite_for(command: Command, client: 'Client', message: MyMessage) -> None:
        await set_config_for(['fortnite', 'accept_invite_for'], command, message)

    @command(
        name='decline_invite_when',
        usage='{name} [{client.l("user_types", **client.variables_without_self)}]'
    )
    async def decline_invite_when(command: Command, client: 'Client', message: MyMessage) -> None:
        await set_config_for(['fortnite', 'decline_invite_when'], command, message)

    @command(
        name='invite_interval_for',
        usage='{name} [{client.l("user_types", **client.variables_without_self)}]'
    )
    async def invite_interval_for(command: Command, client: 'Client', message: MyMessage) -> None:
        await set_config_for(['fortnite', 'invite_interval_for'], command, message)

    @command(
        name='accept_friend_for',
        usage='{name} [{client.l("user_types", **client.variables_without_self)}]'
    )
    async def accept_friend_for(command: Command, client: 'Client', message: MyMessage) -> None:
        await set_config_for(['fortnite', 'accept_friend_for'], command, message)

    @command(
        name='whisper_enable_for',
        usage='{name} [{client.l("user_types", **client.variables_without_self)}]'
    )
    async def whisper_enable_for(command: Command, client: 'Client', message: MyMessage) -> None:
        await set_config_for(['fortnite', 'whisper_enable_for'], command, message)

    @command(
        name='party_chat_enable_for',
        usage='{name} [{client.l("user_types", **client.variables_without_self)}]'
    )
    async def party_chat_enable_for(command: Command, client: 'Client', message: MyMessage) -> None:
        await set_config_for(['fortnite', 'party_chat_enable_for'], command, message)

    @command(
        name='permission_command_operation',
        usage='{name} [{client.l("operations", **client.variables_without_self)}]'
    )
    async def permission_command_operation(command: Command, client: 'Client', message: MyMessage) -> None:
        await set_config_operation(['fortnite', 'permission_command_operation'], command, message)

    @command(
        name='accept_join_for',
        usage='{name} [{client.l("user_types", **client.variables_without_self)}]'
    )
    async def accept_join_for(command: Command, client: 'Client', message: MyMessage) -> None:
        await set_config_for(['fortnite', 'accept_join_for'], command, message)

    @command(
        name='chat_max_for',
        usage='{name} [{client.l("user_types", **client.variables_without_self)}]'
    )
    async def chat_max_for(command: Command, client: 'Client', message: MyMessage) -> None:
        await set_config_for(['fortnite', 'chat_max_for'], command, message)

    @command(
        name='chat_max_operation',
        usage='{name} [{client.l("operations", **client.variables_without_self)}]'
    )
    async def chat_max_operation(command: Command, client: 'Client', message: MyMessage) -> None:
        await set_config_operation(['fortnite', 'chat_max_operation'], command, message)

    @command(
        name='hide_for',
        usage='{name} [{client.l("user_types", **client.variables_without_self)}]'
    )
    async def hide_for(command: Command, client: 'Client', message: MyMessage) -> None:
        await set_config_for(['fortnite', 'hide_for'], command, message)

    @command(
        name='blacklist_operation',
        usage='{name} [{client.l("operations", **client.variables_without_self)}]'
    )
    async def blacklist_operation(command: Command, client: 'Client', message: MyMessage) -> None:
        await set_config_operation(['fortnite', 'blacklist_operation'], command, message)

    @command(
        name='botlist_operation',
        usage='{name} [{client.l("operations", **client.variables_without_self)}]'
    )
    async def botlist_operation(command: Command, client: 'Client', message: MyMessage) -> None:
        await set_config_operation(['fortnite', 'botlist_operation'], command, message)

    @command(
        name='discord_chat_max_for',
        usage='{name} [{client.l("user_types", **client.variables_without_self)}]'
    )
    async def discord_chat_max_for(command: Command, client: 'Client', message: MyMessage) -> None:
        await set_config_for(['fortnite', 'discord_chat_max_for'], command, message)

    @command(
        name='discord_command_enable_for',
        usage='{name} [{client.l("user_types", **client.variables_without_self)}]'
    )
    async def discord_command_enable_for(command: Command, client: 'Client', message: MyMessage) -> None:
        await set_config_for(['fortnite', 'discord_command_enable_for'], command, message)

    @command(
        name='ng_word_for',
        usage='{name} [{client.l("user_types", **client.variables_without_self)}]'
    )
    async def ng_word_for(command: Command, client: 'Client', message: MyMessage) -> None:
        await set_config_for(['ng_word_for'], command, message)

    @command(
        name='ng_word_operation',
        usage='{name} [{client.l("operations", **client.variables_without_self)}]'
    )
    async def ng_word_operation(command: Command, client: 'Client', message: MyMessage) -> None:
        await set_config_operation(['fortnite', 'ng_word_operation'], command, message)

    @command(
        name='get_user',
        usage='{name} [{client.l("name_or_id")}]'
    )
    async def get_user(command: Command, client: 'Client', message: MyMessage) -> None:
        if len(message.args) < 2:
            await client.show_help(command, message)
            return

        users = client.find_users(
            ' '.join(message.args[1:]),
            mode=FindUserMode.NAME_ID,
            method=FindUserMatchMethod.CONTAINS,
            me=message.author
        )
        user = await client.fetch_user(' '.join(message.args[1:]), cache=True)
        if user is not None:
            users.append(user)

        if client.config['search_max'] and len(users) > client.config['search_max']:
            await message.reply(
                client.l('too_many', client.l('user'), len(users))
            )
            return

        if len(users) == 0:
            await message.reply(
                client.l(
                    'not_found',
                    client.l('user'),
                    ' '.join(message.args[1:])
                )
            )
        else:
            text = '\n'.join([client.name(user) for user in users])
            client.send(text)
            await message.reply(text)

    @command(
        name='get_friend',
        usage='{name} [{client.l("name_or_id")}]'
    )
    async def get_friend(command: Command, client: 'Client', message: MyMessage) -> None:
        if len(message.args) < 2:
            await client.show_help(command, message)
            return

        users = client.find_users(
            ' '.join(message.args[1:]),
            mode=FindUserMode.NAME_ID,
            method=FindUserMatchMethod.CONTAINS,
            users=client.friends,
            me=message.author
        )

        if client.config['search_max'] and len(users) > client.config['search_max']:
            await message.reply(
                client.l('too_many', client.l('user'), len(users))
            )
            return

        if len(users) == 0:
            await message.reply(
                client.l(
                    'not_found',
                    client.l('user'),
                    ' '.join(message.args[1:])
                )
            )
        else:
            text = ''
            for user in users:
                friend = client.get_friend(user.id)
                if friend is None:
                    continue

                text += (
                    f'{client.name(friend)}: '
                    f'{client.l("online") if friend.is_online() else client.l("offline")}\n'
                )
                if friend.last_presence:
                    text += client.l(
                        'status_info',
                        friend.last_presence.status
                    ) + '\n'
                    if friend.last_presence.avatar:
                        text += client.l(
                            'avatar_info',
                            friend.last_presence.avatar.asset
                        ) + '\n'
                if friend.last_logout:
                    text += client.l(
                        'last_logout_info',
                        friend.last_logout
                    ) + '\n'
            client.send(text)
            await message.reply(text)

    @command(
        name='get_pending',
        usage='{name} [{client.l("name_or_id")}]'
    )
    async def get_pending(command: Command, client: 'Client', message: MyMessage) -> None:
        if len(message.args) < 2:
            await client.show_help(command, message)
            return

        users = client.find_users(
            ' '.join(message.args[1:]),
            mode=FindUserMode.NAME_ID,
            method=FindUserMatchMethod.CONTAINS,
            users=client.pending_friends,
            me=message.author
        )

        if client.config['search_max'] and len(users) > client.config['search_max']:
            await message.reply(
                client.l('too_many', client.l('user'), len(users))
            )
            return

        if len(users) == 0:
            await message.reply(
                client.l(
                    'not_found',
                    client.l('user'),
                    ' '.join(message.args[1:])
                )
            )
        else:
            text = ''

            outgoings = [user for user in users if client.is_outgoing_pending(user.id)]
            text += client.l('outgoing_pending') + '\n'
            text += '\n'.join([client.name(outgoing) for outgoing in outgoings])

            incomings = [user for user in users if client.is_incoming_pending(user.id)]
            text += client.l('incoming_pending') + '\n'
            text += '\n'.join([client.name(incoming) for incoming in incomings])

            client.send(text)
            await message.reply(text)

    @command(
        name='get_block',
        usage='{name} [{client.l("name_or_id")}]'
    )
    async def get_block(command: Command, client: 'Client', message: MyMessage) -> None:
        if len(message.args) < 2:
            await client.show_help(command, message)
            return

        users = client.find_users(
            ' '.join(message.args[1:]),
            mode=FindUserMode.NAME_ID,
            method=FindUserMatchMethod.CONTAINS,
            users=client.blocked_users,
            me=message.author
        )

        if client.config['search_max'] and len(users) > client.config['search_max']:
            await message.reply(
                client.l('too_many', client.l('user'), len(users))
            )
            return

        if len(users) == 0:
            await message.reply(
                client.l(
                    'not_found',
                    client.l('user'),
                    ' '.join(message.args[1:])
                )
            )
        else:
            text = '\n'.join([client.name(user) for user in users])
            client.send(text)
            await message.reply(text)

    @command(
        name='get_member',
        usage='{name} [{client.l("name_or_id)}]'
    )
    async def get_member(command: Command, client: 'Client', message: MyMessage) -> None:
        if len(message.args) < 2:
            await client.show_help(command, message)
            return

        users = client.find_users(
            ' '.join(message.args[1:]),
            mode=FindUserMode.NAME_ID,
            method=FindUserMatchMethod.CONTAINS,
            users=client.party.members,
            me=message.author
        )

        async def get_member(user):
            member = client.party.get_member(user.id)
            if member is None:
                await message.reply(
                    client.l(
                        'not_found',
                        client.l('party_member'),
                        client.name(user)
                    )
                )
                return

            text = (f'{client.name(member)}\n'
                    f'CID: {client.asset("AthenaCharacter", member)} {member.outfit_variants}\n'
                    f'BID: {client.asset("AthenaBackpack", member)} {member.backpack_variants}\n'
                    f'Pickaxe_ID: {client.asset("AthenaPickaxe", member)} {member.pickaxe_variants}\n'
                    f'EID: {client.asset("AthenaDance", member)}\n')
            client.send(text)
            if client.config['loglevel'] == 'debug':
                client.send(
                    json.dumps(member.meta.schema, indent=4, ensure_ascii=False),
                    color=yellow,
                    add_p=client.time,
                    add_d=client.debug_message
                )
            await message.reply(text)

        if client.config['search_max'] and len(users) > client.config['search_max']:
            await message.reply(
                client.l('too_many', client.l('user'), len(users))
            )
            return

        if len(users) == 0:
            await message.reply(
                client.l(
                    'not_found',
                    client.l('user'),
                    ' '.join(message.args[1:])
                )
            )
        elif len(users) == 1:
            await get_member(users[0])
        else:
            client.select[message.author.id] = {
                'exec': 'await get_member(user)',
                'globals': {**globals(), **locals()},
                'variables': [
                    {'user': user}
                    for user in users
                ]
            }
            await message.reply(
                ('\n'.join([f'{num}: {client.name(user)}'
                            for num, user in enumerate(users, 1)])
                    + '\n' + client.l('enter_number_to_select', client.l('user')))
            )

    @command(
        name='party_info',
        usage='{name}'
    )
    async def party_info(command: Command, client: 'Client', message: MyMessage) -> None:
        if client.config['loglevel'] == 'debug':
            client.send(
                json.dumps(client.party.meta.schema, indent=4, ensure_ascii=False),
                color=yellow,
                add_p=client.time,
                add_d=client.debug_message
            )
        await message.reply(
            client.l(
                'party_info',
                client.party_id,
                client.party.member_count,
                client.party.playlist_info[0],
                '\n'.join([client.name(member) for member in client.party.members])
            )
        )

    @command(
        name='friend_count',
        usage='{name}'
    )
    async def friend_count(command: Command, client: 'Client', message: MyMessage) -> None:
        await message.reply(
            client.l('friend_count_info', len(client.friends))
        )

    @command(
        name='pending_count',
        usage='{name}'
    )
    async def pending_count(command: Command, client: 'Client', message: MyMessage) -> None:
        await message.reply(
            client.l(
                'pending_count_info',
                len(client.pending_friends),
                len(client.outgoing_pending_friends),
                len(client.incoming_pending_friends)
            )
        )

    @command(
        name='block_count',
        usage='{name}'
    )
    async def block_count(command: Command, client: 'Client', message: MyMessage) -> None:
        await message.reply(
            client.l('block_count_info', len(client.block_users))
        )

    @command(
        name='friend_list',
        usage='{name}'
    )
    async def friend_list(command: Command, client: 'Client', message: MyMessage) -> None:
        await message.reply(
            client.l(
                'friend_list_info',
                len(client.friends),
                '\n'.join([client.name(user) for user in client.friends])
            )
        )

    @command(
        name='pending_list',
        usage='{name}'
    )
    async def pending_list(command: Command, client: 'Client', message: MyMessage) -> None:
        await message.reply(
            client.l(
                'pending_list_info',
                len(client.outgoing_pending_friends),
                len(client.incoming_pending_friends),
                '\n'.join([client.name(user) for user in client.outgoing_pending_friends]),
                '\n'.join([client.name(user) for user in client.incoming_pending_friends])
            )
        )

    @command(
        name='block_list',
        usage='{name}'
    )
    async def block_list(command: Command, client: 'Client', message: MyMessage) -> None:
        await message.reply(
            client.l(
                'block_list_info',
                len(client.blocked_users),
                '\n'.join([client.name(user) for user in client.blocked_users])
            )
        )

    @command(
        name='add_friend',
        usage='{name} [{client.l("name_or_id")}]'
    )
    async def add_friend(command: Command, client: 'Client', message: MyMessage) -> None:
        if len(message.args) < 2:
            await client.show_help(command, message)
            return

        users = client.find_users(
            ' '.join(message.args[1:]),
            mode=FindUserMode.NAME_ID,
            method=FindUserMatchMethod.CONTAINS,
            me=message.author
        )
        user = await client.fetch_user(' '.join(message.args[1:]), cache=True)
        if user is not None and user not in users:
            users.append(user)

        async def add_friend(user):
            if client.has_friend(user.id):
                await message.reply(
                    client.l(
                        'already_friend_with_user',
                        client.name(user)
                    )
                )
                return

            ret = await client.send_friend_request(user, message)
            if not isinstance(ret, Exception):
                await message.reply(
                    client.l(
                        'add_friend',
                        client.name(user)
                    )
                )

        if client.config['search_max'] and len(users) > client.config['search_max']:
            await message.reply(
                client.l('too_many', client.l('user'), len(users))
            )
            return

        if len(users) == 0:
            await message.reply(
                client.l(
                    'not_found',
                    client.l('user'),
                    ' '.join(message.args[1:])
                )
            )
        elif len(users) == 1:
            await add_friend(users[0])
        else:
            client.select[message.author.id] = {
                'exec': 'await add_friend(user)',
                'globals': {**globals(), **locals()},
                'variables': [
                    {'user': user}
                    for user in users
                ]
            }
            await message.reply(
                ('\n'.join([f'{num}: {client.name(user)}'
                            for num, user in enumerate(users, 1)])
                    + '\n' + client.l('enter_number_to_select', client.l('user')))
            )

    @command(
        name='remove_friend',
        usage='{name} [{client.l("name_or_id")}]'
    )
    async def remove_friend(command: Command, client: 'Client', message: MyMessage) -> None:
        if len(message.args) < 2:
            await client.show_help(command, message)
            return

        users = client.find_users(
            ' '.join(message.args[1:]),
            mode=FindUserMode.NAME_ID,
            method=FindUserMatchMethod.CONTAINS,
            users=client.friends,
            me=message.author
        )

        async def remove_friend(user):
            friend = client.get_friend(user.id)
            if friend is None:
                await message.reply(
                    client.l(
                        'not_friend_with_user',
                        client.name(user)
                    )
                )
                return

            ret = await client.remove_friend(friend, message)
            if not isinstance(ret, Exception):
                await message.reply(
                    client.l(
                        'remove_friend',
                        client.name(friend)
                    )
                )

        if client.config['search_max'] and len(users) > client.config['search_max']:
            await message.reply(
                client.l('too_many', client.l('user'), len(users))
            )
            return

        if len(users) == 0:
            await message.reply(
                client.l(
                    'not_found',
                    client.l('user'),
                    ' '.join(message.args[1:])
                )
            )
        elif len(users) == 1:
            await remove_friend(users[0])
        else:
            client.select[message.author.id] = {
                'exec': 'await remove_friend(user)',
                'globals': {**globals(), **locals()},
                'variables': [
                    {'user': user}
                    for user in users
                ]
            }
            await message.reply(
                ('\n'.join([f'{num}: {client.name(user)}'
                            for num, user in enumerate(users, 1)])
                    + '\n' + client.l('enter_number_to_select', client.l('user')))
            )

    @command(
        name='remove_friends',
        usage='{name} [{client.l("number")}]'
    )
    async def remove_friends(command: Command, client: 'Client', message: MyMessage) -> None:
        if len(message.args) < 2:
            await client.show_help(command, message)
            return

        try:
            number = int(message.args[1])
        except ValueError as e:
            client.debug_print_exception(e)
            await message.reply(
                client.l('please_enter_valid_number')
            )
            return

        random_friends = random.sample(client.friends, k=number)

        async def remove_friends():
            friend_count_before = len(client.friends)
            for friend in random_friends:
                await client.remove_friend(friend, message)
            friend_count_after = len(client.friends)
            await message.reply(
                client.l(
                    'remove_friends',
                    friend_count_before - friend_count_after
                )
            )

        task = client.loop.create_task(remove_friends())
        client.stoppable_tasks.append(task)

    @command(
        name='remove_all_friend',
        usage='{name}'
    )
    async def remove_all_friend(command: Command, client: 'Client', message: MyMessage) -> None:
        async def remove_all_friend():
            friend_count_before = len(client.friends)
            for friend in client.friends:
                await client.remove_friend(friend, message)
            friend_count_after = len(client.friends)
            await message.reply(
                client.l(
                    'remove_friends',
                    friend_count_before - friend_count_after
                )
            )

        task = client.loop.create_task(remove_all_friend())
        client.stoppable_tasks.append(task)

    @command(
        name='remove_offline_for',
        usage='{name} [{client.l("day")}] ({client.l("hour")}) ({client.l("minute")})'
    )
    async def remove_offline_for(command: Command, client: 'Client', message: MyMessage) -> None:
        if len(message.args) < 2:
            await client.show_help(command, message)
            return

        kwargs = {
            'days': int(message.args[1]),
            'hours': int(client.bot.get_list_index(message.args, 2, 0)),
            'minutes': int(client.bot.get_list_index(message.args, 3, 0))
        }
        offline_for = datetime.timedelta(**kwargs)
        utcnow = datetime.datetime.utcnow()
        friend_count_before = len(client.friends)

        async def remove_offline_for():
            for friend in client.friends:
                last_logout = None
                if friend.last_logout is not None:
                    last_logout = friend.last_logout
                if friend.last_logout is None or (friend.created_at > client.booted_at):
                    last_logout = await friend.fetch_last_logout()

                if last_logout is not None and ((utcnow - last_logout) >= offline_for):
                    await client.remove_friend(friend, message)

            friend_count_after = len(client.friends)
            await message.reply(
                client.l(
                    'remove_friends',
                    friend_count_before - friend_count_after
                )
            )

        task = client.loop.create_task(remove_offline_for())
        client.stoppable_tasks.append(task)

    @command(
        name='accept_pending',
        usage='{name} [{client.l("name_or_id")}]'
    )
    async def accept_pending(command: Command, client: 'Client', message: MyMessage) -> None:
        if len(message.args) < 2:
            await client.show_help(command, message)
            return

        users = client.find_users(
            ' '.join(message.args[1:]),
            mode=FindUserMode.NAME_ID,
            method=FindUserMatchMethod.CONTAINS,
            users=client.incoming_pending_friends,
            me=message.author
        )

        async def accept_pending(user):
            ret = await client.accept_request(user, message)
            if not isinstance(ret, Exception):
                await message.reply(
                    client.l(
                        'accept_pending',
                        client.name(user)
                    )
                )

        if client.config['search_max'] and len(users) > client.config['search_max']:
            await message.reply(
                client.l('too_many', client.l('user'), len(users))
            )
            return

        if len(users) == 0:
            await message.reply(
                client.l(
                    'not_found',
                    client.l('user'),
                    ' '.join(message.args[1:])
                )
            )
        elif len(users) == 1:
            await accept_pending(users[0])
        else:
            client.select[message.author.id] = {
                'exec': 'await accept_pending(user)',
                'globals': {**globals(), **locals()},
                'variables': [
                    {'user': user}
                    for user in users
                ]
            }
            await message.reply(
                ('\n'.join([f'{num}: {client.name(user)}'
                            for num, user in enumerate(users, 1)])
                    + '\n' + client.l('enter_number_to_select', client.l('user')))
            )

    @command(
        name='decline_pending',
        usage='{name} [{client.l("name_or_id")}]'
    )
    async def decline_pending(command: Command, client: 'Client', message: MyMessage) -> None:
        if len(message.args) < 2:
            await client.show_help(command, message)
            return

        users = client.find_users(
            ' '.join(message.args[1:]),
            mode=FindUserMode.NAME_ID,
            method=FindUserMatchMethod.CONTAINS,
            users=client.incoming_pending_friends,
            me=message.author
        )

        async def decline_pending(user):
            ret = await client.decline_request(user, message)
            if not isinstance(ret, Exception):
                await message.reply(
                    client.l(
                        'decline_pending',
                        client.name(user)
                    )
                )

        if client.config['search_max'] and len(users) > client.config['search_max']:
            await message.reply(
                client.l('too_many', client.l('user'), len(users))
            )
            return

        if len(users) == 0:
            await message.reply(
                client.l(
                    'not_found',
                    client.l('user'),
                    ' '.join(message.args[1:])
                )
            )
        elif len(users) == 1:
            await decline_pending(users[0])
        else:
            client.select[message.author.id] = {
                'exec': 'await decline_pending(user)',
                'globals': {**globals(), **locals()},
                'variables': [
                    {'user': user}
                    for user in users
                ]
            }
            await message.reply(
                ('\n'.join([f'{num}: {client.name(user)}'
                            for num, user in enumerate(users, 1)])
                    + '\n' + client.l('enter_number_to_select', client.l('user')))
            )

    @command(
        name='incoming_pending',
        usage='{name} [{client.commands[accept]}/{client.commands[decline]}]'
    )
    async def incoming_pending(command: Command, client: 'Client', message: MyMessage) -> None:
        if len(message.args) < 2:
            await client.show_help(command, message)
            return

        count_before = len(client.incoming_pending_friends)
        if message.args[1] in client.commands['accept']:
            async def incoming_pending():
                for pending in client.incoming_pending_friends:
                    await client.accept_request(pending, message)
                count_after = len(client.incoming_pending_friends)
                await message.reply(
                    client.l(
                        'accept_pendings',
                        count_before - count_after
                    )
                )

            task = client.loop.create_task(incoming_pending())
            client.stoppable_tasks.append(task)
        elif message.args[1] in client.commands['decline']:
            async def incoming_pending():
                for pending in client.incoming_pending_friends:
                    await client.decline_request(pending, message)
                count_after = len(client.incoming_pending_friends)
                await message.reply(
                    client.l(
                        'decline_pendings',
                        count_before - count_after
                    )
                )

            task = client.loop.create_task(incoming_pending())
            client.stoppable_tasks.append(task)
        else:
            await client.show_help(command, message)

    @command(
        name='cancel_outgoing_pending',
        usage='{name}'
    )
    async def cancel_outgoing_pending(command: Command, client: 'Client', message: MyMessage) -> None:
        async def cancel_outgoing_pending():
            count_before = len(client.outgoing_pending_friends)
            for pending in client.outgoing_pending_friends:
                await client.decline_request(pending, message)
            count_after = len(client.outgoing_pending_friends)
            await message.reply(
                client.l(
                    'remove_pendings',
                    count_before - count_after
                )
            )

        task = client.loop.create_task(cancel_outgoing_pending())
        client.stoppable_tasks.append(task)

    @command(
        name='block_user',
        usage='{name} [{client.l("name_or_id")}]'
    )
    async def block_user(command: Command, client: 'Client', message: MyMessage) -> None:
        if len(message.args) < 2:
            await client.show_help(command, message)
            return

        users = client.find_users(
            ' '.join(message.args[1:]),
            mode=FindUserMode.NAME_ID,
            method=FindUserMatchMethod.CONTAINS,
            me=message.author
        )
        user = await client.fetch_user(' '.join(message.args[1:]), cache=True)
        if user is not None and user not in users:
            users.append(user)

        async def block_user(user):
            if client.is_blocked(user.id):
                await message.reply(
                    client.l(
                        'already_blocked',
                        client.name(user)
                    )
                )

            ret = await client.user_block(user, message)
            if not isinstance(ret, Exception):
                await message.reply(
                    client.l(
                        'block_user',
                        client.name(user)
                    )
                )

        if client.config['search_max'] and len(users) > client.config['search_max']:
            await message.reply(
                client.l('too_many', client.l('user'), len(users))
            )
            return

        if len(users) == 0:
            await message.reply(
                client.l(
                    'not_found',
                    client.l('user'),
                    ' '.join(message.args[1:])
                )
            )
        elif len(users) == 1:
            await block_user(users[0])
        else:
            client.select[message.author.id] = {
                'exec': 'await block_user(user)',
                'globals': {**globals(), **locals()},
                'variables': [
                    {'user': user}
                    for user in users
                ]
            }
            await message.reply(
                ('\n'.join([f'{num}: {client.name(user)}'
                            for num, user in enumerate(users, 1)])
                    + '\n' + client.l('enter_number_to_select', client.l('user')))
            )

    @command(
        name='unblock_user',
        usage='{name} [{client.l("name_or_id")}]'
    )
    async def unblock_user(command: Command, client: 'Client', message: MyMessage) -> None:
        if len(message.args) < 2:
            await client.show_help(command, message)
            return

        users = client.find_users(
            ' '.join(message.args[1:]),
            mode=FindUserMode.NAME_ID,
            method=FindUserMatchMethod.CONTAINS,
            users=client.blocked_users,
            me=message.author
        )

        async def unblock_user(user):
            blocked_user = client.get_blocked_user(user.id)
            if blocked_user is None:
                await message.reply(
                    client.l(
                        'not_blocking_user',
                        client.name(user)
                    )
                )

            ret = await client.user_unblock(blocked_user, message)
            if not isinstance(ret, Exception):
                await message.reply(
                    client.l(
                        'unblock_user',
                        client.name(blocked_user)
                    )
                )

        if client.config['search_max'] and len(users) > client.config['search_max']:
            await message.reply(
                client.l('too_many', client.l('user'), len(users))
            )
            return

        if len(users) == 0:
            await message.reply(
                client.l(
                    'not_found',
                    client.l('user'),
                    ' '.join(message.args[1:])
                )
            )
        elif len(users) == 1:
            await unblock_user(users[0])
        else:
            client.select[message.author.id] = {
                'exec': 'await unblock_user(user)',
                'globals': {**globals(), **locals()},
                'variables': [
                    {'user': user}
                    for user in users
                ]
            }
            await message.reply(
                ('\n'.join([f'{num}: {client.name(user)}'
                            for num, user in enumerate(users, 1)])
                    + '\n' + client.l('enter_number_to_select', client.l('user')))
            )

    @command(
        name='unblock_all_user',
        usage='{name}'
    )
    async def unblock_all_user(command: Command, client: 'Client', message: MyMessage) -> None:
        async def unblock_all_user():
            block_count_before = len(client.blocked_users)
            for blocked_user in client.blocked_users:
                await client.unblock_user(blocked_user)
            block_count_after = len(client.blocked_users)
            await message.reply(
                client.l(
                    'unblock_users',
                    block_count_before - block_count_after
                )
            )

        task = client.loop.create_task(unblock_all_user())
        client.stoppable_tasks.append(task)

    @command(
        name='join',
        usage='{name} [{client.l("name_or_id")}]'
    )
    async def join(command: Command, client: 'Client', message: MyMessage) -> None:
        if len(message.args) < 2:
            await client.show_help(command, message)
            return

        users = client.find_users(
            ' '.join(message.args[1:]),
            mode=FindUserMode.NAME_ID,
            method=FindUserMatchMethod.CONTAINS,
            users=client.friends,
            me=message.author
        )

        async def join(user):
            friend = client.get_friend(user.id)
            if friend is None:
                await message.reply(
                    client.l(
                        'not_friend_with_user',
                        client.name(user)
                    )
                )
                return

            ret = await client.join_party_friend(friend, message)
            if not isinstance(ret, Exception):
                if client.config['loglevel'] == 'normal':
                    await message.reply(
                        client.l(
                            'party_join_friend',
                            client.name(friend)
                        )
                    )
                else:
                    await message.reply(
                        client.l(
                            'party_join_friend_info',
                            client.name(friend),
                            ret.id
                        )
                    )

        if client.config['search_max'] and len(users) > client.config['search_max']:
            await message.reply(
                client.l('too_many', client.l('user'), len(users))
            )
            return

        if len(users) == 0:
            await message.reply(
                client.l(
                    'not_found',
                    client.l('user'),
                    ' '.join(message.args[1:])
                )
            )
        elif len(users) == 1:
            await join(users[0])
        else:
            client.select[message.author.id] = {
                'exec': 'await join(user)',
                'globals': {**globals(), **locals()},
                'variables': [
                    {'user': user}
                    for user in users
                ]
            }
            await message.reply(
                ('\n'.join([f'{num}: {client.name(user)}'
                            for num, user in enumerate(users, 1)])
                    + '\n' + client.l('enter_number_to_select', client.l('user')))
            )

    @command(
        name='join_id',
        usage='{name} [{client.l("party_id")}]'
    )
    async def join_id(command: Command, client: 'Client', message: MyMessage) -> None:
        if len(message.args) < 2:
            await client.show_help(command, message)
            return

        ret = await client.join_party_id(message.args[1], message)
        if not isinstance(ret, Exception):
            if client.config['loglevel'] == 'normal':
                await message.reply(
                    client.l('party_join')
                )
            else:
                await message.reply(
                    client.l(
                        'party_join_info',
                        ret.id
                    )
                )

    @command(
        name='request_to_join',
        usage='{name} [{client.l("name_or_id")}]'
    )
    async def request_to_join(command: Command, client: 'Client', message: MyMessage) -> None:
        if len(message.args) < 2:
            await client.show_help(command, message)
            return

        users = client.find_users(
            ' '.join(message.args[1:]),
            mode=FindUserMode.NAME_ID,
            method=FindUserMatchMethod.CONTAINS,
            users=client.friends,
            me=message.author
        )

        async def request_to_join(user):
            friend = client.get_friend(user.id)
            if friend is None:
                await message.reply(
                    client.l(
                        'not_friend_with_user',
                        client.name(user)
                    )
                )
                return
            
            ret = await client.send_join_request(friend, message)
            if not isinstance(ret, Exception):
                if client.config['loglevel'] == 'normal':
                    await message.reply(
                        client.l(
                            'join_request_sent',
                            client.name(friend)
                        )
                    )

        if client.config['search_max'] and len(users) > client.config['search_max']:
            await message.reply(
                client.l('too_many', client.l('user'), len(users))
            )
            return

        if len(users) == 0:
            await message.reply(
                client.l(
                    'not_found',
                    client.l('user'),
                    ' '.join(message.args[1:])
                )
            )
        elif len(users) == 1:
            await request_to_join(users[0])
        else:
            client.select[message.author.id] = {
                'exec': 'await request_to_join(user)',
                'globals': {**globals(), **locals()},
                'variables': [
                    {'user': user}
                    for user in users
                ]
            }
            await message.reply(
                ('\n'.join([f'{num}: {client.name(user)}'
                            for num, user in enumerate(users, 1)])
                    + '\n' + client.l('enter_number_to_select', client.l('user')))
            )

    @command(
        name='leave',
        usage='{name}'
    )
    async def leave(command: Command, client: 'Client', message: MyMessage) -> None:
        await client.party.me.leave()
        if client.config['loglevel'] == 'normal':
            await message.reply(
                client.l('party_leave')
            )
        else:
            await message.reply(
                client.l(
                    'party_leave_info',
                    client.party.id
                )
            )

    @command(
        name='invite',
        usage='{name} [{client.l("name_or_id")}]'
    )
    async def invite(command: Command, client: 'Client', message: MyMessage) -> None:
        if len(message.args) < 2:
            await client.show_help(command, message)
            return

        users = client.find_users(
            ' '.join(message.args[1:]),
            mode=FindUserMode.NAME_ID,
            method=FindUserMatchMethod.CONTAINS,
            users=client.friends,
            me=message.author
        )

        async def invite(user):
            friend = client.get_friend(user.id)
            if friend is None:
                await message.reply(
                    client.l(
                        'not_friend_with_user',
                        client.name(user)
                    )
                )
                return

            ret = await client.invite_friend(friend, message)
            if not isinstance(ret, Exception):
                if client.config['loglevel'] == 'normal':
                    await message.reply(
                        client.l(
                            'user_invite',
                            client.name(friend)
                        )
                    )
                else:
                    await message.reply(
                        client.l(
                            'user_invite_info',
                            client.name(friend),
                            client.party.id
                        )
                    )

        if client.config['search_max'] and len(users) > client.config['search_max']:
            await message.reply(
                client.l('too_many', client.l('user'), len(users))
            )
            return

        if len(users) == 0:
            await message.reply(
                client.l(
                    'not_found',
                    client.l('user'),
                    ' '.join(message.args[1:])
                )
            )
        elif len(users) == 1:
            await invite(users[0])
        else:
            client.select[message.author.id] = {
                'exec': 'await invite(user)',
                'globals': {**globals(), **locals()},
                'variables': [
                    {'user': user}
                    for user in users
                ]
            }
            await message.reply(
                ('\n'.join([f'{num}: {client.name(user)}'
                            for num, user in enumerate(users, 1)])
                    + '\n' + client.l('enter_number_to_select', client.l('user')))
            )

    @command(
        name='invite_list_users',
        usage='{name}'
    )
    async def invite_list_users(command: Command, client: 'Client', message: MyMessage) -> None:
        users = [user for user in client.invitelist
                 if isinstance(user, fortnitepy.Friend)]
        if len(users) == 0:
            return

        tasks = [
            client.loop.create_task(client.invite_friend(user, message))
            for user in users
        ]
        await asyncio.wait(
            tasks,
            return_when=asyncio.ALL_COMPLETED
        )
        if client.config['loglevel'] == 'normal':
            await message.reply(
                client.l('invitelist_invite')
            )
        else:
            await message.reply(
                client.l(
                    'invitelist_invite_info',
                    client.party.id
                )
            )

    @command(
        name='message',
        usage='{name} [{client.l("name_or_id")}] : [{client.l("message")}]'
    )
    async def message(command: Command, client: 'Client', message: MyMessage) -> None:
        if len(message.args) < 2:
            await client.show_help(command, message)
            return

        text = ' '.join(message.args[1:]).split(' : ')
        if len(text) < 2:
            await client.show_help(command, message)
            return

        user_name, content = text

        users = client.find_users(
            user_name,
            mode=FindUserMode.NAME_ID,
            method=FindUserMatchMethod.CONTAINS,
            users=client.friends,
            me=message.author
        )

        async def send_message(user):
            friend = client.get_friend(user.id)
            if friend is None:
                await message.reply(
                    client.l(
                        'not_friend_with_user',
                        client.name(user)
                    )
                )
                return

            await friend.send(content)
            await message.reply(
                client.l(
                    'sent_message',
                    client.name(friend),
                    content
                )
            )

        if client.config['search_max'] and len(users) > client.config['search_max']:
            await message.reply(
                client.l('too_many', client.l('user'), len(users))
            )
            return

        if len(users) == 0:
            await message.reply(
                client.l(
                    'not_found',
                    client.l('user'),
                    user_name
                )
            )
        elif len(users) == 1:
            await send_message(users[0])
        else:
            client.select[message.author.id] = {
                'exec': 'await send_message(user)',
                'globals': {**globals(), **locals()},
                'variables': [
                    {'user': user}
                    for user in users
                ]
            }
            await message.reply(
                ('\n'.join([f'{num}: {client.name(user)}'
                            for num, user in enumerate(users, 1)])
                    + '\n' + client.l('enter_number_to_select', client.l('user')))
            )

    @command(
        name='party_message',
        usage='{name} [{client.l("message")}]'
    )
    async def party_message(command: Command, client: 'Client', message: MyMessage) -> None:
        if len(message.args) < 2:
            await client.show_help(command, message)
            return

        await client.party.send(
            ' '.join(message.args[1:])
        )
        if client.config['loglevel'] == 'normal':
            await message.reply(
                client.l(
                    'sent_party_message',
                    ' '.join(message.args[1:])
                )
            )
        else:
            await message.reply(
                client.l(
                    'sent_party_message_info',
                    ' '.join(message.args[1:]),
                    client.party.id
                )
            )

    @command(
        name='avatar',
        usage='{name} [ID] ({client.l("color")})'
    )
    async def avatar(command: Command, client: 'Client', message: MyMessage) -> None:
        if len(message.args) < 2:
            await client.show_help(command, message)
            return

        if len(message.args) >= 5:
            background_colors = message.args[2:4]
        elif len(message.args) == 2:
            background_colors = None
        else:
            try:
                background_colors = getattr(
                    fortnitepy.KairosBackgroundColorPreset,
                    message.args[2].upper()
                )
            except AttributeError as e:
                client.debug_print_exception(e)
                await message.reply(
                    client.l(
                        'must_be_one_of',
                        client.l('color'),
                        [i.name for i in fortnitepy.KairosBackgroundColorPreset]
                    )
                )
                return

        avatar = fortnitepy.Avatar(
            asset=message.args[1],
            background_colors=background_colors
        )
        client.set_avatar(avatar)
        await message.reply(
            client.l(
                'set_to',
                client.l('avatar'),
                f'{message.args[1]}, {background_colors}'
            )
        )

    @command(
        name='status',
        usage='{name} [{client.l("message")}]'
    )
    async def status(command: Command, client: 'Client', message: MyMessage) -> None:
        await client.set_presence(' '.join(message.args[1:]))
        await message.reply(
            client.l(
                'set_to',
                client.l('status'),
                ' '.join(message.args[1:])
            )
        )

    @command(
        name='banner',
        usage='{name} [ID] [{client.l("color")}]'
    )
    async def banner(command: Command, client: 'Client', message: MyMessage) -> None:
        if len(message.args) < 3:
            await client.show_help(command, message)
            return

        await client.party.me.edit_and_keep(partial(
            client.party.me.set_banner,
            icon=message.args[1],
            color=message.args[2],
            season_level=client.party.me.banner[2]
        ))
        await message.reply(
            client.l(
                'set_to',
                client.l('banner'),
                f'{message.args[1]}, {message.args[2]}'
            )
        )

    @command(
        name='level',
        usage='{name} [{client.l("number")}]'
    )
    async def level(command: Command, client: 'Client', message: MyMessage) -> None:
        if len(message.args) < 2:
            await client.show_help(command, message)
            return

        icon, color = client.party.me.banner[:2]
        try:
            level = int(message.args[1])
        except ValueError as e:
            client.debug_print_exception(e)
            await message.reply(
                client.l('please_enter_valid_value')
            )
            return
        await client.party.me.edit_and_keep(partial(
            client.party.me.set_banner,
            icon=icon,
            color=color,
            season_level=level
        ))
        await message.reply(
            client.l(
                'set_to',
                client.l('level'),
                level
            )
        )

    @command(
        name='battlepass',
        usage='{name} [{client.l("number")}]'
    )    
    async def battlepass(command: Command, client: 'Client', message: MyMessage) -> None:
        if len(message.args) < 2:
            await client.show_help(command, message)
            return

        try:
            tier = int(message.args[1])
        except ValueError as e:
            client.debug_print_exception(e)
            await message.reply(
                client.l('please_enter_valid_value')
            )
            return
        await client.party.me.edit_and_keep(partial(
            client.party.me.set_battlepass_info,
            has_purchased=True,
            level=tier
        ))
        await message.reply(
            client.l(
                'set_to',
                client.l('tier'),
                tier
            )
        )

    @command(
        name='privacy',
        usage='{name} [{client.l("privacy")}]'
    )
    async def privacy(command: Command, client: 'Client', message: MyMessage) -> None:
        if len(message.args) < 2:
            await client.show_help(command, message)
            return

        if not client.party.me.leader:
            await message.reply(
                client.l('not_a_party_leader')
            )

        privacies = [
            (p.name.lower(), p) for p in PartyPrivacy
        ]
        for p, value in privacies:
            if message.args[1] in client.commands[p]:
                try:
                    await client.party.set_privacy(value)
                except fortnitepy.Forbidden as e:
                    client.debug_print_exception(e)
                    await message.reply(
                        client.l('not_a_party_leader')
                    )
                    return
                await message.reply(
                    client.l(
                        'set_to',
                        client.l('privacy'),
                        client.bot.l(f'privacy_{p}')
                    )
                )
                break
        else:
            await message.reply(
                client.l(
                    'must_be_one_of',
                    client.l('privacy'),
                    [client.commands[p][0] for p in privacies]
                )
            )

    @command(
        name='voice_chat',
        usage=(
            '{name} [{client.l("bool", **self.variables_without_self)}]\n'
            '{client.l("current_setting", client.l("enabled") '
            'if client.party.voice_chat_enabled else '
            'client.l("disabled"))}'
        )
    )
    async def voice_chat(command: Command, client: 'Client', message: MyMessage) -> None:
        if len(message.args) < 2:
            await client.show_help(command, message)
            return

        if not client.party.me.leader:
            await message.reply(
                client.l('not_a_party_leader')
            )
            return

        if message.args[1] in client.commands['true']:
            try:
                await client.party.enable_voice_chat()
            except fortnitepy.Forbidden as e:
                client.debug_print_exception(e)
                await message.reply(
                    client.l('not_a_party_leader')
                )
                return
            await message.reply(
                client.l(
                    'set_to',
                    client.l('voice_chat'),
                    client.l('enabled')
                )
            )
        elif message.args[1] in client.commands['false']:
            try:
                await client.party.disable_voice_chat()
            except fortnitepy.Forbidden as e:
                client.debug_print_exception(e)
                await message.reply(
                    client.l('not_a_party_leader')
                )
                return
            await message.reply(
                client.l(
                    'set_to',
                    client.l('voice_chat'),
                    client.l('disabled')
                )
            )
        else:
            await client.show_help(command, message)

    @command(
        name='promote',
        usage='{name} [{client.l("name_or_id")}]'
    )
    async def promote(command: Command, client: 'Client', message: MyMessage) -> None:
        if len(message.args) < 2:
            await client.show_help(command, message)
            return

        if not client.party.me.leader:
            await message.reply(
                client.l('not_a_party_leader')
            )
            return

        users = client.find_users(
            ' '.join(message.args[1:]),
            mode=FindUserMode.NAME_ID,
            method=FindUserMatchMethod.CONTAINS,
            users=client.party.members,
            me=message.author
        )

        async def promote(user):
            member = client.party.get_member(user.id)
            if member is None:
                await message.reply(
                    client.l(
                        'not_in_party',
                        client.name(user)
                    )
                )
                return

            ret = await client.promote_member(member, message)
            if not isinstance(ret, Exception):
                await message.reply(
                    client.l(
                        'promote',
                        client.name(member)
                    )
                )

        if client.config['search_max'] and len(users) > client.config['search_max']:
            await message.reply(
                client.l('too_many', client.l('user'), len(users))
            )
            return

        if len(users) == 0:
            await message.reply(
                client.l(
                    'not_found',
                    client.l('user'),
                    ' '.join(message.args[1:])
                )
            )
        elif len(users) == 1:
            await promote(users[0])
        else:
            client.select[message.author.id] = {
                'exec': 'await promote(user)',
                'globals': {**globals(), **locals()},
                'variables': [
                    {'user': user}
                    for user in users
                ]
            }
            await message.reply(
                ('\n'.join([f'{num}: {client.name(user)}'
                            for num, user in enumerate(users, 1)])
                    + '\n' + client.l('enter_number_to_select', client.l('user')))
            )

    @command(
        name='kick',
        usage='{name} [{client.l("name_or_id")}]'
    )
    async def kick(command: Command, client: 'Client', message: MyMessage) -> None:
        if len(message.args) < 2:
            await client.show_help(command, message)
            return

        if not client.party.me.leader:
            await message.reply(
                client.l('not_a_party_leader')
            )
            return

        users = client.find_users(
            ' '.join(message.args[1:]),
            mode=FindUserMode.NAME_ID,
            method=FindUserMatchMethod.CONTAINS,
            users=client.party.members,
            me=message.author
        )

        async def kick(user):
            member = client.party.get_member(user.id)
            if member is None:
                await message.reply(
                    client.l(
                        'not_in_party',
                        client.name(user)
                    )
                )
                return

            ret = await client.kick_member(member, message)
            if not isinstance(ret, Exception):
                await message.reply(
                    client.l(
                        'kick',
                        client.name(member)
                    )
                )

        if client.config['search_max'] and len(users) > client.config['search_max']:
            await message.reply(
                client.l('too_many', client.l('user'), len(users))
            )
            return

        if len(users) == 0:
            await message.reply(
                client.l(
                    'not_found',
                    client.l('user'),
                    ' '.join(message.args[1:])
                )
            )
        elif len(users) == 1:
            await kick(users[0])
        else:
            client.select[message.author.id] = {
                'exec': 'await kick(user)',
                'globals': {**globals(), **locals()},
                'variables': [
                    {'user': user}
                    for user in users
                ]
            }
            await message.reply(
                ('\n'.join([f'{num}: {client.name(user)}'
                            for num, user in enumerate(users, 1)])
                    + '\n' + client.l('enter_number_to_select', client.l('user')))
            )

    @command(
        name='chatban',
        usage='{name} [{client.l("name_or_id")}] : ({client.l("reason")})'
    )
    async def chatban(command: Command, client: 'Client', message: MyMessage) -> None:
        if len(message.args) < 2:
            await client.show_help(command, message)
            return

        if not client.party.me.leader:
            await message.reply(
                client.l('not_a_party_leader')
            )
            return

        text = ' '.join(message.args[1:]).split(' : ')

        if len(text) == 1:
            user_name = text[0]
            reason = None
        else:
            user_name, *reason = text
            reason = ' '.join(reason)

        users = client.find_users(
            user_name,
            mode=FindUserMode.NAME_ID,
            method=FindUserMatchMethod.CONTAINS,
            users=client.party.members,
            me=message.author
        )

        async def chatban(user):
            member = client.party.get_member(user.id)
            if member is None:
                await message.reply(
                    client.l(
                        'not_in_party',
                        client.name(user)
                    )
                )
                return

            ret = await client.chatban_member(member, reason, message)
            if not isinstance(ret, Exception):
                if reason is None:
                    await message.reply(
                        client.l(
                            'chatban',
                            client.name(member)
                        )
                    )
                else:
                    await message.reply(
                        client.l(
                            'chatban_reason',
                            client.name(member),
                            reason
                        )
                    )

        if client.config['search_max'] and len(users) > client.config['search_max']:
            await message.reply(
                client.l('too_many', client.l('user'), len(users))
            )
            return

        if len(users) == 0:
            await message.reply(
                client.l(
                    'not_found',
                    client.l('user'),
                    user_name
                )
            )
        elif len(users) == 1:
            await chatban(users[0])
        else:
            client.select[message.author.id] = {
                'exec': 'await chatban(user)',
                'globals': {**globals(), **locals()},
                'variables': [
                    {'user': user}
                    for user in users
                ]
            }
            await message.reply(
                ('\n'.join([f'{num}: {client.name(user)}'
                            for num, user in enumerate(users, 1)])
                    + '\n' + client.l('enter_number_to_select', client.l('user')))
            )

    @command(
        name='hide',
        usage='{name} ({client.l("name_or_id")})'
    )
    async def hide(command: Command, client: 'Client', message: MyMessage) -> None:
        if len(message.args) < 2:
            count = 0
            for member in client.party.members:
                if client.is_hide_for(client.get_user_type(member.id)):
                    if client.party.add_hide_user(member.id):
                        count += 1
            try:
                await client.party.refresh_squad_assignments()
            except Exception as e:
                if isinstance(e, fortnitepy.HTTPException):
                    client.debug_print_exception(e)
                else:
                    client.print_exception(e)
                text = client.l('error_while_hiding_members')
                client.send(
                    text,
                    add_p=client.time,
                    file=sys.stderr
                )
                if message is not None:
                    await message.reply(text)
                return
            await message.reply(
                client.l(
                    'hide_members',
                    count
                )
            )
        else:
            if not client.party.me.leader:
                await message.reply(
                    client.l('not_a_party_leader')
                )
                return

            users = client.find_users(
                ' '.join(message.args[1:]),
                mode=FindUserMode.NAME_ID,
                method=FindUserMatchMethod.CONTAINS,
                users=client.party.members,
                me=message.author
            )

            async def hide(user):
                member = client.party.get_member(user.id)
                if member is None:
                    await message.reply(
                        client.l(
                            'not_in_party',
                            client.name(user)
                        )
                    )
                    return

                ret = await client.hide_member(member, message)
                if not isinstance(ret, Exception):
                    await message.reply(
                        client.l(
                            'hide',
                            client.name(member)
                        )
                    )

            if client.config['search_max'] and len(users) > client.config['search_max']:
                await message.reply(
                    client.l('too_many', client.l('user'), len(users))
                )
                return

            if len(users) == 0:
                await message.reply(
                    client.l(
                        'not_found',
                        client.l('user'),
                        ' '.join(message.args[1:])
                    )
                )
            elif len(users) == 1:
                await hide(users[0])
            else:
                client.select[message.author.id] = {
                    'exec': 'await hide(user)',
                    'globals': {**globals(), **locals()},
                    'variables': [
                        {'user': user}
                        for user in users
                    ]
                }
                await message.reply(
                    ('\n'.join([f'{num}: {client.name(user)}'
                                for num, user in enumerate(users, 1)])
                        + '\n' + client.l('enter_number_to_select', client.l('user')))
                )

    @command(
        name='show',
        usage='{name} ({client.l("name_or_id")})'
    )
    async def show(command: Command, client: 'Client', message: MyMessage) -> None:
        if not client.party.me.leader:
            await message.reply(
                client.l('not_a_party_leader')
            )
            return

        if len(message.args) < 2:
            count = 0
            for member in client.party.members:
                if client.party.remove_hide_user(member.id):
                    count += 1
            client.party.update_hide_users([])
            try:
                await client.party.refresh_squad_assignments()
            except Exception as e:
                if isinstance(e, fortnitepy.HTTPException):
                    client.debug_print_exception(e)
                else:
                    client.print_exception(e)
                text = client.l('error_while_showing_members')
                client.send(
                    text,
                    add_p=client.time,
                    file=sys.stderr
                )
                if message is not None:
                    await message.reply(text)
                return
            await message.reply(
                client.l(
                    'show_members',
                    count
                )
            )
        else:
            users = client.find_users(
                ' '.join(message.args[1:]),
                mode=FindUserMode.NAME_ID,
                method=FindUserMatchMethod.CONTAINS,
                users=client.party.members,
                me=message.author
            )

            async def show(user):
                member = client.party.get_member(user.id)
                if member is None:
                    await message.reply(
                        client.l(
                            'not_in_party',
                            client.name(user)
                        )
                    )
                    return

                ret = await client.show_member(member, message)
                if not isinstance(ret, Exception):
                    await message.reply(
                        client.l(
                            'show',
                            client.name(member)
                        )
                    )

            if client.config['search_max'] and len(users) > client.config['search_max']:
                await message.reply(
                    client.l('too_many', client.l('user'), len(users))
                )
                return

            if len(users) == 0:
                await message.reply(
                    client.l(
                        'not_found',
                        client.l('user'),
                        ' '.join(message.args[1:])
                    )
                )
            elif len(users) == 1:
                await show(users[0])
            else:
                client.select[message.author.id] = {
                    'exec': 'await show(user)',
                    'globals': {**globals(), **locals()},
                    'variables': [
                        {'user': user}
                        for user in users
                    ]
                }
                await message.reply(
                    ('\n'.join([f'{num}: {client.name(user)}'
                                for num, user in enumerate(users, 1)])
                        + '\n' + client.l('enter_number_to_select', client.l('user')))
                )

    @command(
        name='ready',
        usage='{name}'
    )
    async def ready(command: Command, client: 'Client', message: MyMessage) -> None:
        await client.party.me.set_ready(fortnitepy.ReadyState.READY)
        await message.reply(
            client.l(
                'set_to',
                client.l('ready_state'),
                client.l('ready_state_ready')
            )
        )

    @command(
        name='unready',
        usage='{name}'
    )
    async def unready(command: Command, client: 'Client', message: MyMessage) -> None:
        await client.party.me.set_ready(fortnitepy.ReadyState.NOT_READY)
        await message.reply(
            client.l(
                'set_to',
                client.l('ready_state'),
                client.l('ready_state_unready')
            )
        )

    @command(
        name='sitout',
        usage='{name}'
    )
    async def sitout(command: Command, client: 'Client', message: MyMessage) -> None:
        await client.party.me.set_ready(fortnitepy.ReadyState.SITTING_OUT)
        await message.reply(
            client.l(
                'set_to',
                client.l('ready_state'),
                client.l('ready_state_sitout')
            )
        )

    @command(
        name='match',
        usage='{name} ({client.l("number")})'
    )
    async def match(command: Command, client: 'Client', message: MyMessage) -> None:
        if len(message.args) < 2:
            players_left = 100
        else:
            try:
                players_left = int(message.args[1])
            except ValueError as e:
                client.debug_print_exception(e)
                await message.reply(
                    client.l('please_enter_valid_number')
                )
                return

        await client.party.me.set_in_match(
            players_left=players_left
        )
        await message.reply(
            client.l(
                'set_to',
                client.l('match_state'),
                client.l(
                    'players_left',
                    players_left
                )
            )
        )

    @command(
        name='unmatch',
        usage='{name}'
    )
    async def unmatch(command: Command, client: 'Client', message: MyMessage) -> None:
        await client.party.me.clear_in_match()
        await message.reply(
            client.l(
                'set_to',
                client.l('match_state'),
                client.l('off')
            )
        )

    @command(
        name='swap',
        usage='{name} [{client.l("name_or_id")}]'
    )
    async def swap(command: Command, client: 'Client', message: MyMessage) -> None:
        if len(message.args) < 2:
            await client.show_help(command, message)
            return

        users = client.find_users(
            ' '.join(message.args[1:]),
            mode=FindUserMode.NAME_ID,
            method=FindUserMatchMethod.CONTAINS,
            users=client.party.members,
            me=message.author
        )

        async def swap(user):
            member = client.party.get_member(user.id)
            if member is None:
                await message.reply(
                    client.l(
                        'not_in_party',
                        client.name(user)
                    )
                )
                return

            ret = await client.swap_member(member, message)
            if not isinstance(ret, Exception):
                await message.reply(
                    client.l(
                        'swap',
                        client.name(member)
                    )
                )

        if client.config['search_max'] and len(users) > client.config['search_max']:
            await message.reply(
                client.l('too_many', client.l('user'), len(users))
            )
            return

        if len(users) == 0:
            await message.reply(
                client.l(
                    'not_found',
                    client.l('user'),
                    ' '.join(message.args[1:])
                )
            )
        elif len(users) == 1:
            await swap(users[0])
        else:
            client.select[message.author.id] = {
                'exec': 'await swap(user)',
                'globals': {**globals(), **locals()},
                'variables': [
                    {'user': user}
                    for user in users
                ]
            }
            await message.reply(
                ('\n'.join([f'{num}: {client.name(user)}'
                            for num, user in enumerate(users, 1)])
                    + '\n' + client.l('enter_number_to_select', client.l('user')))
            )

    @command(
        name='stop',
        usage='{name}'
    )
    async def stop(command: Command, client: 'Client', message: MyMessage) -> None:
        for num in reversed(range(len(client.stoppable_tasks))):
            exc = None
            task = client.stoppable_tasks[num]
            if task.done():
                exc = task.exception()
            if exc is not None:
                client.debug_print_exception(exc)
            task.cancel()
            del task

        await message.reply(
            client.l('stopped')
        )

    @command(
        name='new_items',
        usage='{name}'
    )
    async def new_items(command: Command, client: 'Client', message: MyMessage) -> None:
        async def new_items():
            for item in client.bot.new_items.values():
                attr = f'is_{client.bot.convert_backend_to_key(item["type"]["backendValue"])}_lock_for'
                if not getattr(client, attr)(message.user_type):
                    await client.party.me.change_asset(
                        item['type']['backendValue'],
                        item['id'],
                        keep=False
                    )
                    await message.reply(
                        f'{item["type"]["displayValue"]}: {client.name_cosmetic(item)}'
                    )
                    await asyncio.sleep(5)
                else:
                    await message.reply(
                        client.l('cosmetic_locked')
                    )
                    return
            await message.reply(
                client.l(
                    'has_end',
                    client.l('new_items')
                )
            )

        task = client.loop.create_task(new_items())
        client.stoppable_tasks.append(task)

    @command(
        name='shop_items',
        usage='{name}'
    )
    async def shop_items(command: Command, client: 'Client', message: MyMessage) -> None:
        async def shop_items():
            try:
                shop = await client.fetch_item_shop()
            except fortnitepy.HTTPException as e:
                m = 'errors.com.epicgames.common.missing_action'
                if e.message_code == m:
                    client.debug_print_exception(e)
                    await client.auth.accept_eula()
                    shop = await client.fetch_item_shop()
                else:
                    raise
            items = []
            entries = (sorted(shop.featured_items, key=lambda x: x.sort_priority, reverse=True)
                       + sorted(shop.daily_items, key=lambda x: x.sort_priority, reverse=True)
                       + sorted(shop.special_featured_items, key=lambda x: x.sort_priority, reverse=True)
                       + sorted(shop.special_daily_items, key=lambda x: x.sort_priority, reverse=True))
            for entry in entries:
                for item in entry.grants:
                    if item['type'] not in ['AthenaCharacter',
                                            'AthenaBackpack',
                                            'AthenaPet',
                                            'AthenaPetCarrier',
                                            'AthenaPickaxe',
                                            'AthenaDance',
                                            'AthenaEmoji',
                                            'AthenaToy']:
                        continue
                    items.append({
                        'name': client.bot.main_items.get(item['asset'], {}).get('name'),
                        'id': item['asset'],
                        'type': {
                            'value': client.bot.convert_backend_type(item['type']),
                            'displayValue': (
                                client.bot.l(
                                    client.bot.convert_backend_type(item['type'])
                                )
                                or client.bot.convert_backend_type(item['type'])
                            ),
                            'backendValue': item['type']
                        }
                    })
            for item in items:
                attr = f'is_{client.bot.convert_backend_to_key(item["type"]["backendValue"])}_lock_for'
                if not getattr(client, attr)(message.user_type):
                    await client.party.me.change_asset(
                        item['type']['backendValue'],
                        item['id'],
                        keep=False
                    )
                    await message.reply(
                        f'{item["type"]["displayValue"]}: {client.name_cosmetic(item)}'
                    )
                    await asyncio.sleep(5)

                else:
                    await message.reply(
                        client.l('cosmetic_locked')
                    )
            await message.reply(
                client.l(
                    'has_end',
                    client.l('shop_items')
                )
            )

        task = client.loop.create_task(shop_items())
        client.stoppable_tasks.append(task)

    @command(
        name='enlightenment',
        usage='{name} [{client.l("season")}] [{client.l("number")}]'
    )
    async def enlightenment(command: Command, client: 'Client', message: MyMessage) -> None:
        if len(message.args) < 3:
            await client.show_help(command, message)
            return

        try:
            season = int(message.args[1])
            number = int(message.args[2])
        except ValueError as e:
            client.debug_print_exception(e)
            await message.reply(
                client.l('please_enter_valid_number')
            )
            return

        if not client.is_emote_lock_for(message.user_type):
            await client.party.me.change_asset(
                'AthenaCharacter',
                client.party.me.outfit,
                variants=client.party.me.outfit_variants,
                enlightenment=(season, number),
                corruption=client.party.me.corruption
            )
            await message.reply(
                client.l(
                    'set_to',
                    'enlightenment',
                    f'{season}, {number}'
                )
            )
        else:
            await message.reply(
                client.l('cosmetic_locked')
            )

    @command(
        name='corruption',
        usage='{name} [{client.l("number")}]'
    )
    async def corruption(command: Command, client: 'Client', message: MyMessage) -> None:
        if len(message.args) < 2:
            await client.show_help(command, message)
            return

        try:
            number = int(message.args[1])
        except ValueError as e:
            client.debug_print_exception(e)
            await message.reply(
                client.l('please_enter_valid_number')
            )
            return

        if not client.is_emote_lock_for(message.user_type):
            await client.party.me.change_asset(
                'AthenaCharacter',
                client.party.me.outfit,
                variants=client.party.me.outfit_variants,
                enlightenment=client.party.me.enlightenments,
                corruption=number
            )
            await message.reply(
                client.l(
                    'set_to',
                    'corruption',
                    number
                )
            )
        else:
            await message.reply(
                client.l('cosmetic_locked')
            )

    @command(
        name='all_outfit',
        usage='{name}'
    )
    async def all_outfit(command: Command, client: 'Client', message: MyMessage) -> None:
        await all_cosmetics('AthenaCharacter', client, message)

    @command(
        name='all_backpack',
        usage='{name}'
    )
    async def all_backpack(command: Command, client: 'Client', message: MyMessage) -> None:
        await all_cosmetics('AthenaBackpack', client, message)

    @command(
        name='all_pet',
        usage='{name}'
    )
    async def all_pet(command: Command, client: 'Client', message: MyMessage) -> None:
        await all_cosmetics('AthenaPet,AthenaPetCarrier', client, message)

    @command(
        name='all_pickaxe',
        usage='{name}'
    )
    async def all_pickaxe(command: Command, client: 'Client', message: MyMessage) -> None:
        await all_cosmetics('AthenaCharacter', client, message)

    @command(
        name='all_emote',
        usage='{name}'
    )
    async def all_emote(command: Command, client: 'Client', message: MyMessage) -> None:
        await all_cosmetics('AthenaDance', client, message)

    @command(
        name='all_emoji',
        usage='{name}'
    )
    async def all_emoji(command: Command, client: 'Client', message: MyMessage) -> None:
        await all_cosmetics('AthenaEmoji', client, message)

    @command(
        name='all_toy',
        usage='{name}'
    )
    async def all_toy(command: Command, client: 'Client', message: MyMessage) -> None:
        await all_cosmetics('AthenaToy', client, message)

    @command(
        name='cid',
        usage='{name} [ID]'
    )
    async def cid(command: Command, client: 'Client', message: MyMessage) -> None:
        await cosmetic_search('AthenaCharacter', 'id', command, client, message)

    @command(
        name='bid',
        usage='{name} [ID]'
    )
    async def bid(command: Command, client: 'Client', message: MyMessage) -> None:
        await cosmetic_search('AthenaBackpack', 'id', command, client, message)

    @command(
        name='petcarrier',
        usage='{name} [ID]'
    )
    async def petcarrier(command: Command, client: 'Client', message: MyMessage) -> None:
        await cosmetic_search('AthenaPet,AthenaPetCarrier', 'id', command, client, message)

    @command(
        name='pickaxe_id',
        usage='{name} [ID]'
    )
    async def pickaxe_id(command: Command, client: 'Client', message: MyMessage) -> None:
        await cosmetic_search('AthenaPickaxe', 'id', command, client, message)

    @command(
        name='eid',
        usage='{name} [ID]'
    )
    async def eid(command: Command, client: 'Client', message: MyMessage) -> None:
        await cosmetic_search('AthenaDance', 'id', command, client, message)

    @command(
        name='emoji_id',
        usage='{name} [ID]'
    )
    async def emoji_id(command: Command, client: 'Client', message: MyMessage) -> None:
        await cosmetic_search('AthenaEmoji', 'id', command, client, message)

    @command(
        name='toy_id',
        usage='{name} [ID]'
    )
    async def toy_id(command: Command, client: 'Client', message: MyMessage) -> None:
        await cosmetic_search('AthenaToy', 'id', command, client, message)

    @command(
        name='id',
        usage='{name} [ID]'
    )
    async def id(command: Command, client: 'Client', message: MyMessage) -> None:
        await cosmetic_search(None, 'id', command, client, message)

    @command(
        name='outfit',
        usage='{name} [{client.l("name")}]'
    )
    async def outfit(command: Command, client: 'Client', message: MyMessage) -> None:
        await cosmetic_search('AthenaCharacter', 'name', command, client, message)

    @command(
        name='random_outfit',
        usage='{name}'
    )
    async def random_outfit(command: Command, client: 'Client', message: MyMessage) -> None:
        await random_cosmetic('AthenaCharacter', command, client, message)

    @command(
        name='clear_outfit',
        usage='{name}'
    )
    async def clear_outfit(command: Command, client: 'Client', message: MyMessage) -> None:
        if not client.is_outfit_lock_for(message.user_type):
            await client.party.me.change_asset('AthenaCharacter', '')
            await message.reply(client.l('cleared'))
        else:
            await message.reply(
                client.l('cosmetic_locked')
            )

    @command(
        name='backpack',
        usage='{name} [{client.l("name")}]'
    )
    async def backpack(command: Command, client: 'Client', message: MyMessage) -> None:
        await cosmetic_search('AthenaBackpack', 'name', command, client, message)

    @command(
        name='random_backpack',
        usage='{name}'
    )
    async def random_backpack(command: Command, client: 'Client', message: MyMessage) -> None:
        await random_cosmetic('AthenaBackpack', command, client, message)

    @command(
        name='pet',
        usage='{name} [{client.l("name")}]'
    )
    async def pet(command: Command, client: 'Client', message: MyMessage) -> None:
        await cosmetic_search('AthenaPet,AthenaPetCarrier', 'name', command, client, message)

    @command(
        name='random_pet',
        usage='{name}'
    )
    async def random_pet(command: Command, client: 'Client', message: MyMessage) -> None:
        await random_cosmetic('AthenaPet,AthenaPerCarrier', command, client, message)

    @command(
        name='clear_backpack',
        usage='{name}'
    )
    async def clear_backpack(command: Command, client: 'Client', message: MyMessage) -> None:
        if not client.is_backpack_lock_for(message.user_type):
            await client.party.me.change_asset('AthenaBackpack', '')
            await message.reply(client.l('cleared'))
        else:
            await message.reply(
                client.l('cosmetic_locked')
            )

    @command(
        name='pickaxe',
        usage='{name} [{client.l("name")}]'
    )
    async def pickaxe(command: Command, client: 'Client', message: MyMessage) -> None:
        await cosmetic_search('AthenaPickaxe', 'name', command, client, message)

    @command(
        name='random_pickaxe',
        usage='{name}'
    )
    async def random_pickaxe(command: Command, client: 'Client', message: MyMessage) -> None:
        await random_cosmetic('AthenaPickaxe', command, client, message)

    @command(
        name='clear_pickaxe',
        usage='{name}'
    )
    async def clear_pickaxe(command: Command, client: 'Client', message: MyMessage) -> None:
        if not client.is_pickaxe_lock_for(message.user_type):
            await client.party.me.change_asset('AthenaPickaxe', '')
            await message.reply(client.l('cleared'))
        else:
            await message.reply(
                client.l('cosmetic_locked')
            )

    @command(
        name='emote',
        usage='{name} [{client.l("name")}]'
    )
    async def emote(command: Command, client: 'Client', message: MyMessage) -> None:
        await cosmetic_search('AthenaDance', 'name', command, client, message)

    @command(
        name='random_emote',
        usage='{name}'
    )
    async def random_emote(command: Command, client: 'Client', message: MyMessage) -> None:
        await random_cosmetic('AthenaDance', command, client, message)

    @command(
        name='emoji',
        usage='{name} [{client.l("name")}]'
    )
    async def emoji(command: Command, client: 'Client', message: MyMessage) -> None:
        await cosmetic_search('AthenaEmoji', 'name', command, client, message)

    @command(
        name='random_emoji',
        usage='{name}'
    )
    async def random_emoji(command: Command, client: 'Client', message: MyMessage) -> None:
        await random_cosmetic('AthenaEmoji', command, client, message)

    @command(
        name='toy',
        usage='{name} [{client.l("name")}]'
    )
    async def toy(command: Command, client: 'Client', message: MyMessage) -> None:
        await cosmetic_search('AthenaToy', 'name', command, client, message)

    @command(
        name='random_toy',
        usage='{name}'
    )
    async def random_toy(command: Command, client: 'Client', message: MyMessage) -> None:
        await random_cosmetic('AthenaToy', command, client, message)

    @command(
        name='clear_emote',
        usage='{name}'
    )
    async def clear_emote(command: Command, client: 'Client', message: MyMessage) -> None:
        if not client.is_emote_lock_for(message.user_type):
            await client.party.me.change_asset('AthenaDance', '')
            await message.reply(client.l('cleared'))
        else:
            await message.reply(
                client.l('cosmetic_locked')
            )

    @command(
        name='item',
        usage='{name} [{client.l("name")}]'
    )
    async def item(command: Command, client: 'Client', message: MyMessage) -> None:
        await cosmetic_search(None, 'name', command, client, message)

    @command(
        name='random_item',
        usage='{name}'
    )
    async def random_item(command: Command, client: 'Client', message: MyMessage) -> None:
        await random_cosmetic(None, command, client, message)

    @command(
        name='playlist_id',
        usage='{name} [ID]'
    )
    async def playlist_id(command: Command, client: 'Client', message: MyMessage) -> None:
        await playlist_search('id', command, client, message)

    @command(
        name='playlist',
        usage='{name} [{client.l("name")}]'
    )
    async def playlist(command: Command, client: 'Client', message: MyMessage) -> None:
        await playlist_search('name', command, client, message)

    @command(
        name='island_code',
        usage='{name} [{client.l("island_code")}]'
    )
    async def island_code(command: Command, client: 'Client', message: MyMessage) -> None:
        if not client.party.leader:
            await message.reply(
                client.l('not_a_party_leader')
            )
            return
        meta = client.party.meta
        data = (meta.get_prop('Default:PlaylistData_j'))['PlaylistData']
        data['playlistName'] = 'Playlist_PlaygroundV2'
        data['mnemonic'] = message.args[1]

        final = {'PlaylistData': data}
        key = 'Default:PlaylistData_j'
        prop = {key: meta.set_prop(key, final)}

        try:
            await client.party.patch(updated=prop)
        except fortnitepy.Forbidden:
            await message.reply(
                client.l('not_a_party_leader')
            )
            return
        await message.reply(
            client.l(
                'set_to',
                client.bot.l('playlist'),
                message.args[1]
            )
        )

    @command(
        name='set',
        usage='{name} [{client.l("name")}]'
    )
    async def set_(command: Command, client: 'Client', message: MyMessage) -> None:
        await cosmetic_search(None, 'set', command, client, message)

    @command(
        name='set_style',
        usage='{name} [{client.l("cosmetic_types", **self.variables_without_self)}]'
    )
    async def set_style(command: Command, client: 'Client', message: MyMessage) -> None:
        if len(message.args) < 2:
            await client.show_help(command, message)
            return

        for k in ['outfit', 'backpack', 'pickaxe']:
            if message.args[1] in client.commands[k]:
                key = k
                break
        else:
            await client.show_help(command, message)
            return

        item = client.bot.convert_to_backend_type(key)
        asset = client.party.me.asset(item)
        enlightenment = client.party.me.enlightenments
        corruption = client.party.me.corruption
        styles = client.searcher.get_style(asset)

        async def set_style(style):
            attr = f'is_{client.bot.convert_backend_to_key(item)}_lock_for'
            if getattr(client, attr)(message.user_type):
                await message.reply(
                    client.l('cosmetic_locked')
                )
                return
            await client.party.me.change_asset(
                item,
                asset,
                variants=style['variants'],
                enlightenment=enlightenment,
                corruption=corruption
            )

        if len(styles) == 0:
            await message.reply(
                client.l('no_style_change')
            )
        else:
            client.select[message.author.id] = {
                'exec': (
                    'await set_style(style)'
                ),
                'globals': {**globals(), **locals()},
                'variables': [
                    {'style': style}
                    for style in styles
                ]
            }
            await message.reply(
                ('\n'.join([f'{num}: {style["name"]}'
                            for num, style in enumerate(styles, 1)])
                    + '\n' + client.l('enter_number_to_select', client.bot.l('style')))
            )

    @command(
        name='add_style',
        usage='{name} [{client.l("cosmetic_types", **self.variables_without_self)}]'
    )
    async def add_style(command: Command, client: 'Client', message: MyMessage) -> None:
        if len(message.args) < 2:
            await client.show_help(command, message)
            return

        for k in ['outfit', 'backpack', 'pickaxe']:
            if message.args[1] in client.commands[k]:
                key = k
                break
        else:
            await client.show_help(command, message)
            return

        item = client.bot.convert_to_backend_type(key)
        asset = client.party.me.asset(item)
        variants = client.party.me.variants(item)
        enlightenment = client.party.me.enlightenments
        corruption = client.party.me.corruption
        styles = client.searcher.get_style(asset)

        async def add_style(style):
            attr = f'is_{client.bot.convert_backend_to_key(item)}_lock_for'
            if getattr(client, attr)(message.user_type):
                await message.reply(
                    client.l('cosmetic_locked')
                )
                return
            await client.party.me.change_asset(
                item,
                asset,
                variants=variants + style['variants'],
                enlightenment=enlightenment,
                corruption=corruption
            )

        if len(styles) == 0:
            await message.reply(
                client.l('no_style_change')
            )
        else:
            client.select[message.author.id] = {
                'exec': (
                    'await add_style(style)'
                ),
                'globals': {**globals(), **locals()},
                'variables': [
                    {'style': style}
                    for style in styles
                ]
            }
            await message.reply(
                ('\n'.join([f'{num}: {style["name"]}'
                            for num, style in enumerate(styles, 1)])
                    + '\n' + client.l('enter_number_to_select', client.bot.l('style')))
            )

    @command(
        name='set_variant',
        usage='{name} [{client.l("cosmetic_types", **self.variables_without_self)}] [variant] [{client.l("number")}]'
    )
    async def set_variant(command: Command, client: 'Client', message: MyMessage) -> None:
        if len(message.args) < 4:
            await client.show_help(command, message)
            return

        if not any([message.args[1] in client.commands[key]
                    for key in ['outfit', 'backpack', 'pickaxe']]):
            await client.show_help(command, message)
            return

        for k in ['outfit', 'backpack', 'pickaxe']:
            if message.args[1] in client.commands[k]:
                key = k
                break
        else:
            return

        variant_dict = {}
        for num, text in enumerate(message.args[2:]):
            if num % 2 != 0:
                continue
            try:
                variant_dict[text] = message.args[num + 3]
            except IndexError:
                break
        item = client.bot.convert_to_backend_type(key)
        variants = client.party.me.create_variants(**variant_dict)
        asset = client.party.me.asset(item)
        enlightenment = client.party.me.enlightenments
        corruption = client.party.me.corruption

        attr = f'is_{client.bot.convert_backend_to_key(item)}_lock_for'
        if getattr(client, attr)(message.user_type):
            await message.reply(
                client.l('cosmetic_locked')
            )
            return
        await client.party.me.change_asset(
            item,
            asset,
            variants=variants,
            enlightenment=enlightenment,
            corruption=corruption
        )

    @command(
        name='add_variant',
        usage='{name} [{client.l("cosmetic_types", **self.variables_without_self)}] [variant] [{client.l("number")}]'
    )
    async def add_variant(command: Command, client: 'Client', message: MyMessage) -> None:
        if len(message.args) < 4:
            await client.show_help(command, message)
            return

        if not any([message.args[1] in client.commands[key]
                    for key in ['outfit', 'backpack', 'pickaxe']]):
            await client.show_help(command, message)
            return

        for k in ['outfit', 'backpack', 'pickaxe']:
            if message.args[1] in client.commands[k]:
                key = k
                break
        else:
            return

        variant_dict = {}
        for num, text in enumerate(message.args[2:]):
            if num % 2 != 0:
                continue
            try:
                variant_dict[text] = message.args[num + 3]
            except IndexError:
                break
        item = client.bot.convert_to_backend_type(key)
        variants = client.party.me.variants(item)
        variants += client.party.me.create_variants(**variant_dict)
        asset = client.party.me.asset(item)
        enlightenment = client.party.me.enlightenments
        corruption = client.party.me.corruption

        attr = f'is_{client.bot.convert_backend_to_key(item)}_lock_for'
        if getattr(client, attr)(message.user_type):
            await message.reply(
                client.l('cosmetic_locked')
            )
            return
        await client.party.me.change_asset(
            item,
            asset,
            variants=variants,
            enlightenment=enlightenment,
            corruption=corruption
        )

    @command(
        name='cosmetic_preset',
        usage='{name} [{client.l("save_or_load", **self.variables_without_self)}] [{client.l("number")}]'
    )
    async def cosmetic_preset(command: Command, client: 'Client', message: MyMessage) -> None:
        if len(message.args) < 3:
            await client.show_help(command, message)
            return

        if not message.args[2].isdigit():
            await message.reply(
                client.l('please_enter_valid_number')
            )
            return

        number = message.args[2]
        if int(number) <= 0:
            await message.reply(
                client.l('please_enter_valid_number')
            )
            return

        if message.args[1] in client.commands['save']:
            if client.user.id not in client.bot.cosmetic_presets:
                client.bot.cosmetic_presets[client.user.id] = {}
            client.bot.cosmetic_presets[client.user.id][number] = {
                'AthenaCharacter': {
                    'asset': client.party.me.asset('AthenaCharacter'),
                    'variants': client.party.me.variants('AthenaCharacter')
                },
                'AthenaBackpack': {
                    'asset': client.party.me.asset('AthenaBackpack'),
                    'variants': client.party.me.variants('AthenaBackpack')
                },
                'AthenaPickaxe': {
                    'asset': client.party.me.asset('AthenaPickaxe'),
                    'variants': client.party.me.variants('AthenaPickaxe')
                },
                'AthenaDance': {
                    'asset': client.emote
                },
                'enlightenment': client.party.me.enlightenments,
                'corruption': client.party.me.corruption
            }
            await client.bot.store_cosmetic_presets(client.user.id, client.bot.cosmetic_presets[client.user.id])
            await message.reply(
                client.l('cosmetic_preset_saved', number)
            )
        elif message.args[1] in client.commands['load']:
            if client.bot.cosmetic_presets.get(client.user.id, {}).get(number) is None:
                await message.reply(
                    client.l('cosmetic_preset_not_found')
                )
                return
            assets = client.bot.cosmetic_presets[client.user.id][number]
            coros = []

            items = [
                'AthenaCharacter',
                'AthenaBackpack',
                'AthenaPickaxe',
                'AthenaDance'
            ]
            for item in items:
                conf = client.bot.convert_backend_type(item)
                coro = client.party.me.change_asset(
                    item,
                    assets[item]['asset'],
                    variants=assets[item].get('variants'),
                    enlightenment=assets['enlightenment'],
                    corruption=assets['corruption'],
                    do_point=False
                )
                coro.__qualname__ = f'ClientPartyMember.set_{conf}'
                coros.append(coro)
            await client.party.me.edit(
                *coros
            )
            await message.reply(
                client.l('cosmetic_preset_loaded', number)
            )
        else:
            await message.reply(
                client.l('please_enter_valid_number')
            )
