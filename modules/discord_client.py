# -*- coding: utf-8 -*-
import asyncio
import datetime
import importlib
import inspect
import io
import sys
from typing import TYPE_CHECKING, Any, Callable, Optional, Union, List, Type

from .colors import green
from .commands import MyMessage
from .localize import LocalizedText

if TYPE_CHECKING:
    from .bot import Bot
    from .client import Client


discord = importlib.import_module('discord')
fortnitepy = importlib.import_module('fortnitepy')


class DiscordClient(discord.Client):
    def __init__(self, bot: Union['Bot', 'Client'], config: dict, *, loop=None, **options) -> None:
        self.bot = bot
        self.config = config

        super().__init__(loop=loop, **options)

        self.booted_at = None

        self._owner = {}
        self._whitelist = {}
        self._blacklist = {}

    # Config controls
    def fix_config(self) -> None:
        self.config['discord']['status_type'] = getattr(
            discord.ActivityType,
            self.config['discord']['status_type'].lower()
        )

    @property
    def owner(self) -> list:
        return list(self._owner.values())

    def is_owner(self, user_id: str) -> bool:
        return self._owner.get(user_id) is not None

    @property
    def whitelist(self) -> list:
        return list(self._whitelist.values())

    def is_whitelist(self, user_id: str) -> bool:
        return self._whitelist.get(user_id) is not None

    @property
    def blacklist(self) -> list:
        return list(self._blacklist.values())

    def is_blacklist(self, user_id: int) -> bool:
        return self._blacklist.get(user_id) is not None

    def get_user_type(self, user_id: int) -> str:
        if self.is_owner(user_id):
            return 'owner'
        elif self.is_whitelist(user_id):
            return 'whitelist'
        elif self.is_blacklist(user_id):
            return 'blacklist'
        elif self.get_user(user_id) is not None and self.get_user(user_id).bot:
            return 'bot'
        return 'user'

    def is_for(self, config_key: str, user_id: int, discord: Optional[bool] = True) -> bool:
        user_type = self.get_user_type(user_id)
        if discord:
            config = self.config['discord'][config_key]
        else:
            config = self.config[config_key]
        if config is None:
            return False
        return user_type in config

    def is_chat_max_for(self, user_id: str) -> bool:
        return self.is_for('chat_max_for', user_id)

    def is_discord_enable_for(self, user_id: int) -> bool:
        return self.is_for('command_enable_for', user_id)

    def is_ng_word_for(self, user_id: int) -> bool:
        return self.is_for('ng_word_for', user_id, discord=False)

    # Basic functions
    @property
    def variables(self) -> dict:
        user = getattr(self, 'user', None)
        uptime = (datetime.datetime.now() - self.booted_at) if self.booted_at is not None else None
        if uptime is not None:
            d, h, m, s = self.bot.convert_td(uptime)
        else:
            d = h = m = s = None
        return {
            'self': self,
            'client': self,
            'bot': self,
            'discord_bot': self,
            'guild_count': len(self.guilds),
            'display_name': getattr(user, 'display_name', None),
            'id': getattr(user, 'id', None),
            'uptime': uptime,
            'uptime_days': d,
            'uptime_hours': h,
            'uptime_minutes': m,
            'uptime_seconds': s,
            'owner': self.owner,
            'whitelist': self.whitelist,
            'blacklist': self.blacklist
        }

    def eval_format(self, text: str, variables: dict) -> str:
        return self.bot.eval_format(text, variables)

    def l(self, key: str, *args: tuple, default: Optional[str] = '', **kwargs: dict) -> LocalizedText:
        return LocalizedText(self.bot, ['discord_client', key], default, *args, **kwargs)

    def send(self, content: Any,
             user_name: Optional[str] = None,
             color: Optional[Callable] = None,
             add_p: Optional[Union[Callable, List[Callable]]] = None,
             add_d: Optional[Union[Callable, List[Callable]]] = None,
             file: Optional[io.IOBase] = None) -> Optional[str]:
        file = file or sys.stdout
        content = str(content)
        color = color or (lambda x: x)
        add_p = (add_p if isinstance(add_p, list) else [add_p or (lambda x: x)])
        add_d = (add_d if isinstance(add_d, list) else [add_d or (lambda x: x)])
        if file == sys.stderr:
            add_d.append(self.bot.discord_error)
        if not self.config['no_logs'] if self.config else True:
            text = content
            for func in add_p:
                text = func(text)
            print(color(text), file=file)

        if self.bot.webhook:
            content = discord.utils.escape_markdown(content)
            name = user_name or self.user.name
            text = content
            for func in add_d:
                text = func(text)
            self.bot.webhook.send(text, name)

    def now(self) -> str:
        return self.bot.now()

    def time(self, text: str) -> str:
        return f'[{self.now()}] [{self.user.name}] {text}'

    def name(self, user: Optional[discord.User] = None) -> str:
        user = user or self.user
        if self.config['loglevel'] == 'normal':
            return user.name
        else:
            return '{0} / {0.id}'.format(user)

    def format_exception(self, exc: Optional[Exception] = None) -> str:
        return self.bot.print_exception(exc)

    def print_exception(self, exc: Optional[Exception] = None) -> None:
        return self.bot.print_exception(exc)

    def debug_print_exception(self, exc: Optional[Exception] = None) -> None:
        return self.bot.debug_print_exception(exc)

    async def aexec(self, body: str, variables: dict) -> Optional[bool]:
        flag = False
        for line in body.split('\n'):
            match = self.bot.return_pattern.fullmatch(line)
            if match is not None:
                flag = True
                break
        try:
            await self.bot.aexec(body, variables)
            if flag:
                return False
        except Exception as e:
            def cleanup(code_context):
                return ''.join([i.strip('\n ') for i in code_context])

            self.bot.send(
                ('Ignoring exception\n'
                 f'body: {body}\n'
                 'Traceback\n'
                 + '\n'.join([(f'  File "{stack.filename}", line {stack.lineno}, in {stack.function}'
                               + (f'\n    {cleanup(stack.code_context)}' if stack.code_context else ''))
                              for stack in reversed(inspect.stack()[1:])])),
                file=sys.stderr
            )

    async def exec_event(self, event: str, variables: dict) -> None:
        if self.config['discord']['exec'][event]:
            return await self.aexec(
                ' '.join(self.config['discord']['exec'][event]),
                variables
            )

    async def update_owner(self) -> None:
        self._owner = {}
        if self.config['discord']['owner'] is None:
            return
        for owner in self.config['discord']['owner']:
            user = self.get_user(owner)
            if user is None:
                try:
                    user = await self.fetch_user(owner)
                except discord.NotFound as e:
                    self.debug_print_exception(e)
            if user is None:
                self.send(
                    self.l(
                        'owner_not_found',
                        owner
                    ),
                    add_p=self.time,
                    add_d=self.bot.discord_error,
                    file=sys.stderr
                )
            else:
                self._owner[user.id] = user
                self.send(
                    self.l(
                        'owner_log',
                        self.name(user)
                    ),
                    color=green,
                    add_p=self.time
                )

    async def _update_user_list(self, lists: list, keys_list: list) -> None:
        for keys, list_users in zip(keys_list, lists):
            attr = keys[-1]
            setattr(self, f'_{attr}', {})
            for list_user in list_users:
                user = self.get_user(list_user)
                if user is None:
                    try:
                        user = await self.fetch_user(list_user)
                    except discord.NotFound as e:
                        self.debug_print_exception(e)
                if user is None:
                    self.send(
                        self.l(
                            'list_user_not_found',
                            self.l(attr),
                            list_user
                        ),
                        add_p=self.time,
                        add_d=self.bot.discord_error,
                        file=sys.stderr
                    )
                else:
                    getattr(self, f'_{attr}')[user.id] = user
                    self.send(
                        self.l(
                            'list_user_log',
                            self.l(attr),
                            self.name(user)
                        ),
                        color=green,
                        add_p=self.time
                    )

    async def update_user_lists(self) -> None:
        keys_list = [
            ['discord', 'whitelist'],
            ['discord', 'blacklist']
        ]
        lists = [self.bot.get_dict_key(self.config, keys)
                 for keys in keys_list
                 if self.bot.get_dict_key(self.config, keys) is not None]
        await self._update_user_list(
            lists,
            keys_list
        )

    async def update_status(self) -> None:
        activity = discord.Activity(
            name=self.eval_format(self.config['discord']['status'], self.variables),
            type=self.config['discord']['status_type']
        )
        await self.change_presence(activity=activity)

    async def status_loop(self) -> None:
        while True:
            try:
                await self.update_status()
            except Exception as e:
                self.debug_print_exception(e)
            await asyncio.sleep(30)

    async def ng_word_check(self, message: discord.Message) -> bool:
        if message.author.id == self.user.id:
            return True
        if not self.is_ng_word_for(message.author.id):
            return True
        command_stats = getattr(self.bot, 'command_stats', self.bot.bot.command_stats)

        match = None
        for ng in self.config['ng_words']:
            flag = False
            if ng['matchmethod'] == 'full' and any([message.content == word for word in ng['words']]):
                for word in ng['words']:
                    if message.content == word:
                        match = word
                        break
                flag = True
            elif ng['matchmethod'] == 'contains' and any([word in message.content for word in ng['words']]):
                for word in ng['words']:
                    if word in message.content:
                        match = word
                        break
                flag = True
            elif ng['matchmethod'] == 'starts' and any([message.content.startswith(word) for word in ng['words']]):
                for word in ng['words']:
                    if message.content.startswith(word):
                        match = word
                        break
                flag = True
            elif ng['matchmethod'] == 'ends' and any([message.content.endswith(word) for word in ng['words']]):
                for word in ng['words']:
                    if message.content.endswith(word):
                        match = word
                        break
                flag = True

            if flag:
                if self.user.id not in command_stats:
                    command_stats[self.user.id] = {'commands': {}, 'ngs': {}}
                stats = command_stats[self.user.id]
                if message.author.id not in stats['ngs']:
                    stats['ngs'][message.author.id] = {}
                if match not in stats['ngs'][message.author.id]:
                    stats['ngs'][message.author.id][match] = 0
                stats['ngs'][message.author.id][match] += 1

                if self.config['ng_word_reply']:
                    var = self.variables
                    var.update({
                        'message': message,
                        'author': message.author,
                        'author_display_name': message.author.name,
                        'author_id': message.author.id
                    })
                    text = self.eval_format(
                        self.config['ng_word_reply'],
                        var
                    )
                    await message.channel.send(text)

                return False

        return True

    # Events
    async def on_ready(self) -> None:
        self.booted_at = datetime.datetime.now()
        self.loop.create_task(self.status_loop())

        self.send(
            self.l(
                'ready',
                self.name()
            ),
            color=green,
            add_p=self.time
        )
        ret = await self.exec_event('ready', {**locals(), **self.variables})
        if ret is False:
            return

        try:
            await self.update_owner()
        except Exception as e:
            self.send(
                (f'{self.format_exception(e)}\n{e}\n'
                 + self.l(
                     'error_while_updating_owner'
                 )),
                file=sys.stderr
            )
        try:
            await self.update_user_lists()
        except Exception as e:
            self.send(
                (f'{self.format_exception(e)}\n{e}\n'
                 + self.l(
                     'error_while_updating_list'
                 )),
                file=sys.stderr
            )

    async def on_message(self, message: discord.Message) -> None:
        if not self.is_ready():
            await self.wait_until_ready()

        if (self.config['discord']['chat_max'] is not None
                and self.is_chat_max_for(message.author.id)
                and len(message.content) > self.config['discord']['chat_max']):
            return

        if isinstance(self.bot, fortnitepy.Client) and not await self.ng_word_check(message):
            return

        if (message.author.id == self.user.id
                or message.webhook_id is not None
                or not self.is_discord_enable_for(message.author.id)):
            return

        if isinstance(self.bot, fortnitepy.Client):
            if '{all}' not in self.config['discord']['channels']:
                mapping = {
                    'name': self.bot.user.display_name,
                    'id': self.bot.user.id,
                    'discord_name': self.user.name,
                    'discord_id': self.user.id,
                    'discord_nickname': getattr(message.guild, 'me', self.user).display_name,
                    'num': self.bot.num
                }
                if not any([message.channel.name == self.bot.cleanup_channel_name(c.format_map(mapping))
                            for c in self.config['discord']['channels']]):
                    return
                
                self.send(
                    message.content,
                    user_name=self.name(message.author),
                    add_p=[lambda x: f'{self.name(message.author)} | {x}', self.time]
                )

                mes = MyMessage(self.bot, message)
                await self.bot.process_command(mes, self.config['discord']['prefix'])
        else:
            for client in self.bot.clients:
                mapping = {
                    'name': client.user.display_name,
                    'id': client.user.id,
                    'discord_name': self.user.name,
                    'discord_id': self.user.id,
                    'discord_nickname': getattr(message.guild, 'me', self.user).display_name,
                    'num': client.num
                }
                if not any([message.channel.name == self.bot.cleanup_channel_name(c.format_map(mapping))
                            for c in self.config['discord']['channels']]):
                    continue

                self.send(
                    message.content,
                    user_name=self.name(message.author),
                    add_p=[lambda x: f'{self.name(message.author)} | {x}', self.time]
                )

                mes = MyMessage(client, message, discord_client=self)
                await client.process_command(mes, self.config['discord']['prefix'])
