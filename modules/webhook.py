# -*- coding: utf-8 -*-
import asyncio
import re
from typing import Union, TYPE_CHECKING

from .http import HTTPClient

if TYPE_CHECKING:
    from .bot import Bot
    from .client import Client


class WebhookClient:
    def __init__(self, client: Union['Bot', 'Client'], bot: 'Bot', loop: asyncio.AbstractEventLoop, http: HTTPClient) -> None:
        self.client = client
        self.bot = bot
        self.loop = loop
        self.http = http
        self.messages = []
        self.text_max = 1900
        self.loop_task = None

        self.url_pattern = re.compile(
            r'https://(ptb\.|canary\.)?discord(app)?\.com/api/webhooks'
            r'/\d{18}/.+'
        )

    def start(self) -> None:
        self.loop_task = self.loop.create_task(self.send_loop())

    def stop(self) -> None:
        if self.loop_task is not None:
            self.loop_task.cancel()

    async def send_loop(self) -> None:
        has_avatar = None
        while True:
            if (self.client.config['discord_log']
                    and self.url_pattern.match(self.client.config['discord_log'])):
                if has_avatar is None:
                    data = await self.http.get(
                        self.client.config['discord_log']
                    )
                    has_avatar = data['avatar'] is not None

                removed = []
                for num, message in enumerate(self.messages):
                    flag = False
                    if len(self.messages) >= 20 and self.client.config['skip_if_overflow']:
                        message = {
                            'content': f'Skipped {len(self.messages)} logs',
                            'Logs.txt': '\n'.join([mes['content'] for mes in self.messages])
                        }
                        flag = True
                        for num in enumerate(self.messages):
                            removed.append(num)
                    if not has_avatar:
                        message['avatar_url'] = 'https://cdn.discordapp.com/icons/718709023427526697/8353f50201fcfde80b8fcc9d806e7046.webp'
                    messages = [
                        message['content'][i:i + self.text_max]
                        for i in range(0, len(message['content']), self.text_max)
                    ]
                    for mes in messages:
                        error = False
                        while True:
                            data = message
                            data['content'] = mes
                            res = await self.http.post(
                                self.client.config['discord_log'],
                                data=data,
                                raw=True
                            )
                            try:
                                remain = int(res.headers['x-ratelimit-remaining'])
                            except KeyError:
                                remain = 5
                            if remain == 0 or res.status == 429:
                                reset_after = int(res.headers['x-ratelimit-reset-after'])
                                await asyncio.sleep(reset_after)
                            else:
                                if res.status != 204:
                                    error = True
                                break
                        if error:
                            break
                    if flag:
                        break
                    removed.append(num)

                for num in reversed(removed):
                    del self.messages[num]
            await asyncio.sleep(1)

    def send(self, content: str, user_name: str) -> None:
        if (self.client.config['discord_log']
                and self.url_pattern.match(self.client.config['discord_log'])):
            if self.bot.config.get('hide_email'):
                for client in self.bot.clients:
                    content = content.replace(
                        client.config['fortnite']['email'],
                        len(client.config['fortnite']['email']) * 'X'
                    )
            if self.bot.config.get('hide_password'):
                content = content.replace(
                    self.bot.config['web']['password'],
                    len(self.bot.config['web']['password']) * 'X'
                )
            if self.bot.config.get('hide_token'):
                clients = [self.bot, *self.bot.clients]
                for client in clients:
                    content = content.replace(
                        client.config['discord']['token'],
                        len(client.config['discord']['token']) * 'X'
                    )
            if self.bot.config.get('hide_webhook'):
                clients = [self.bot, *self.bot.clients]
                for client in clients:
                    if client.config['discord_log']:
                        content = content.replace(
                            client.config['discord_log'],
                            len(client.config['discord_log']) * 'X'
                        )

            if (len(self.messages) > 0
                    and (self.messages[-1]['username'] == user_name
                         and len(self.messages[-1]['content'] + content) < self.text_max)):
                if self.client.config['omit_over2000'] and len(content) > self.text_max:
                    self.messages[-1]['content'] += f'\n{content[:self.text_max]}...'
                else:
                    self.messages[-1]['content'] += f'\n{content}'
            else:
                self.messages.append({'username': user_name, 'content': content})
