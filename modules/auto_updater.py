import asyncio
import json
import os
import sys
from typing import TYPE_CHECKING, Optional, Tuple, Union

from aiofiles import open as aopen
from aiofiles.os import remove as aremove
from aiofiles.os import rename as arename

from .localize import LocalizedText

if TYPE_CHECKING:
    from .bot import Bot


__version__ = '1.5.2'


class Updater:
    version = __version__

    def __init__(self, bot: 'Bot'):
        self.bot = bot
        self.updates = {
            'docs/en/commands.md': [],
            'docs/en/config.md': [],
            'docs/en/custom_commands.md': [],
            'docs/en/docs.md': [],
            'docs/en/glossary.md': [],
            'docs/en/pc.md': [],
            'docs/en/repl.md': [],
            'docs/en/replies.md': [],
            'docs/en/setup.md': [],

            'docs/ja/commands.md': [],
            'docs/ja/config.md': [],
            'docs/ja/custom_commands.md': [],
            'docs/ja/docs.md': [],
            'docs/ja/glossary.md': [],
            'docs/ja/pc.md': [],
            'docs/ja/repl.md': [],
            'docs/ja/replies.md': [],
            'docs/ja/setup.md': [],

            'lang/en.json': [],
            'lang/es.json': [],
            'lang/ja.json': [],

            'modules/__init__.py': ['backup'],
            'modules/auth.py': ['backup'],
            'modules/auto_updater.py': ['backup'],
            'modules/bot.py': ['backup'],
            'modules/client.py': ['backup'],
            'modules/colors.py': ['backup'],
            'modules/commands.py': ['backup'],
            'modules/cosmetics.py': ['backup'],
            'modules/discord_client.py': ['backup'],
            'modules/encoder.py': ['backup'],
            'modules/formatter.py': ['backup'],
            'modules/http.py': ['backup'],
            'modules/localize.py': ['backup'],
            'modules/web.py': ['backup'],
            'modules/webhook.py': ['backup'],

            'static/css/boot-switch.css': [],
            'static/css/clients-viewer.css': [],
            'static/css/clients-viewer-client.css': [],
            'static/css/editor.css': [],
            'static/css/header.css': [],
            'static/css/login.css': [],
            'static/css/main.css': [],
            'static/css/markdown.css': [],

            'static/images/backpack.jpg': ['raw'],
            'static/images/banner.jpg': ['raw'],
            'static/images/crown.png': ['raw'],
            'static/images/emote.jpg': ['raw'],
            'static/images/favicon.ico': ['raw'],
            'static/images/logo.png': ['raw'],
            'static/images/outfit.jpg': ['raw'],
            'static/images/pickaxe.jpg': ['raw'],

            'static/js/boot-switch.js': [],
            'static/js/clients-viewer.js': [],
            'static/js/clients-viewer-client.js': [],
            'static/js/editor.js': [],
            'static/js/header.js': [],
            'static/js/login.js': [],
            'static/js/main.js': [],
            'static/js/ws.js': [],

            'templates/boot-switch.jinja': [],
            'templates/clients-viewer.jinja': [],
            'templates/clients-viewer-client.jinja': [],
            'templates/editor.jinja': [],
            'templates/index.jinja': [],
            'templates/login.jinja': [],
            'templates/openfile.jinja': [],

            'commands.json': ['diff', 'db', 'backup'],
            'config.json': ['diff', 'db', 'backup'],
            'custom_commands.json': ['diff', 'db', 'backup'],
            'index.py': ['backup'],
            'LICENSE': [],
            'README.md': [],
            'README_EN.md': [],
            'README_ES.md': [],
            'replies.json': ['diff', 'db', 'backup']
        }
        self.pc_updates = {
            'INSTALL.bat': [],
            'requirements.txt': [],
            'RUN.bat': []
        }
        self.repl_updates = {
            'pyproject.toml': []
        }

    def l(self, key: str, *args: tuple, default: Optional[str] = '', **kwargs: dict) -> LocalizedText:
        return LocalizedText(self.bot, ['updater', key], default, *args, **kwargs)

    def add_new_key(self, data: dict, new: dict, overwrite: Optional[bool] = False) -> dict:
        if isinstance(new, dict):
            result = data.copy()
            for key, value in new.items():
                if isinstance(value, dict):
                    result[key] = self.add_new_key(result.get(key) or {}, value, overwrite)
                elif isinstance(value, list):
                    result[key] = self.add_new_key(result.get(key) or [], value, overwrite)
                if overwrite:
                    result[key] = value
                else:
                    result.setdefault(key, value)
        else:
            result = [
                (self.add_new_key(self.bot.get_list_index(data or [], i, {}), self.bot.get_list_index(new or [], i, {}), overwrite)
                 if isinstance(self.bot.get_list_index(data or [], i), dict) or isinstance(self.bot.get_list_index(new or [], i), dict) else
                 self.add_new_key(self.bot.get_list_index(data or [], i, []), self.bot.get_list_index(new or [], i, []), overwrite)
                 if isinstance(self.bot.get_list_index(data or [], i), list) or isinstance(self.bot.get_list_index(new or [], i), list) else
                 self.bot.get_list_index(data or [], i, self.bot.get_list_index(new or [], i)))
                for i in range(max(len(new), len(data or [])))
            ]
        return result

    async def check_update(self, uri: str, path: str, save: Optional[str] = None,
                           write: Optional[bool] = True) -> Tuple[bool, Optional[Union[bytes, str]]]:
        dirs = '/'.join(path.split('/')[:-1])
        dirs = f'{dirs}/' if dirs else ''
        filename = path.split('/')[-1]
        key = '.'.join(filename.split('.')[:-1])
        extension = filename.split('.')[-1]
        tags = self.updates.get(path, self.pc_updates.get(path, self.repl_updates.get(path)))
        save = save or path
        is_image = (
            True
            if path.endswith('.png') or path.endswith('.jpg') or path.endswith('.ico') else
            False
        )

        async def backup():
            if os.path.isfile(path) and 'backup' in tags:
                try:
                    if os.path.isfile(f'{dirs}{key}_old.{extension}'):
                        await aremove(f'{dirs}{key}_old.{extension}')
                    await arename(path, f'{dirs}{key}_old.{extension}')
                except PermissionError:
                    self.bot.send(
                        self.l(
                            'backup_failed',
                            path,
                            default=(
                                "'{0}' のバックアップに失敗しました\n"
                                "Failed backup for '{0}'"
                            )
                        ),
                        add_p=self.bot.time
                    )

        self.bot.send(
            self.l(
                'checking_update',
                path,
                default=(
                    "'{0}' のアップデートを確認中...\n"
                    "Checking update for '{0}'..."
                )
            ),
            add_p=[self.bot.time, lambda x: f'\n{x}']
        )
        retry = 5
        for tries in range(retry):
            if 'db' in tags:
                if self.bot.isfile(key):
                    existing = await self.bot.aload_json(key)
                else:
                    existing = {}
            else:
                if os.path.isfile(path):
                    if 'raw' in tags:
                        async with aopen(path, 'rb') as f:
                            existing = await f.read()
                            if not is_image and sys.platform == 'win32':
                                existing = existing.replace(b'\r\n', b'\n')
                    else:
                        async with aopen(path, 'r', encoding='utf-8') as f:
                            existing = await f.read()
                            if not is_image and sys.platform == 'win32':
                                existing = existing.replace('\r\n', '\n')
                else:
                    existing = b'' if 'raw' in tags else ''
            res = await self.bot.http.session.get(uri + path)
            if res.status == 404:
                self.bot.send(
                    self.l(
                        'file_not_found',
                        path,
                        default=(
                            "'{0}' ファイルが存在しません\n"
                            "File '{0}' doesn't exists"
                        )
                    ),
                    add_p=self.bot.time
                )
                return False, existing
            if res.status != 200:
                retry_after = 10
                self.bot.send(
                    self.l(
                        'get_failed',
                        path,
                        retry_after,
                        tries,
                        retry,
                        default=(
                            "'{0}' のデータの取得に失敗しました。{1}秒後に再試行します {2}/{3}\n"
                            "Failed to get data for '{0}'. Retry after {1} seconds {2}/{3}"
                        )
                    ),
                    add_p=self.bot.time
                )
                await asyncio.sleep(retry_after)
                continue
    
            if path.endswith('.json'):
                if isinstance(existing, str):
                    existing = json.loads(existing)
                latest = await res.json(content_type=None)
                await res.release()

                if 'diff' in tags:
                    new = self.add_new_key(existing, latest, 'diff' not in tags)
                    if existing != new:
                        if write:
                            self.bot.send(
                                self.l(
                                    'update_detected',
                                    path,
                                    default=(
                                        "'{0}' のアップデートを確認しました\n"
                                        "Detected update for '{0}'"
                                    )
                                ),
                                add_p=self.bot.time
                            )
                            if 'db' in tags:
                                self.bot.save_json(key, new)
                            else:
                                if dirs:
                                    os.makedirs(dirs, exist_ok=True)
                                await backup()
                                self.bot.save_json(f'{dirs}{key}', new, force_file=True)
                        return True, new
                else:
                    if existing != latest:
                        if write:
                            self.bot.send(
                                self.l(
                                    'update_detected',
                                    path,
                                    default=(
                                        "'{0}' のアップデートを確認しました\n"
                                        "Detected update for '{0}'"
                                    )
                                ),
                                add_p=self.bot.time
                            )
                            if 'db' in tags:
                                self.bot.save_json(key, latest)
                            else:
                                if dirs:
                                    os.makedirs(dirs, exist_ok=True)
                                await backup()
                                self.bot.save_json(f'{dirs}{key}', latest, force_file=True)
                        return True, latest
            else:
                if 'raw' in tags:
                    latest = await res.read()
                    if not is_image and sys.platform == 'win32':
                        latest = latest.replace(b'\r\n', b'\n')
                else:
                    latest = await res.text()
                    if not is_image and sys.platform == 'win32':
                        latest = latest.replace('\r\n', '\n')
                await res.release()

                if existing != latest:
                    if write:
                        self.bot.send(
                            self.l(
                                'update_detected',
                                path,
                                default=(
                                    "'{0}' のアップデートを確認しました\n"
                                    "Detected update for '{0}'"
                                )
                            ),
                            add_p=self.bot.time
                        )
                        if dirs:
                            os.makedirs(dirs, exist_ok=True)
                        await backup()
                        if 'raw' in tags:
                            async with aopen(path, 'wb') as f:
                                await f.write(latest)
                        else:
                            async with aopen(path, 'w', encoding='utf-8') as f:
                                await f.write(latest)
                    return True, latest
            return False, latest

    async def check_updates(self, dev: Optional[bool] = False) -> bool:
        if dev:
            uri = 'https://raw.githubusercontent.com/gomashio1596/Fortnite-LobbyBot-v2/dev/'
        else:
            uri = 'https://raw.githubusercontent.com/gomashio1596/Fortnite-LobbyBot-v2/main/'

        _, data = await self.check_update(uri, 'modules/auto_updater.py', write=False)

        var = {}
        exec(data, globals(), var)
        if __version__ < var['__version__']:
            self.bot.send(
                self.l(
                    'new_version',
                    var['__version__'],
                    default=(
                        "アップデートを確認しました。バージョン: {0}\n"
                        "Update detected. Version: {0}"
                    )
                ),
                add_p=self.bot.time
            )
            await var['Updater'](self.bot).update(uri)
            self.bot.send(
                self.l(
                    'update_finish',
                    var['__version__'],
                    default=(
                        "バージョン{0}へのアップデートが完了しました\n"
                        "Successfully updated to version {0}"
                    )
                ),
                add_p=[self.bot.time, lambda x: f'\n{x}']
            )
            return True
        return False

    async def update(self, uri: str) -> None:
        tasks = [
            self.bot.loop.create_task(self.check_update(uri, path))
            for path in self.updates.keys()
        ]
        if self.bot.mode == 'pc':
            tasks.extend([
                self.bot.loop.create_task(self.check_update(uri, path))
                for path in self.pc_updates.keys()
            ])
        elif self.bot.mode == 'repl':
            tasks.extend([
                self.bot.loop.create_task(self.check_update(uri, path))
                for path in self.repl_updates.keys()
            ])
        await asyncio.wait(tasks)
