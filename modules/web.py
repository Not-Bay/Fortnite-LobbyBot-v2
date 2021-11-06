# -*- coding: utf-8 -*-
import asyncio
import datetime
import json
import os
import random
import re
import string
from functools import wraps
from types import SimpleNamespace
from typing import TYPE_CHECKING, Any, Callable, Optional
from urllib.parse import urlparse

import sanic
from jinja2 import Environment, FileSystemLoader
from sanic import exceptions as exc
from sanic import response as res
from sanic.request import Request
from sanic.response import HTTPResponse
from websockets.exceptions import ConnectionClosedOK

if sanic.__version__ >= '21.9.0':
    from sanic.server.websockets.connection import WebSocketConnection
else:
    from sanic.websocket import WebSocketConnection

from .colors import yellow
from .commands import DummyMessage, MyMessage
from .localize import LocalizedText

if TYPE_CHECKING:
    from .bot import Bot
    from .client import Client


class LoginManager:
    def __init__(self, ignore: Optional[Callable] = lambda r: False) -> None:
        self.ignore = ignore
        self.id_len = 64
        self.expires_in = datetime.timedelta(minutes=10)
        self.expires = {}
        self.cookie_key = 'X-SessionId'
        self.unauthorized_handler_ = res.html('Unauthorized', status=401)

    def generate_id(self, request: Request) -> str:
        id_ = ''.join(random.choices(
            string.ascii_letters + string.digits,
            k=self.id_len
        ))
        while id_ in self.expires.keys():
            id_ = ''.join(random.choices(
                string.ascii_letters + string.digits,
                k=self.id_len
            ))
        return id_

    def authenticated(self, request: Request) -> bool:
        app = request.app
        if (not app.ctx.bot.is_error()
                and app.ctx.bot.config['web']['login_required']
                and app.ctx.bot.config['status'] == 1):
            id_ = request.cookies.get(self.cookie_key)
            if not id_:
                return False
            elif id_ in self.expires.keys():
                return True
            else:
                return False
        else:
            return True

    def login_user(self, request: Request, response: HTTPResponse) -> None:
        id_ = self.generate_id(request)
        response.cookies[self.cookie_key] = id_
        self.expires[id_] = datetime.datetime.utcnow() + self.expires_in

    def logout_user(self, request: Request, response: HTTPResponse) -> None:
        id_ = request.cookies.get(self.cookie_key)
        if id_ is not None:
            del response.cookies[self.cookie_key]
            del self.expires[id_]
            
    def login_required(self, func: Callable) -> Callable:
        @wraps(func)
        def deco(request: Request, *args: Any, **kwargs: Any):
            if self.ignore(request) or self.authenticated(request):
                return func(request, *args, **kwargs)
            elif isinstance(self.unauthorized_handler_, HTTPResponse):
                return self.unauthorized_handler_
            elif callable(self.unauthorized_handler_):
                return self.unauthorized_handler_(request, *args, **kwargs)
        return deco

    def unauthorized_handler(self, func: Callable) -> Callable:
        if asyncio.iscoroutinefunction(func) is False:
            raise ValueError('Function must be a coroutine')
        self.unauthorized_handler_ = func
        @wraps(func)
        def deco(*args: Any, **kwargs: Any):
            return func(*args, **kwargs)
        return deco


auth = LoginManager(lambda r: urlparse(r.url).path.startswith('/static'))
bp = sanic.Blueprint('app')


@auth.unauthorized_handler
async def login(request: Request, *args: Any, **kwargs: Any) -> HTTPResponse:
    app = request.app
    return await app.render_template('login.jinja')


@bp.route('/readme', methods=['GET'])
@auth.login_required
async def readme(request: Request) -> HTTPResponse:
    app = request.app
    if app.ctx.bot.config['lang'] == 'ja':
        return await res.file('README.md')
    elif app.ctx.bot.config['lang'] == 'en':
        return await res.file('README_EN.md')
    elif app.ctx.bot.config['lang'] == 'es':
        return await res.file('README_ES.md')
    exc.abort(404)


@bp.route('/<filename>', methods=['GET'])
@auth.login_required
async def openfile(request: Request, filename: str) -> HTTPResponse:
    app = request.app
    files = [
        'README.md',
        'README_EN.md',
        'README_ES.md',
        'LICENSE'
    ]
    if filename in files:
        return await app.render_template(
            'openfile.jinja',
            open_file=filename
        )

    url_path = os.path.normpath(urlparse(request.url).path)
    if url_path.startswith('/') or url_path.startswith('\\'):
        url_path = url_path[1:]
    for static in app._future_statics:
        file_or_directory = os.path.normpath(static.file_or_directory)
        path = url_path
        if path.startswith(file_or_directory):
            path = path[len(file_or_directory):]
        if path.startswith('/') or path.startswith('\\'):
            path = path[1:]
        try:
            if os.path.isfile(os.path.join(file_or_directory, re.sub('^[/]*', '', path))):
                return await app._static_request_handler(
                    file_or_directory,
                    static.use_modified_since,
                    static.use_content_range,
                    static.stream_large_files,
                    request=request,
                    content_type=static.content_type,
                    __file_uri__=path
                )
        except Exception:
            pass
        else:
            break
    exc.abort(404)


@bp.route('/docs/<lang>/<filename>', methods=['GET'])
@auth.login_required
async def openfile_docs(request: Request, lang: str, filename: str) -> HTTPResponse:
    app = request.app
    langs = [
        'en',
        'es',
        'ja'
    ]
    files = [
        'commands.md',
        'config.md',
        'custom_commands.md',
        'docs.md',
        'glossary.md',
        'pc.md',
        'repl.md',
        'replies.md',
        'setup.md'
    ]
    if lang in langs and filename in files:
        return await app.render_template(
            'openfile.jinja',
            open_file=f'docs/{lang}/{filename}'
        )
    exc.abort(404)


@bp.route('/file/<filename>', methods=['GET'])
@auth.login_required
async def file_openfile(request: Request, filename: str) -> HTTPResponse:
    files = [
        'README.md',
        'README_EN.md',
        'README_ES.md',
        'LICENSE'
    ]
    if filename in files:
        return await res.file(filename)
    exc.abort(404)


@bp.route('/file/docs/<lang>/<filename>', methods=['GET'])
@auth.login_required
async def file_openfile_docs(request: Request, lang: str, filename: str) -> HTTPResponse:
    langs = [
        'en',
        'es',
        'ja'
    ]
    files = [
        'commands.md',
        'config.md',
        'custom_commands.md',
        'docs.md',
        'glossary.md',
        'pc.md',
        'repl.md',
        'replies.md',
        'setup.md'
    ]
    if lang in langs and filename in files:
        return await res.file(f'docs/{lang}/{filename}')
    exc.abort(404)


@bp.route('/favicon.ico', methods=['GET'])
async def favicon(request: Request) -> HTTPResponse:
    app = request.app
    return res.redirect(app.url_for('static', filename='images/favicon.ico'))


@bp.route('/', methods=['GET'])
@auth.login_required
async def main(request: Request) -> HTTPResponse:
    app = request.app
    if app.ctx.bot.config['status'] == 0:
        return res.redirect('/config-editor')
    return await app.render_template(
        'index.jinja',
        version=app.ctx.bot.updater.version
    )


@bp.route('/l', methods=['POST'])
async def l(request: Request) -> HTTPResponse:
    app = request.app
    args = request.json['args']
    kwargs = request.json['kwargs']
    return res.text(app.l(request.json['text'], *args, **kwargs).get_text())


@bp.route('/login', methods=['POST'])
async def login(request: Request) -> HTTPResponse:
    app = request.app
    if auth.authenticated(request):
        return res.json({
            'success': True
        })

    if request.form.get('password', '') == app.ctx.bot.config['web']['password']:
        r = res.json({
            'success': True
        })
        auth.login_user(request, r)
        return r
    else:
        return res.json({
            'success': False
        })


@bp.route('/config-editor', methods=['GET'])
@auth.login_required
async def config_editor(request: Request) -> HTTPResponse:
    app = request.app
    return await app.render_template(
        'editor.jinja',
        key_prefix='config_',
        data=await app.ctx.bot.aload_json('config'),
        tags=app.ctx.bot.config_tags
    )


@bp.route('/commands-editor', methods=['GET'])
@auth.login_required
async def commands_editor(request: Request) -> HTTPResponse:
    app = request.app
    return await app.render_template(
        'editor.jinja',
        key_prefix='commands_',
        data=await app.ctx.bot.aload_json('commands'),
        tags=app.ctx.bot.commands_tags
    )


@bp.route('/custom-commands-editor', methods=['GET'])
@auth.login_required
async def custom_commands_editor(request: Request) -> HTTPResponse:
    app = request.app
    return await app.render_template(
        'editor.jinja',
        key_prefix='custom_commands_',
        data=await app.ctx.bot.aload_json('custom_commands'),
        tags=app.ctx.bot.custom_commands_tags
    )


@bp.route('/replies-editor', methods=['GET'])
@auth.login_required
async def replies_editor(request: Request) -> HTTPResponse:
    app = request.app
    return await app.render_template(
        'editor.jinja',
        key_prefix='replies_',
        data=await app.ctx.bot.aload_json('replies'),
        tags=app.ctx.bot.replies_tags
    )


def save(request: Request, data: dict, data_tags: list, filename: str, reload: Optional[bool] = False) -> HTTPResponse:
    app = request.app
    errors = []

    if not auth.authenticated(request):
        return res.json({
            'color': '#FF0000',
            'text': app.l('unauthorized').get_text(),
            'data': {},
            'flat_data': {},
            'errors': []
        }, status=401)

    final = {}
    final.update(data)

    def format_part(data, data_keys, prefix, tag_data, is_append = True):
        part_data = {}
        for raw_key, tags in tag_data.items():
            keys = raw_key[2:-2].split("']['")
            multiple_select_tag = app.ctx.bot.get_multiple_select_tag(tags)
            config_tag = app.ctx.bot.get_config_tag(tags)
            try:
                raw_value = request.form[f'{prefix}{raw_key}']
            except KeyError:
                raw_value = ''
            if multiple_select_tag is None and isinstance(raw_value, list):
                raw_value = raw_value[0]

            if tags[0] in [dict, list]:
                app.ctx.bot.set_dict_key(part_data, keys, tags[0]())
                if tags[0] is dict:
                    continue
            if config_tag is not None:
                suffix = ''
                if config_tag == 'client_config':
                    suffix = "['email']"
                elif config_tag == "ng_names_config":
                    suffix = "['matchmethod']"
                elif config_tag == 'ng_words_config':
                    suffix = "['count']"
                elif config_tag == 'custom_commands_config':
                    suffix = "['word']"
                elif config_tag == 'replies_config':
                    suffix = "['matchmethod']"
                values = [
                    v
                    for k, v in request.form.items()
                    if k.startswith(f'{prefix}{raw_key}') and k.endswith(suffix)
                ]
                for num in range(len(values)):
                    format_part(part_data, keys, f'{prefix}{raw_key}[{num}]',
                                getattr(app.ctx.bot, f'{config_tag}_tags'))
            else:
                if tags[0] is list and tags[1] is list:
                    raw_client_values = sum([
                        v
                        for k, v in request.form.items()
                        if k.startswith(f'{prefix}{raw_key}')
                    ], [])
                    value = [app.convert_web_value(value, tags) for value in raw_client_values]
                    app.ctx.bot.set_dict_key(part_data, keys, value)
                else:
                    value = app.convert_web_value(raw_value, tags)
                    app.ctx.bot.set_dict_key(part_data, keys, value)
        if is_append:
            app.ctx.bot.get_dict_key(data, data_keys).append(part_data)
        else:
            data.clear()
            data.update(part_data)

    format_part(final, [], '', data_tags, False)

    errors = []
    app.ctx.bot.tag_check(final, errors, '', data_tags)
    if app.ctx.bot.config['loglevel'] == 'debug':
        app.ctx.bot.send(
            app.ctx.bot.dumps(final),
            add_p=app.ctx.bot.time
        )

    if len(errors) == 0:
        final['status'] = 1
        app.ctx.bot.save_json(filename, final)

        async def rebooter():
            await asyncio.sleep(1)
            await app.ctx.bot.reboot()

        if app.ctx.bot.config['status'] == 0 or reload:
            app.ctx.loop.create_task(rebooter())

        return res.json({
            'color': '#57FF33',
            'text': app.l('saved').get_text(),
            'data': final,
            'flat_data': app.ctx.bot.flat_dict(final),
            'errors': []
        }, dumps=app.ctx.bot.dumps)
    else:
        return res.json({
            'color': '#FF0000',
            'text': app.l('error_keys').get_text(),
            'data': final,
            'flat_data': app.ctx.bot.flat_dict(final),
            'errors': errors
        }, dumps=app.ctx.bot.dumps)


def save_raw(request: Request, data: dict, data_tags: list, filename: str, reload: Optional[bool] = False) -> HTTPResponse:
    app = request.app

    if not auth.authenticated(request):
        return res.json({
            'color': '#FF0000',
            'text': app.l('unauthorized').get_text(),
            'data': {},
            'flat_data': {},
            'errors': []
        }, status=401)

    final = {}
    final.update(data)
    final.update(request.json)
    errors = []
    app.ctx.bot.tag_check(final, errors, '', data_tags)
    
    if len(errors) == 0:
        final['status'] = 1
        app.ctx.bot.save_json(filename, final)

        async def rebooter():
            await asyncio.sleep(1)
            await app.ctx.bot.reboot()

        if app.ctx.bot.config['status'] == 0 or reload:
            app.ctx.loop.create_task(rebooter())

        return res.json({
            'color': '#57FF33',
            'text': app.l('saved').get_text(),
            'data': final,
            'flat_data': app.ctx.bot.flat_dict(final),
            'errors': []
        }, dumps=app.ctx.bot.dumps)
    else:
        return res.json({
            'color': '#FF0000',
            'text': app.l('error_keys').get_text(),
            'data': final,
            'flat_data': app.ctx.bot.flat_dict(final),
            'errors': errors
        }, dumps=app.ctx.bot.dumps)


@bp.route('/config-editor/add-client', methods=['POST'])
async def config_editor_add_client(request: Request) -> HTTPResponse:
    app = request.app
    config = await app.ctx.bot.aload_json('config')
    data = {}
    for raw_key, tags in app.ctx.bot.client_config_tags.items():
        keys = raw_key[2:-2].split("']['")
        app.ctx.bot.set_dict_key(data, keys, tags[0]())
    if app.ctx.bot.get_dict_key_default(config, ['clients'], None) is None:
        app.ctx.bot.set_dict_key(config, ['clients'], [])
    app.ctx.bot.get_dict_key(config, ['clients']).append(data)
    app.ctx.bot.save_json('config', config)

    return res.empty()


@bp.route('/config-editor/add-ng-name/<num>', methods=['POST'])
async def config_editor_add_ng_name(request: Request, num: str) -> HTTPResponse:
    app = request.app
    config = await app.ctx.bot.aload_json('config')
    data = {}
    for raw_key, tags in app.ctx.bot.ng_names_config_tags.items():
        keys = raw_key[2:-2].split("']['")
        app.ctx.bot.set_dict_key(data, keys, tags[0]())
    if app.ctx.bot.get_dict_key_default(config, ['clients', int(num), 'fortnite', 'ng_names'], None) is None:
        app.ctx.bot.set_dict_key(config, ['clients', int(num), 'fortnite', 'ng_names'], [])
    app.ctx.bot.get_dict_key(
        config,
        ['clients', int(num), 'fortnite', 'ng_names']
    ).append(data)
    app.ctx.bot.save_json('config', config)

    return res.empty()


@bp.route('/config-editor/add-ng-word/<num>', methods=['POST'])
async def config_editor_add_ng_word(request: Request, num: str) -> HTTPResponse:
    app = request.app
    config = await app.ctx.bot.aload_json('config')
    data = {}
    for raw_key, tags in app.ctx.bot.ng_words_config_tags.items():
        keys = raw_key[2:-2].split("']['")
        app.ctx.bot.set_dict_key(data, keys, tags[0]())
    if app.ctx.bot.get_dict_key_default(config, ['clients', int(num), 'ng_words'], None) is None:
        app.ctx.bot.set_dict_key(config, ['clients', int(num), 'ng_words'], [])
    app.ctx.bot.get_dict_key(
        config,
        ['clients', int(num), 'ng_words']
    ).append(data)
    app.ctx.bot.save_json('config', config)

    return res.empty()


@bp.route('/config-editor/save', methods=['POST'])
async def config_editor_save(request: Request) -> HTTPResponse:
    app = request.app
    return save(request, await app.ctx.bot.aload_json('config'), app.ctx.bot.config_tags, 'config', request.args.get('reload') == 'true')


@bp.route('/config-editor/save-raw', methods=['POST'])
async def config_editor_save_raw(request: Request) -> HTTPResponse:
    app = request.app
    return save_raw(request, await app.ctx.bot.aload_json('config'), app.ctx.bot.config_tags, 'config', request.args.get('reload') == 'true')


@bp.route('/commands-editor/save', methods=['POST'])
async def commands_editor_save(request: Request) -> HTTPResponse:
    app = request.app
    return save(request, await app.ctx.bot.aload_json('commands'), app.ctx.bot.commands_tags, 'commands', request.args.get('reload') == 'true')


@bp.route('/commands-editor/save-raw', methods=['POST'])
async def commands_editor_save_raw(request: Request) -> HTTPResponse:
    app = request.app
    return save_raw(request, await app.ctx.bot.aload_json('commands') , app.ctx.bot.commands_tags, 'commands', request.args.get('reload') == 'true')


@bp.route('/custom-commands-editor/add-command', methods=['POST'])
async def custom_commands_editor_add_command(request: Request) -> HTTPResponse:
    app = request.app
    custom_commands = await app.ctx.bot.aload_json('custom_commands')
    data = {}
    for raw_key, tags in app.ctx.bot.custom_commands_config_tags.items():
        keys = raw_key[2:-2].split("']['")
        app.ctx.bot.set_dict_key(data, keys, tags[0]())
    if app.ctx.bot.get_dict_key_default(custom_commands, ['commands'], None) is None:
        app.ctx.bot.set_dict_key(custom_commands, ['commands'], [])
    app.ctx.bot.get_dict_key(
        custom_commands,
        ['commands']
    ).append(data)
    app.ctx.bot.save_json('custom_commands', custom_commands)

    return res.empty()


@bp.route('/custom-commands-editor/save', methods=['POST'])
async def custom_commands_save(request: Request) -> HTTPResponse:
    app = request.app
    return save(request, await app.ctx.bot.aload_json('custom_commands'), app.ctx.bot.custom_commands_tags, 'custom_commands', request.args.get('reload') == 'true')


@bp.route('/custom-commands-editor/save-raw', methods=['POST'])
async def custom_commands_save_raw(request: Request) -> HTTPResponse:
    app = request.app
    return save_raw(request, await app.ctx.bot.aload_json('custom_commands'), app.ctx.bot.custom_commands_tags, 'custom_commands', request.args.get('reload') == 'true')


@bp.route('/replies-editor/add-replie', methods=['POST'])
async def replies_editor_add_reply(request: Request) -> HTTPResponse:
    app = request.app
    replies = await app.ctx.bot.aload_json('replies')
    data = {}
    for raw_key, tags in app.ctx.bot.replies_config_tags.items():
        keys = raw_key[2:-2].split("']['")
        app.ctx.bot.set_dict_key(data, keys, tags[0]())
    if app.ctx.bot.get_dict_key_default(replies, ['replies'], None) is None:
        app.ctx.bot.set_dict_key(replies, ['replies'], [])
    app.ctx.bot.get_dict_key(
        replies,
        ['replies']
    ).append(data)
    app.ctx.bot.save_json('replies', replies)

    return res.empty()


@bp.route('/replies-editor/save', methods=['POST'])
async def replies_editor_save(request: Request) -> HTTPResponse:
    app = request.app
    return save(request, await app.ctx.bot.aload_json('replies'), app.ctx.bot.replies_tags, 'replies', request.args.get('reload') == 'true')


@bp.route('/replies-editor/save-raw', methods=['POST'])
async def replies_editor_save_raw(request: Request) -> HTTPResponse:
    app = request.app
    return save_raw(request, await app.ctx.bot.aload_json('replies'), app.ctx.bot.replies_tags, 'replies', request.args.get('reload') == 'true')


@bp.route('/boot-switch', methods=['GET'])
@auth.login_required
async def boot_switch(request: Request) -> HTTPResponse:
    app = request.app
    return await app.render_template('boot-switch.jinja')


@bp.route('/boot-switch/restart', methods=['POST'])
@auth.login_required
async def boot_switch_restart(request: Request) -> HTTPResponse:
    app = request.app
    await app.ctx.bot.reboot()
    return res.empty()


def client_variables(client: 'Client', full: Optional[bool] = False) -> dict:
    if full:
        app = client.bot.web
        user = getattr(client, 'user', None)
        party = getattr(client, 'party', None)
        return {
            'name': (
                f'{client.config["fortnite"]["nickname"] or user.display_name} / {user.id}'
            ) if client.is_ready() else (
                f'{client.config["fortnite"]["nickname"]} / {client.email}'
                if client.config['fortnite']['nickname'] else
                client.email
            ),
            'id': user.id if user is not None else None,
            'is_ready': client.is_ready(),
            'state': (
                'ready'
                if client.is_ready() else
                'booting'
                if client.is_booting() else
                'closed'
            ),
            'num': client.num,
            'friend_requests': [
                {
                    'name': client.name(pending, force_info=True),
                    'id': pending.id,
                    'type': 'outgoing' if pending.outgoing else 'incoming'
                } for pending in client.pending_friends
            ],
            'join_requests': [
                {
                    'name': client.name(request.requester, force_info=True),
                    'id': request.requester.id
                } for request in client.join_requests.values()
            ],
            'friends': [
                {
                    'name': client.name(friend, force_info=True),
                    'id': friend.id,
                    'is_online': friend.is_online(),
                    'is_joinable': (
                        False
                        if friend.last_presence is None or friend.last_presence.party is None else
                        not friend.last_presence.party.private
                    )
                } for friend in client.friends
            ],
            'blocked_users': [
                {
                    'name': client.name(blocked, force_info=True),
                    'id': blocked.id
                } for blocked in client.blocked_users
            ],
            'party_data': {
                'id': getattr(party, 'id', None),
                'party_size': getattr(party, 'member_count', 0),
                'party_max_size': getattr(party, 'config', {}).get('max_size', 0)
            },
            'party_members': [
                {
                    'name': client.name(member, force_info=True),
                    'display_name': member.display_name,
                    'id': member.id,
                    'position': member.position,
                    'is_leader': member.leader,
                    'is_incoming_pending': client.is_incoming_pending(member.id),
                    'is_outgoing_pending': client.is_outgoing_pending(member.id),
                    'is_friend': client.has_friend(member.id),
                    'is_blocked': client.is_blocked(member.id),
                    'outfit': {
                        'name': client.searcher.get_item(
                            client.asset('AthenaCharacter', member),
                            {}
                        ).get('name', 'TBD'),
                        'url': client.searcher.get_item(
                            client.asset('AthenaCharacter', member),
                            {}
                        ).get('url') or app.url_for('static', filename='images/outfit.jpg')
                    }
                    if client.searcher.get_item(client.asset('AthenaCharacter', member)) is not None else
                    None,
                    'backpack': {
                        'name': client.searcher.get_item(
                            client.asset('AthenaBackpack', member),
                            {}
                        ).get('name', 'TBD'),
                        'url': client.searcher.get_item(
                            client.asset('AthenaBackpack', member),
                            {}
                        ).get('url') or app.url_for('static', filename='images/backpack.jpg')
                    }
                    if client.searcher.get_item(client.asset('AthenaBackpack', member)) is not None else
                    None,
                    'pickaxe': {
                        'name': client.searcher.get_item(
                            client.asset('AthenaPickaxe', member),
                            {}
                        ).get('name', 'TBD'),
                        'url': client.searcher.get_item(
                            client.asset('AthenaPickaxe', member),
                            {}
                        ).get('url') or app.url_for('static', filename='images/pickaxe.jpg')
                    }
                    if client.searcher.get_item(client.asset('AthenaPickaxe', member)) is not None else
                    None,
                    'emote': {
                        'name': client.searcher.get_item(
                            client.asset('AthenaDance', member),
                            {}
                        ).get('name', 'TBD'),
                        'url': client.searcher.get_item(
                            client.asset('AthenaDance', member),
                            {}
                        ).get('url') or app.url_for('static', filename='images/emote.jpg')
                    }
                    if client.searcher.get_item(client.asset('AthenaDance', member)) is not None else
                    None,
                    'banner': client.bot.get_banner_url(member.banner[0]),
                    'level': member.banner[2]
                } for member in getattr(party, 'members', [])
            ],
            'client_party_member': {
                'name': client.name(party.me, force_info=True),
                'id': party.me.id,
                'position': party.me.position,
                'is_leader': party.me.leader,
                'is_incoming_pending': client.is_incoming_pending(party.me.id),
                'is_outgoing_pending': client.is_outgoing_pending(party.me.id),
                'is_friend': client.has_friend(party.me.id),
                'is_blocked': client.is_blocked(party.me.id),
                'outfit': {
                    'name': client.searcher.get_item(
                        client.asset('AthenaCharacter', party.me),
                        {}
                    ).get('name', 'TBD'),
                    'url': client.searcher.get_item(
                        client.asset('AthenaCharacter', party.me),
                        {}
                    ).get('url') or app.url_for('static', filename='images/outfit.jpg')
                }
                if client.searcher.get_item(client.asset('AthenaCharacter', party.me)) is not None else
                None,
                'backpack': {
                    'name': client.searcher.get_item(
                        client.asset('AthenaBackpack', party.me),
                        {}
                    ).get('name', 'TBD'),
                    'url': client.searcher.get_item(
                        client.asset('AthenaBackpack', party.me),
                        {}
                    ).get('url') or app.url_for('static', filename='images/backpack.jpg')
                }
                if client.searcher.get_item(client.asset('AthenaBackpack', party.me)) is not None else
                None,
                'pickaxe': {
                    'name': client.searcher.get_item(
                        client.asset('AthenaPickaxe', party.me),
                        {}
                    ).get('name', 'TBD'),
                    'url': client.searcher.get_item(
                        client.asset('AthenaPickaxe', party.me),
                        {}
                    ).get('url') or app.url_for('static', filename='images/pickaxe.jpg')
                }
                if client.searcher.get_item(client.asset('AthenaPickaxe', party.me)) is not None else
                None,
                'emote': {
                    'name': client.searcher.get_item(
                        client.asset('AthenaDance', party.me),
                        {}
                    ).get('name', 'TBD'),
                    'url': client.searcher.get_item(
                        client.asset('AthenaDance', party.me),
                        {}
                    ).get('url') or app.url_for('static', filename='images/emote.jpg')
                }
                if client.searcher.get_item(client.asset('AthenaDance', party.me)) is not None else
                None,
                'banner': client.bot.get_banner_url(party.me.banner[0]),
                'level': party.me.banner[2]
            } if party is not None else None,
            'whisper': client.whisper,
            'party_chat': (
                client.party_chat['party_chat']
                if client.party_chat['party_id'] == client.party_id else
                []
            )
        }
    else:
        user = getattr(client, 'user', None)
        return {
            'name': (
                f'{client.config["fortnite"]["nickname"] or user.display_name} / {user.id}'
            ) if client.is_ready() else (
                f'{client.config["fortnite"]["nickname"]} / {client.email}'
                if client.config['fortnite']['nickname'] else
                client.email
            ),
            'id': user.id if user is not None else None,
            'is_ready': client.is_ready(),
            'state': (
                'ready'
                if client.is_ready() else
                'booting'
                if client.is_booting() else
                'closed'
            ),
            'num': client.num
        }


async def websocket_sender(request: Request, ws: WebSocketConnection,
                           interval: Optional[int] = 1) -> None:
    app = request.app

    def variables():
        return json.dumps([
            client_variables(client)
            for client in app.ctx.bot.clients
        ])

    var = variables()
    try:
        await ws.send(var)
    except ConnectionClosedOK:
        return

    async def sender():
        nonlocal var
        while True:
            await asyncio.sleep(interval)
            new_var = variables()
            if new_var != var:
                var = new_var
                try:
                    await ws.send(var)
                except ConnectionClosedOK:
                    break

    loop = app.ctx.loop
    loop.create_task(sender())


@bp.websocket('/boot-switch/ws')
@auth.login_required
async def boot_switch_ws(request: Request, ws: WebSocketConnection) -> None:
    app = request.app
    loop = app.ctx.loop

    await websocket_sender(request, ws)

    while True:
        data = json.loads(await ws.recv())
        try:
            client = app.ctx.bot.clients[data['num']]
        except IndexError:
            continue
        if data['event'] == 'start' and not client.is_ready():
            loop.create_task(client.start())
        elif data['event'] == 'close' and client.is_ready():
            loop.create_task(client.close())


@bp.route('/clients-viewer')
@auth.login_required
async def clients_viewer(request: Request) -> HTTPResponse:
    app = request.app
    return await app.render_template('clients-viewer.jinja')


async def websocket_sender_client(request: Request, ws: WebSocketConnection,
                                  client: 'Client') -> None:
    app = request.app

    def variables():
        var = client_variables(client, full=True)

        incoming = len([i for i in var['friend_requests'] if i['type'] == 'incoming'])
        online = len([i for i in var['friends'] if i['is_online']])

        var.update(
            {
                'incoming_friend_request': app.l(
                    'incoming_friend_request',
                    incoming
                ).get_text(),
                'outgoing_friend_request': app.l(
                    'outgoing_friend_request',
                    len(var['friend_requests']) - incoming
                ).get_text(),
                'join_request': app.l(
                    'join_request',
                    len(var['join_requests'])
                ).get_text(),
                'friend': app.l(
                    'online',
                    online,
                    len(var['friends'])
                ).get_text(),
                'blocked_user': app.l(
                    'blocked_user',
                    len(var['blocked_users'])
                ).get_text(),
                'party': app.l(
                    'party_name',
                    var['party_data']['id']
                ).get_text(),
                'party_member': app.l(
                    'member',
                    var['party_data']['party_size'],
                    var['party_data']['party_max_size']
                ).get_text()
            }
        )
        return var

    def get_diff(before, after):
        def get_added(key):
            return [value for value in after[key] if value not in before[key]]

        def get_removed(key):
            return [value for value in before[key] if value not in after[key]]

        final = {
            'added': {},
            'removed': {}
        }
        for key in ['friend_requests',
                    'join_requests',
                    'friends',
                    'blocked_users',
                    'party_members']:
            final['added'][key] = get_added(key)
            final['removed'][key] = get_removed(key)
        for key in ['name',
                    'id',
                    'is_ready',
                    'state',
                    'num',
                    'incoming_friend_request',
                    'outgoing_friend_request',
                    'join_request',
                    'friend',
                    'blocked_user',
                    'party',
                    'party_member',
                    'party_data',
                    'client_party_member']:
            final[key] = after[key]
        
        return final

    client.cached_var = variables()
    client.cached_var['type'] = 'full'
    try:
        await ws.send(json.dumps(client.cached_var))
    except ConnectionClosedOK:
        return

    async def sender():
        async def store_whisper(to, data):
            try:
                data = {
                    'type': 'friend_message',
                    'to': to,
                    **data
                }
                await ws.send(json.dumps(data))
            except Exception as e:
                client.remove_event_handler('store_whisper', store_whisper)
                if e.__class__ is not ConnectionClosedOK:
                    raise

        client.add_event_handler('store_whisper', store_whisper)

        async def store_party_chat(data):
            try:
                data = {
                    'type': 'party_message',
                    **data
                }
                await ws.send(json.dumps(data))
            except Exception as e:
                client.remove_event_handler('store_party_chat', store_party_chat)
                if e.__class__ is not ConnectionClosedOK:
                    raise

        client.add_event_handler('store_party_chat', store_party_chat)

        async def clear_party_chat():
            try:
                data = {
                    'type': 'clear_party_message'
                }
                await ws.send(json.dumps(data))
            except Exception as e:
                client.remove_event_handler('clear_party_chat', clear_party_chat)
                if e.__class__ is not ConnectionClosedOK:
                    raise

        client.add_event_handler('clear_party_chat', clear_party_chat)

        while True:
            await asyncio.sleep(1)
            new_var = variables()
            if new_var != client.cached_var:
                diff = get_diff(client.cached_var, new_var)
                diff['type'] = 'diff'
                client.cached_var = new_var
                try:
                    await ws.send(json.dumps(diff))
                except ConnectionClosedOK:
                    break

    loop = app.ctx.loop
    loop.create_task(sender())


@bp.websocket('/clients-viewer/ws')
@auth.login_required
async def clients_viewer_ws(request: Request, ws: WebSocketConnection) -> None:
    app = request.app

    await websocket_sender(request, ws)

    while True:
        await ws.recv()


@bp.route('/clients-viewer/<num>')
@auth.login_required
async def clients_viewer_client(request: Request, num: str) -> HTTPResponse:
    app = request.app
    num = int(num)
    client = app.ctx.bot.get_list_index(app.ctx.bot.clients, num)
    if client is None:
        exc.abort(404)

    var = client_variables(client)

    return await app.render_template(
        'clients-viewer-client.jinja',
        num=var['num'],
        name=var['name']
    )


@bp.websocket('/clients-viewer/<num>/ws')
@auth.login_required
async def clients_viewer_client_ws(request: Request, ws: WebSocketConnection, num: str) -> None:
    app = request.app
    num = int(num)
    client = app.ctx.bot.get_list_index(app.ctx.bot.clients, num)
    if client is None:
        exc.abort(404)

    await websocket_sender_client(request, ws, client)

    def variables():
        var = client_variables(client, full=True)
        
        incoming = len([i for i in var['friend_requests'] if i['type'] == 'incoming'])
        online = len([i for i in var['friends'] if i['is_online']])

        var.update(
            {
                'incoming_friend_request': app.l(
                    'incoming_friend_request',
                    incoming
                ).get_text(),
                'outgoing_friend_request': app.l(
                    'outgoing_friend_request',
                    len(var['friend_requests']) - incoming
                ).get_text(),
                'join_request': app.l(
                    'join_request',
                    len(var['join_requests'])
                ).get_text(),
                'friend': app.l(
                    'online',
                    online,
                    len(var['friends'])
                ).get_text(),
                'blocked_user': app.l(
                    'blocked_user',
                    len(var['blocked_users'])
                ).get_text(),
                'party': app.l(
                    'party_name',
                    var['party_data']['id']
                ).get_text(),
                'party_member': app.l(
                    'member',
                    var['party_data']['party_size'],
                    var['party_data']['party_max_size']
                ).get_text()
            }
        )
        return var

    def get_diff(before, after):
        def get_added(key):
            return [value for value in after[key] if value not in before[key]]

        def get_removed(key):
            return [value for value in before[key] if value not in after[key]]

        final = {
            'added': {},
            'removed': {}
        }
        for key in ['friend_requests',
                    'join_requests',
                    'friends',
                    'blocked_users',
                    'party_members']:
            final['added'][key] = get_added(key)
            final['removed'][key] = get_removed(key)
        for key in ['name',
                    'id',
                    'is_ready',
                    'state',
                    'num',
                    'incoming_friend_request',
                    'outgoing_friend_request',
                    'join_request',
                    'friend',
                    'blocked_user',
                    'party',
                    'party_member',
                    'party_data',
                    'client_party_member']:
            final[key] = after[key]
        
        return final

    while True:
        data = json.loads(await ws.recv())
        if data['event'] == 'leave_party':
            try:
                await client.party.me.leave()
            except Exception as e:
                client.bot.debug_print_exception(e)
        elif data['event'] == 'friend_message':
            friend = client.get_friend(data['user_id'])
            if friend is None:
                continue
            try:
                await friend.send(data['content'])
            except Exception as e:
                client.debug_print_exception(e)
                continue
        elif data['event'] == 'party_message':
            party = getattr(client, 'party')
            if party is None:
                continue
            try:
                await party.send(data['content'])
            except Exception as e:
                client.debug_print_exception(e)
                continue
        elif data['event'] == 'accept_join_request':
            request = client.join_requests.get(data['user_id'])
            if request is not None:
                try:
                    await request.accept()
                except Exception as e:
                    client.bot.debug_print_exception(e)
                else:
                    if data['user_id'] in client.join_requests:
                        client.join_requests.pop(data['user_id'])
        elif data['event'] == 'decline_join_request':
            if data['user_id'] in client.join_requests:
                client.join_requests.pop(data['user_id'])
        elif data['event'] == 'join_friend':
            try:
                await client.get_friend(data['user_id']).join_party()
            except Exception as e:
                client.bot.debug_print_exception(e)
        elif data['event'] == 'command':
            mes = DummyMessage(
                client,
                WebMessage(client, data['content'], request.cookies.get('X-SessionId'))
            )
            message = MyMessage(client, mes)
            client.send(
                message.content,
                user_name=client.name(message.author),
                add_p=[lambda x: f'{client.name(message.author)} | {x}', client.time]
            )
            await client.process_command(message, client.bot.config['web']['prefix'])
            await ws.send(json.dumps({
                'type': 'response',
                'response': mes.result
            }))
        else:
            if data['event'].startswith('member_'):
                member = client.party.get_member(data['user_id'])
                if member is None:
                    continue
                func = lambda x: getattr(member, data['event'][len('member_'):])()
            else:
                func = getattr(client, data['event'])
            client.cached_var = variables()
            try:
                await func(data['user_id'])
            except Exception as e:
                client.bot.debug_print_exception(e)
            else:
                try:
                    await client.wait_for(data['wait_event'], timeout=5)
                except asyncio.TimeoutError:
                    if app.ctx.bot.config['loglevel'] == 'debug':
                        app.ctx.bot.send(
                            f"Event '{data['wait_event']}' timeout",
                            color=yellow,
                            add_d=app.ctx.bot.discord_error
                        )
                after_var = variables()
                diff = get_diff(client.cached_var, after_var)
                diff['type'] = 'diff'
                client.cached_var = after_var
                try:
                    await ws.send(json.dumps(diff))
                except ConnectionClosedOK:
                    break


class WebUser:
    def __init__(self) -> None:
        self.display_name = 'WebUser'
        self.id = 'WebUser'


class WebMessage:
    def __init__(self, client: 'Client', content: str, session_id: str) -> None:
        self.client = client
        self.content = content
        self.author = WebUser()
        self.created_at = datetime.datetime.utcnow()


class Web(sanic.Sanic):
    def __init__(self, bot: 'Bot', *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        if sanic.__version__ < '21.3.1':
            self.ctx = SimpleNamespace()
        self.ctx.bot = bot
        self.ctx.loop = self.ctx.bot.loop

        self.ctx.env = Environment(
            loader=FileSystemLoader('./templates', encoding='utf8'),
            extensions=['jinja2.ext.do'],
            enable_async=True
        )
        self.ctx.env.globals.update({
            'client': self,
            'isinstance': isinstance,
            'enumerate': enumerate,
            'getattr': getattr,
            'str_key_to_list': self.str_key_to_list,
            'list_key_to_str': self.list_key_to_str,
            'convert_list_str': self.convert_list_str,
            'len': len,
            'map': map,
            'str': str,
            'dict': dict,
            'list': list,
            'none': None,
            'repr': repr
        })
        self.ctx.route_prefix = 'route_'

        self.ctx.secret_key = os.urandom(32)
        self.blueprint(bp)
        self.static('/static', './static')

    def l(self, key: str, *args: tuple, default: Optional[str] = '', **kwargs: dict) -> LocalizedText:
        return LocalizedText(self.ctx.bot, ['web', key], default, *args, **kwargs)

    def str_key_to_list(self, text: str) -> list:
        return [
            i[1:-1]
            if i.startswith("'") and i.endswith("'") else
            int(i)
            for i in text[1:-1].split('][')
            if i != ''
        ]

    def list_key_to_str(self, value: list) -> str:
        return ''.join([f"[{repr(i)}]" for i in value])

    def convert_list_str(self, value: list) -> str:
        return '\n'.join([str(i).replace('\n', '\\n') for i in value])

    def convert_web_value(self, raw_value: Any, tags: list) -> Any:
        select_tag = self.ctx.bot.get_select_tag(tags)
        multiple_select_tag = self.ctx.bot.get_multiple_select_tag(tags)

        # Fix type
        value = raw_value
        if tags[0] is dict:
            pass
        elif tags[0] is list:
            if value == '':
                if 'can_be_none' in tags:
                    value = None
                else:
                    value = []
            else:
                if tags[1] in [str, list]:
                    if multiple_select_tag is None:
                        value = [i.replace('\\\\', '\\') for i in re.split(r'\r\n|\n', value)]
                elif tags[1] is int:
                    value = [int(i) for i in re.split(r'\r\n|\n', value)]
        elif tags[0] is str:
            if value == '':
                if 'can_be_none' in tags:
                    value = None
                else:
                    value = ''
            else:
                value = value
        elif tags[0] is int:
            if value == '':
                if 'can_be_none' in tags:
                    value = None
                else:
                    value = 0
            else:
                value = int(value)
        elif tags[0] is float:
            if value == '':
                if 'can_be_none' in tags:
                    value = None
                else:
                    value = 0
            else:
                value = float(value)

        # Fix tag values
        def fix_tag_value(val):
            if select_tag is not None:
                for v in getattr(self.ctx.bot, select_tag):
                    if v['value'] == val:
                        return v['real_value']
            if multiple_select_tag is not None:
                for v in getattr(self.ctx.bot, multiple_select_tag):
                    if v['value'] == val:
                        return v['real_value']
            return val

        if isinstance(value, list):
            value = [fix_tag_value(v) for v in value]
            if None in value:
                value = None
        else:
            value = fix_tag_value(value)

        return value

    async def render_template(self, filename: str, *args: Any, **kwargs: Any) -> HTTPResponse:
        template = self.ctx.env.get_template(filename)
        return res.html(await template.render_async(*args, **kwargs))
