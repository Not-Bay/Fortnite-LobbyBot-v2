# -*- coding: utf-8 -*-
import asyncio
import datetime
import importlib
import io
import json
import logging
import os
import platform
import re
import subprocess
import sys
import textwrap
import traceback
from contextlib import redirect_stderr, redirect_stdout
from functools import partial
from glob import glob
from logging import WARNING, getLogger
from typing import Any, Callable, List, Optional, Tuple, Union

import aiohttp
from aioconsole import ainput
from aiofiles import open as aopen
from aiofiles.os import remove as aremove
from tzlocal import get_localzone

from .auth import MyAdvancedAuth
from .auto_updater import Updater
from .client import Client, MyClientParty, MyClientPartyMember
from .colors import cyan, green, yellow
from .commands import Command, DefaultCommands, MyMessage, PartyPrivacy
from .cosmetics import CaseInsensitiveDict, Searcher
from .discord_client import DiscordClient
from .encoder import MyJSONEncoder
from .formatter import EvalFormatter
from .http import HTTPClient
from .localize import LocalizedText
from .web import Web, WebMessage, WebUser
from .webhook import WebhookClient

if (os.getenv('REPLIT_DB_URL') is not None
        and os.getcwd().startswith('/home/runner')
        and sys.platform == 'linux'):
    from replit import db
else:
    db = None

discord = importlib.import_module('discord')
fortnitepy = importlib.import_module('fortnitepy')
_ = importlib.import_module('pykakasi')
kakasi = _.kakasi


Message = Union[
    fortnitepy.FriendMessage,
    fortnitepy.PartyMessage,
    discord.Message,
    WebMessage
]
Author = Union[
    fortnitepy.Friend,
    fortnitepy.PartyMember,
    discord.User,
    discord.Member,
    WebUser
]


class Bot:
    BACKEND_TO_API_CONVERTER = {
        'AthenaBackpack': 'backpack',
        'AthenaPickaxe': 'pickaxe',
        'AthenaItemWrap': 'wrap',
        'AthenaGlider': 'glider',
        'AthenaCharacter': 'outfit',
        'AthenaPet': 'pet',
        'AthenaMusicPack': 'music',
        'AthenaLoadingScreen': 'loadingscreen',
        'AthenaDance': 'emote',
        'AthenaSpray': 'spray',
        'AthenaEmoji': 'emoji',
        'AthenaSkyDiveContrail': 'contrail',
        'AthenaPetCarrier': 'petcarrier',
        'AthenaToy': 'toy',
        'AthenaConsumableEmote': 'consumableemote',
        'AthenaBattleBus': 'battlebus',
        'AthenaVictoryPose': 'ridethepony',
        'BannerToken': 'banner'
    }
    API_TO_BACKEND_CONVERTER = {
        v: k for k, v in BACKEND_TO_API_CONVERTER.items()
    }
    BACKEND_TO_KEY_CONVERTER = {
        'AthenaBackpack': 'backpack',
        'AthenaPickaxe': 'pickaxe',
        'AthenaItemWrap': 'wrap',
        'AthenaGlider': 'glider',
        'AthenaCharacter': 'outfit',
        'AthenaPet': 'backpack',
        'AthenaMusicPack': 'music',
        'AthenaLoadingScreen': 'loadingscreen',
        'AthenaDance': 'emote',
        'AthenaSpray': 'emote',
        'AthenaEmoji': 'emote',
        'AthenaSkyDiveContrail': 'contrail',
        'AthenaPetCarrier': 'backpack',
        'AthenaToy': 'emote',
        'AthenaConsumableEmote': 'emote',
        'AthenaBattleBus': 'battlebus',
        'AthenaVictoryPose': 'emote',
        'BannerToken': 'banner'
    }
    BACKEND_TO_ID_CONVERTER = {
        'AthenaCharacter': 'CID',
        'AthenaBackpack': 'BID',
        'AthenaPetCarrier': 'PetCarrier',
        'AthenaPet': 'PetID',
        'AthenaPickaxe': 'Pickaxe_ID',
        'AthenaDance': 'EID',
        'AthenaEmoji': 'Emoji',
        'AthenaToy': 'Toy',
        'AthenaConsumableEmote': 'EID',
    }
    VARIANT_FORMATS = [
        'Mat',
        'Stage',
        'Emissive',
        'Stage',
        'Particle'
        'Numeric.',
        'Color.'
    ]

    def __init__(self, mode: str, loop: asyncio.AbstractEventLoop,
                 dev: Optional[bool] = False,
                 use_device_code: Optional[bool] = False,
                 use_device_auth: Optional[bool] = False) -> None:
        self.mode = mode
        self.loop = loop
        self.dev = dev
        self.use_device_code = use_device_code
        self.use_device_auth = use_device_auth

        self.clients = []
        self.updater = Updater(self)
        self.web = Web(self, __name__)
        self.web_text = ''
        self.server = None
        self.lang_dir = 'lang'
        self.item_dir = 'item'
        os.makedirs(self.item_dir, exist_ok=True)

        self.booted_at = None
        self.email_pattern = re.compile(
            r'[a-zA-Z0-9.+-_]+@[a-zA-Z0-9-_]+\.[a-zA-Z0-9]+'
        )
        self.return_pattern = re.compile(
            r'(?P<space>\s*)(return|return\s+(?P<text>.*))\s*'
        )
        self.formatter = EvalFormatter()
        self.kakasi = kakasi()
        self.kakasi.setMode('J', 'H')
        self.converter = self.kakasi.getConverter()
        self.localize = None

        self.all_commands = {
            attr.name: attr
            for attr in DefaultCommands.__dict__.values()
            if isinstance(attr, Command)
        }

        self.none_data = {
            'real_value': None,
            'value': 'null',
            'display_value': self.l('none_none', default='null')
        }
        self.select_bool = [
            {
                'real_value': True,
                'value': 'true',
                'display_value': self.l('bool_true', default='true')
            },
            {
                'real_value': False,
                'value': 'false',
                'display_value': self.l('bool_false', default='false')
            }
        ]
        self.select_event = [
            {
                'real_value': i,
                'value': i,
                'display_value': self.l(f'event_{i}', default=i)
            } for i in ['me', 'user']
        ]
        self.select_platform = [
            {
                'real_value': i,
                'value': i,
                'display_value': self.l(f'platform_{i}', default=i)
            } for i in ['WIN', 'MAC', 'PSN', 'PS5', 'XBL',
                        'XBX', 'XBS', 'SWT', 'IOS', 'AND']
        ]
        self.select_privacy = [
            {
                'real_value': i,
                'value': i,
                'display_value': self.l(f'privacy_{i.lower()}', default=i.upper())
            } for i in ['PUBLIC', 'FRIENDS_ALLOW_FRIENDS_OF_FRIENDS',
                        'FRIENDS', 'PRIVATE_ALLOW_FRIENDS_OF_FRIENDS',
                        'PRIVATE']
        ]
        self.select_status = [
            {
                'real_value': i,
                'value': i,
                'display_value': self.l(f'status_type_{i}', default=i)
            } for i in ['playing', 'streaming', 'listening', 'watching', 'competing']
        ]
        self.select_matchmethod = [
            {
                'real_value': i,
                'value': i,
                'display_value': self.l(f'matchmethod_{i}', default=i)
            } for i in ['full', 'contains', 'starts', 'ends']
        ]
        self.select_lang = [
            {
                'real_value': re.sub(r'lang(\\|/)', '', i).replace('.json', ''),
                'value': re.sub(r'lang(\\|/)', '', i).replace('.json', ''),
                'display_value': re.sub(r'lang(\\|/)', '', i).replace('.json', '')
            } for i in glob('lang/*.json') if not i.endswith('_old.json')
        ]
        self.select_api_lang = [
            {
                'real_value': i,
                'value': i,
                'display_value': i
            } for i in ['ar', 'de', 'en', 'es', 'es-419', 'fr', 'it', 'ja',
                        'ko', 'pl', 'pt-BR', 'ru', 'tr', 'zh-CN', 'zh-Hant']
        ]
        self.select_api = [
            {
                'real_value': i,
                'value': i,
                'display_value': i
            } for i in ['BenBot', 'Fortnite-API', 'FortniteApi.io']
        ]
        self.select_loglevel = [
            {
                'real_value': i,
                'value': i,
                'display_value': self.l(f'loglevel_{i}', default=i)
            } for i in ['normal', 'info', 'debug']
        ]
        self.select_run_when = [
            {
                'real_value': i,
                'value': i,
                'display_value': self.l(f'run_when_{i}', default=i)
            } for i in ['before_command', 'after_command']
        ]

        self.multiple_select_user_type = [
            {
                'real_value': i,
                'value': i,
                'display_value': self.l(f'multiple_select_user_{i}', default=i)
            } for i in ['user', 'whitelist', 'blacklist', 'owner', 'bot']
        ]
        self.multiple_select_user_operation = [
            {
                'real_value': i,
                'value': i,
                'display_value': self.l(f'multiple_select_operation_{i}', default=i)
            } for i in ['kick', 'chatban', 'remove', 'block', 'blacklist']
        ]
        self.multiple_select_platform = self.select_platform

        self.config = None
        self.config_tags = {
            "['clients']": [list, dict, 'client_config'],
            "['discord']": [dict],
            "['discord']['enabled']": [bool, 'select_bool'],
            "['discord']['token']": [str],
            "['discord']['owner']": [list, str, 'can_be_none'],
            "['discord']['channels']": [list, str],
            "['discord']['status']": [str],
            "['discord']['status_type']": [str, 'select_status'],
            "['discord']['chat_max']": [int, 'can_be_none'],
            "['discord']['chat_max_for']": [list, str, 'multiple_select_user_type', 'can_be_none'],
            "['discord']['command_enable_for']": [list, str, 'multiple_select_user_type', 'can_be_none'],
            "['discord']['blacklist']": [list, str],
            "['discord']['whitelist']": [list, str],
            "['discord']['prefix']": [list, str, 'can_be_none'],
            "['discord']['exec']": [dict],
            "['discord']['exec']['ready']": [list, str, 'can_be_none', 'accept_empty'],
            "['web']": [dict],
            "['web']['enabled']": [bool, 'select_bool'],
            "['web']['ip']": [str],
            "['web']['port']": [int],
            "['web']['password']": [str],
            "['web']['login_required']": [bool, 'select_bool'],
            "['web']['command_web']": [bool, 'select_bool'],
            "['web']['access_log']": [bool, 'select_bool'],
            "['web']['prefix']": [list, str, 'can_be_none'],
            "['check_update_on_startup']": [bool, 'select_bool'],
            "['restart_in']": [int, 'can_be_none'],
            "['lang']": [str, 'select_lang'],
            "['search_lang']": [str, 'select_api_lang'],
            "['sub_search_lang']": [str, 'select_api_lang'],
            "['api']": [str, 'select_api'],
            "['api_key']": [str, 'can_be_none'],
            "['discord_log']": [str, 'can_be_none'],
            "['omit_over2000']": [bool, 'select_bool'],
            "['skip_if_overflow']": [bool, 'select_bool'],
            "['hide_email']": [bool, 'select_bool'],
            "['hide_password']": [bool, 'select_bool'],
            "['hide_token']": [bool, 'select_bool'],
            "['hide_webhook']": [bool, 'select_bool'],
            "['no_logs']": [bool, 'select_bool'],
            "['loglevel']": [str, 'select_loglevel'],
            "['debug']": [bool, 'select_bool']
        }
        self.client_config_tags = {
            "['fortnite']": [dict],
            "['fortnite']['email']": [str, 'lambda x: x and self.email_pattern.match(x) is not None'],
            "['fortnite']['nickname']": [str, 'can_be_none'],
            "['fortnite']['owner']": [list, str, 'can_be_none'],
            "['fortnite']['outfit']": [str, 'can_be_none'],
            "['fortnite']['outfit_style']": [list, str, 'can_be_none'],
            "['fortnite']['ng_outfits']": [list, str, 'can_be_none'],
            "['fortnite']['ng_outfit_for']": [list, str, 'multiple_select_user_type', 'can_be_none'],
            "['fortnite']['ng_outfit_operation']": [list, str, 'multiple_select_user_operation', 'can_be_none'],
            "['fortnite']['ng_outfit_reply']": [str, 'can_be_none'],
            "['fortnite']['join_outfit']": [str, 'can_be_none'],
            "['fortnite']['join_outfit_style']": [list, str, 'can_be_none'],
            "['fortnite']['join_outfit_on']": [str, 'select_event'],
            "['fortnite']['leave_outfit']": [str, 'can_be_none'],
            "['fortnite']['leave_outfit_style']": [list, str, 'can_be_none'],
            "['fortnite']['leave_outfit_on']": [str, 'select_event'],
            "['fortnite']['outfit_mimic_for']": [list, str, 'multiple_select_user_type', 'can_be_none'],
            "['fortnite']['outfit_lock_for']": [list, str, 'multiple_select_user_type', 'can_be_none'],
            "['fortnite']['backpack']": [str, 'can_be_none'],
            "['fortnite']['backpack_style']": [list, str, 'can_be_none'],
            "['fortnite']['ng_backpacks']": [list, str, 'can_be_none'],
            "['fortnite']['ng_backpack_for']": [list, str, 'multiple_select_user_type', 'can_be_none'],
            "['fortnite']['ng_backpack_operation']": [list, str, 'multiple_select_user_operation', 'can_be_none'],
            "['fortnite']['ng_backpack_reply']": [str, 'can_be_none'],
            "['fortnite']['join_backpack']": [str, 'can_be_none'],
            "['fortnite']['join_backpack_style']": [list, str, 'can_be_none'],
            "['fortnite']['join_backpack_on']": [str, 'select_event'],
            "['fortnite']['leave_backpack']": [str, 'can_be_none'],
            "['fortnite']['leave_backpack_style']": [list, str, 'can_be_none'],
            "['fortnite']['leave_backpack_on']": [str, 'select_event'],
            "['fortnite']['backpack_mimic_for']": [list, str, 'multiple_select_user_type', 'can_be_none'],
            "['fortnite']['backpack_lock_for']": [list, str, 'multiple_select_user_type', 'can_be_none'],
            "['fortnite']['pickaxe']": [str, 'can_be_none'],
            "['fortnite']['pickaxe_style']": [list, str, 'can_be_none'],
            "['fortnite']['do_point']": [bool, 'select_bool'],
            "['fortnite']['ng_pickaxes']": [list, str, 'can_be_none'],
            "['fortnite']['ng_pickaxe_for']": [list, str, 'multiple_select_user_type', 'can_be_none'],
            "['fortnite']['ng_pickaxe_operation']": [list, str, 'multiple_select_user_operation', 'can_be_none'],
            "['fortnite']['ng_pickaxe_reply']": [str, 'can_be_none'],
            "['fortnite']['join_pickaxe']": [str, 'can_be_none'],
            "['fortnite']['join_pickaxe_style']": [list, str, 'can_be_none'],
            "['fortnite']['join_pickaxe_on']": [str, 'select_event'],
            "['fortnite']['leave_pickaxe']": [str, 'can_be_none'],
            "['fortnite']['leave_pickaxe_style']": [list, str, 'can_be_none'],
            "['fortnite']['leave_pickaxe_on']": [str, 'select_event'],
            "['fortnite']['pickaxe_mimic_for']": [list, str, 'multiple_select_user_type', 'can_be_none'],
            "['fortnite']['pickaxe_lock_for']": [list, str, 'multiple_select_user_type', 'can_be_none'],
            "['fortnite']['emote']": [str],
            "['fortnite']['emote_section']": [int, 'can_be_none'],
            "['fortnite']['repeat_emote_when_join']": [bool, 'select_bool'],
            "['fortnite']['ng_emotes']": [list, str, 'can_be_none'],
            "['fortnite']['ng_emote_for']": [list, str, 'multiple_select_user_type', 'can_be_none'],
            "['fortnite']['ng_emote_operation']": [list, str, 'multiple_select_user_operation', 'can_be_none'],
            "['fortnite']['ng_emote_reply']": [str, 'can_be_none'],
            "['fortnite']['join_emote']": [str, 'can_be_none'],
            "['fortnite']['join_emote_section']": [int, 'can_be_none'],
            "['fortnite']['join_emote_on']": [str, 'select_event'],
            "['fortnite']['leave_emote']": [str, 'can_be_none'],
            "['fortnite']['leave_emote_section']": [int, 'can_be_none'],
            "['fortnite']['leave_emote_on']": [str, 'select_event'],
            "['fortnite']['emote_mimic_for']": [list, str, 'multiple_select_user_type', 'can_be_none'],
            "['fortnite']['emote_lock_for']": [list, str, 'multiple_select_user_type', 'can_be_none'],
            "['fortnite']['leave_delay_for']": [float],
            "['fortnite']['refresh_on_reload']": [bool, 'select_bool'],
            "['fortnite']['party']": [dict],
            "['fortnite']['party']['privacy']": [str, 'select_privacy'],
            "['fortnite']['party']['max_size']": [int, 'lambda x: 1 <= x <= 16'],
            "['fortnite']['party']['allow_swap']": [bool, 'select_bool'],
            "['fortnite']['party']['playlist']": [str],
            "['fortnite']['party']['disable_voice_chat']": [bool, 'select_bool'],
            "['fortnite']['avatar_id']": [str, 'can_be_none'],
            "['fortnite']['avatar_color']": [str, 'can_be_multiple', 'lambda x: x and (len(x.split(",")) >= 3) if "," in x else (getattr(fortnitepy.KairosBackgroundColorPreset, x.upper(), None) is not None)'],  # noqa
            "['fortnite']['banner_id']": [str],
            "['fortnite']['banner_color']": [str],
            "['fortnite']['level']": [int],
            "['fortnite']['tier']": [int],
            "['fortnite']['platform']": [str, 'select_platform'],
            "['fortnite']['ng_platforms']": [list, str, 'multiple_select_platform', 'can_be_none'],
            "['fortnite']['ng_platform_for']": [list, str, 'multiple_select_user_type', 'can_be_none'],
            "['fortnite']['ng_platform_operation']": [list, str, 'multiple_select_user_operation', 'can_be_none'],
            "['fortnite']['ng_platform_reply']": [str, 'can_be_none'],
            "['fortnite']['ng_names']": [list, dict, 'ng_names_config'],
            "['fortnite']['ng_name_for']": [list, str, 'multiple_select_user_type', 'can_be_none'],
            "['fortnite']['ng_name_operation']": [list, str, 'multiple_select_user_operation', 'can_be_none'],
            "['fortnite']['ng_name_reply']": [str, 'can_be_none'],
            "['fortnite']['status']": [str],
            "['fortnite']['accept_invite_for']": [list, str, 'multiple_select_user_type', 'can_be_none'],
            "['fortnite']['decline_invite_when']": [list, str, 'multiple_select_user_type', 'can_be_none'],
            "['fortnite']['invite_interval']": [float, 'can_be_none'],
            "['fortnite']['invite_interval_for']": [list, str, 'multiple_select_user_type', 'can_be_none'],
            "['fortnite']['accept_friend_for']": [list, str, 'multiple_select_user_type', 'can_be_none'],
            "['fortnite']['send_friend_request']": [bool, 'select_bool'],
            "['fortnite']['whisper_enable_for']": [list, str, 'multiple_select_user_type', 'can_be_none'],
            "['fortnite']['party_chat_enable_for']": [list, str, 'multiple_select_user_type', 'can_be_none'],
            "['fortnite']['permission_command_operation']": [list, str, 'multiple_select_user_operation', 'can_be_none'],
            "['fortnite']['accept_join_for']": [list, str, 'multiple_select_user_type', 'can_be_none'],
            "['fortnite']['join_message']": [list, str, 'can_be_none', 'accept_empty'],
            "['fortnite']['join_message_whisper']": [list, str, 'can_be_none', 'accept_empty'],
            "['fortnite']['random_message']": [list, list, str, 'can_be_none', 'accept_empty'],
            "['fortnite']['random_message_whisper']": [list, list, str, 'can_be_none', 'accept_empty'],
            "['fortnite']['chat_max']": [int, 'can_be_none'],
            "['fortnite']['chat_max_for']": [list, str, 'multiple_select_user_type', 'can_be_none'],
            "['fortnite']['chat_max_operation']": [list, str, 'multiple_select_user_operation', 'can_be_none'],
            "['fortnite']['kick_disconnect']": [bool, 'select_bool'],
            "['fortnite']['kick_in_match']": [bool, 'select_bool'],
            "['fortnite']['hide_for']": [list, str, 'multiple_select_user_type', 'can_be_none'],
            "['fortnite']['blacklist']": [list, str],
            "['fortnite']['blacklist_operation']": [list, str, 'multiple_select_user_operation', 'can_be_none'],
            "['fortnite']['whitelist']": [list, str],
            "['fortnite']['invitelist']": [list, str],
            "['fortnite']['botlist']": [list, str],
            "['fortnite']['botlist_operation']": [list, str, 'multiple_select_user_operation', 'can_be_none'],
            "['fortnite']['prefix']": [list, str, 'can_be_none'],
            "['fortnite']['exec']": [dict],
            "['fortnite']['exec']['ready']": [list, str, 'can_be_none'],
            "['fortnite']['exec']['party_join_request']": [list, str, 'can_be_none'],
            "['fortnite']['exec']['party_invite']": [list, str, 'can_be_none'],
            "['fortnite']['exec']['friend_request']": [list, str, 'can_be_none'],
            "['fortnite']['exec']['friend_add']": [list, str, 'can_be_none'],
            "['fortnite']['exec']['friend_remove']": [list, str, 'can_be_none'],
            "['fortnite']['exec']['party_member_join']": [list, str, 'can_be_none'],
            "['fortnite']['exec']['party_member_leave']": [list, str, 'can_be_none'],
            "['fortnite']['exec']['party_member_confirm']": [list, str, 'can_be_none'],
            "['fortnite']['exec']['party_member_kick']": [list, str, 'can_be_none'],
            "['fortnite']['exec']['party_member_promote']": [list, str, 'can_be_none'],
            "['fortnite']['exec']['party_update']": [list, str, 'can_be_none'],
            "['fortnite']['exec']['party_member_update']": [list, str, 'can_be_none'],
            "['fortnite']['exec']['party_member_disconnect']": [list, str, 'can_be_none'],
            "['discord']": [dict],
            "['discord']['enabled']": [bool, 'select_bool'],
            "['discord']['token']": [str],
            "['discord']['owner']": [list, str, 'can_be_none'],
            "['discord']['channels']": [list, str],
            "['discord']['status']": [str],
            "['discord']['status_type']": [str, 'select_status'],
            "['discord']['chat_max']": [int, 'can_be_none'],
            "['discord']['chat_max_for']": [list, str, 'multiple_select_user_type', 'can_be_none'],
            "['discord']['command_enable_for']": [list, str, 'multiple_select_user_type', 'can_be_none'],
            "['discord']['blacklist']": [list, str],
            "['discord']['whitelist']": [list, str],
            "['discord']['prefix']": [list, str, 'can_be_none'],
            "['discord']['exec']": [dict],
            "['discord']['exec']['ready']": [list, str, 'can_be_none'],
            "['ng_words']": [list, dict, 'ng_words_config'],
            "['ng_word_for']": [list, str, 'multiple_select_user_type', 'can_be_none'],
            "['ng_word_operation']": [list, str, 'multiple_select_user_operation', 'can_be_none'],
            "['ng_word_reply']": [str, 'can_be_none'],
            "['relogin_in']": [int, 'can_be_none'],
            "['search_max']": [int, 'can_be_none'],
            "['no_logs']": [bool, 'select_bool'],
            "['loglevel']": [str, 'select_loglevel'],
            "['discord_log']": [str, 'can_be_none'],
            "['omit_over2000']": [bool, 'select_bool'],
            "['skip_if_overflow']": [bool, 'select_bool'],
            "['case_insensitive']": [bool, 'select_bool'],
            "['convert_kanji']": [bool, 'select_bool']
        }
        self.ng_names_config_tags = {
            "['matchmethod']": [str, 'select_matchmethod'],
            "['word']": [str]
        }
        self.ng_words_config_tags = {
            "['count']": [int],
            "['matchmethod']": [str, 'select_matchmethod'],
            "['words']": [list, str]
        }

        self.commands = None
        tags = [list, str, 'can_be_multiple']
        tags2 = [list, str, 'can_be_multiple', 'lambda x: len(x) > 0']
        self.commands_tags = {
            **{
                "['whitelist_commands']": tags,
                "['user_commands']": tags,
                "['prefix_to_item_search']": [bool, 'select_bool'],
                "['command']": tags2,
                "['ng_word']": tags2,
                "['most']": tags2,
                "['user']": tags2,
                "['whitelist']": tags2,
                "['blacklist']": tags2,
                "['owner']": tags2,
                "['bot']": tags2,
                "['null']": tags2,
                "['operation_kick']": tags2,
                "['operation_chatban']": tags2,
                "['operation_remove']": tags2,
                "['operation_block']": tags2,
                "['operation_blacklist']": tags2,
                "['add']": tags2,
                "['remove']": tags2,
                "['true']": tags2,
                "['false']": tags2,
                "['accept']": tags2,
                "['decline']": tags2,
                "['me']": tags2,
                "['public']": tags2,
                "['friends_allow_friends_of_friends']": tags2,
                "['friends']": tags2,
                "['private_allow_friends_of_friends']": tags2,
                "['private']": tags2,
                "['outfit']": tags2,
                "['backpack']": tags2,
                "['pickaxe']": tags2,
                "['save']": tags2,
                "['load']": tags2,
                "['commands']": [dict]
            },
            **{
                f"['commands']['{command}']": tags
                for command in self.all_commands.keys()
            }
        }

        self.custom_commands = None
        self.custom_commands_tags = {
            "['run_when']": [str, 'select_run_when'],
            "['commands']": [list, dict, 'custom_commands_config']
        }
        self.custom_commands_config_tags = {
            "['word']": [str],
            "['allow_for']": [list, str, 'multiple_select_user_type', 'can_be_none'],
            "['run']": [list, str, 'can_be_multiple']
        }

        self.replies = None
        self.replies_tags = {
            "['run_when']": [str, 'select_run_when'],
            "['prefix_to_replies']": [bool, 'select_bool'],
            "['replies']": [list, dict, 'replies_config']
        }
        self.replies_config_tags = {
            "['matchmethod']": [str, 'select_matchmethod'],
            "['word']": [str],
            "['reply']": [list, str, 'can_be_multiple', 'accept_empty'],
            "['ct']": [int, 'can_be_none']
        }

        self.cosmetic_presets = None

        self.config_item_pattern = re.compile(
            r"<Item name='(?P<name>.+)' "
            r"id='(?P<id>.+)' "
            r"path='(?P<path>.+)'>"
        )
        self.config_playlist_pattern = re.compile(
            r"<Playlist name='(?P<name>.+)' "
            r"id='(?P<id>.+)'>"
        )
        self.config_variant_pattern = re.compile(
            r"<Variant name='(?P<name>.+)' "
            r"channel='(?P<channel>.+)' "
            r"tag='(?P<tag>.+)'>"
        )

        self.http = HTTPClient(aiohttp.ClientSession())
        self.webhook = None
        self.discord_client = None

    @property
    def loaded_clients(self) -> List[Client]:
        return [client for client in self.clients if client.is_ready()]

    @property
    def loaded_client_ids(self) -> List[Client]:
        return [client.user.id for client in self.loaded_clients]

    def add_command(self, command: Command) -> None:
        if not isinstance(command, Command):
            raise TypeError(f'command argument must be instance of {Command.__name__}')
        if command.name in self.all_commands:
            raise ValueError(f"Command '{command.name}' is already registered")

        self.all_commands[command.name] = command
        for client in self.clients:
            client.add_command(command)

    def is_error(self) -> bool:
        return (
            self.error_config
            or self.error_commands
            or self.error_custom_commands
            or self.error_replies
        )

    def get_device_auth_details(self) -> dict:
        if self.isfile('device_auths'):
            return self.load_json('device_auths')
        else:
            return {}

    def store_device_auth_details(self, email: str, details: dict) -> None:
        existing = self.get_device_auth_details()
        existing[email.lower()] = details
        self.save_json('device_auths', existing)

    def get_refresh_tokens(self) -> dict:
        if self.isfile('refresh_tokens'):
            return self.load_json('refresh_tokens')
        else:
            return {}

    def store_refresh_token(self, email: str, refresh_token: str) -> None:
        existing = self.get_refresh_tokens()
        existing[email.lower()] = refresh_token
        self.save_json('refresh_tokens', existing)

    def get_cosmetic_presets(self) -> dict:
        if self.isfile('cosmetic_presets'):
            return self.load_json('cosmetic_presets')
        else:
            return {}

    async def store_cosmetic_presets(self, account_id: str, details: dict) -> None:
        existing = self.get_cosmetic_presets()
        existing[account_id] = details
        self.save_json('cosmetic_presets', existing)

    def get_command_stats(self) -> dict:
        if self.isfile('command_stats'):
            return self.load_json('command_stats')
        else:
            return {}

    def store_command_stats(self) -> None:
        self.save_json('command_stats', self.command_stats)

    def convert_td(self, td: datetime.timedelta) -> Tuple[int, int, int, int]:
        m, s = divmod(td.seconds, 60)
        h, m = divmod(m, 60)
        return td.days, h, m, s

    def isfile(self, key: str, force_file: Optional[bool] = False) -> bool:
        if self.mode == 'repl' and not force_file:
            if db.get(key) is None:
                return False
        else:
            if not os.path.isfile(f'{key}.json'):
                return False
        return True

    def remove(self, key: str, force_file: Optional[bool] = False) -> None:
        if self.mode == 'repl' and not force_file:
            try:
                del db[key]
            except KeyError as e:
                raise FileNotFoundError from e
        else:
            os.remove(f'{key}.json')

    async def aremove(self, key: str, force_file: Optional[bool] = False) -> None:
        if self.mode == 'repl' and not force_file:
            try:
                del db[key]
            except KeyError as e:
                raise FileNotFoundError from e
        else:
            await aremove(f'{key}.json')

    def rename(self, key_src: str, key_dst: str, force_file: Optional[bool] = False) -> None:
        if self.mode == 'repl' and not force_file:
            try:
                db[key_dst] = db[key_src]
                del db[key_src]
            except KeyError as e:
                raise FileNotFoundError from e
        else:
            os.rename(f'{key_src}.json', f'{key_dst}.json')

    def load_json(self, key: str, force_file: Optional[bool] = False) -> Union[dict, list]:
        if self.mode == 'repl' and not force_file:
            data = db[key]['value']
            if isinstance(data, str):
                return json.loads(db[key]['value'])
            return data
        else:
            try:
                with open(f'{key}.json', encoding='utf-8') as f:
                    data = f.read()
            except UnicodeDecodeError:
                try:
                    with open(f'{key}.json', encoding='utf-8-sig') as f:
                        data = f.read()
                except UnicodeDecodeError:
                    with open(f'{key}.json', encoding='shift_jis') as f:
                        data = f.read()
            return json.loads(data)

    async def aload_json(self, key: str, force_file: Optional[bool] = False) -> Union[dict, list]:
        if self.mode == 'repl' and not force_file:
            data = db[key]['value']
            if isinstance(data, str):
                return json.loads(db[key]['value'])
            return data
        else:
            try:
                async with aopen(f'{key}.json', encoding='utf-8') as f:
                    data = await f.read()
            except UnicodeDecodeError:
                try:
                    async with aopen(f'{key}.json', encoding='utf-8-sig') as f:
                        data = await f.read()
                except UnicodeDecodeError:
                    async with aopen(f'{key}.json', encoding='shift_jis') as f:
                        data = await f.read()
            return json.loads(data)

    def save_json(self, key: str, value: Union[dict, list],
                  force_file: Optional[bool] = False,
                  compact: Optional[bool] = False) -> None:
        if self.mode == 'repl' and not force_file:
            db[key] = {
                'last_edited': self.utcnow(),
                'value': json.dumps(
                    value,
                    ensure_ascii=False,
                    cls=MyJSONEncoder
                )
            }
        else:
            with open(f'{key}.json', 'w', encoding='utf-8') as f:
                if compact:
                    json.dump(
                        value,
                        f,
                        ensure_ascii=False,
                        cls=MyJSONEncoder
                    )
                else:
                    json.dump(
                        value,
                        f,
                        indent=4,
                        ensure_ascii=False,
                        cls=MyJSONEncoder
                    )

    def dumps(self, data: Union[dict, list]) -> str:
        return json.dumps(
            data,
            ensure_ascii=False,
            cls=MyJSONEncoder
        )

    def get_last_edited(self, key: str, force_file: Optional[bool] = False) -> datetime.datetime:
        if self.mode == 'repl' and not force_file:
            return datetime.datetime.fromisoformat(db[key]['last_edited'])
        else:
            stat = os.stat(f'{key}.json')
            return datetime.datetime.fromtimestamp(stat.st_mtime)

    def is_not_edited_for(self, key: str, td: datetime.timedelta, force_file: Optional[bool] = False) -> bool:
        last_edited = self.get_last_edited(key, force_file=force_file)
        if last_edited < (datetime.datetime.utcnow() - td):
            return True
        return False

    def l(self, key: str, *args: tuple, default: Optional[str] = '', **kwargs: dict) -> LocalizedText:
        return LocalizedText(self, ['main', key], default, *args, **kwargs)

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
            add_d.append(self.discord_error)
        if not self.config['no_logs'] if self.config else True:
            text = content
            for func in add_p:
                text = func(text)
            print(color(text), file=file)

        if self.webhook:
            content = discord.utils.escape_markdown(content)
            name = user_name or 'Fortnite-LobbyBot'
            text = content
            for func in add_d:
                text = func(text)
            self.webhook.send(text, name)

    def time(self, text: str) -> str:
        return f'[{self.now()}] {text}'

    def discord_error(self, text: str) -> str:
        texts = []
        for line in text.split('\n'):
            texts.append(f'> {line}')
        return '\n'.join(texts)

    def debug_message(self, text: str) -> str:
        return f'```\n{text}\n```'

    def format_exception(self, exc: Optional[Exception] = None) -> str:
        if exc is not None:
            return ''.join(list(traceback.TracebackException.from_exception(exc).format()))
        return traceback.format_exc()

    def print_exception(self, exc: Optional[Exception] = None) -> None:
        if exc is not None:
            self.send(
                ''.join(['Ignoring exception\n']
                        + list(traceback.TracebackException.from_exception(exc).format())),
                file=sys.stderr
            )
        else:
            self.send(
                traceback.format_exc(),
                file=sys.stderr
            )

    def debug_print_exception(self, exc: Optional[Exception] = None) -> None:
        if self.config is not None and self.config['loglevel'] == 'debug':
            self.print_exception(exc)

    def now(self) -> str:
        return datetime.datetime.now().strftime('%H:%M:%S')

    def utcnow(self) -> str:
        return datetime.datetime.utcnow().strftime('%H:%M:%S')

    def strftime(self, dt: datetime.datetime) -> str:
        dt = dt.astimezone(get_localzone())
        if dt.hour >= 12 and self.config['lang'] == 'en':
            dt -= datetime.timedelta(hours=12)
            return f"{dt.strftime('%H:%M PM')}"
        return f"{dt.strftime('%H:%M')}"

    def str_to_bool(self, text: str) -> bool:
        if text.lower() == 'true':
            return True
        elif text.lower() == 'false':
            return False
        raise ValueError(f"{text!r} does not match to any of True, False")

    def get_list_index(self, data: list, index: int, default: Optional[Any] = None) -> Any:
        return data[index] if data[index:index + 1] else default

    def eval_format(self, text: str, variables: dict) -> str:
        return self.formatter.format(text, **variables)

    def eval_dict(self, data: dict, keys: list) -> str:
        text = ''
        for key in keys:
            text += f"[{repr(key)}]"
        return text

    def get_dict_key(self, data: dict, keys: list,
                     func: Optional[Callable] = None) -> Any:
        func = func or (lambda x: x)
        text = self.eval_dict(data, keys)
        return func(eval(f'data{text}'))

    def set_dict_key(self, data: dict, keys: list, value: Any,
                     func: Optional[Callable] = None) -> None:
        func = func or (lambda x: x)
        text = self.eval_dict(data, keys)
        exec(f'data{text} = func(value)')

    def eval_dict_default(self, data: dict, keys: list) -> Tuple[str, str]:
        text = ''
        text2 = ''
        for nest, key in enumerate(keys, 1):
            text += f"[{repr(key)}]"
            if nest == len(keys):
                if isinstance(key, str):
                    text2 += f".get('{key}', default)"
                else:
                    text2 = f"self.get_list_index(data{text2}, key, default)"
            else:
                text2 += f"[{repr(key)}]"
        return text, text2

    def get_dict_key_default(self, data: dict, keys: list, default: Any,
                             func: Optional[Callable] = None) -> Any:
        func = func or (lambda x: x)
        _, text2 = self.eval_dict_default(data, keys)
        try:
            value = eval(f'data{text2}')
        except (TypeError, KeyError):
            value = default
        return func(value)

    def set_dict_key_default(self, data: dict, keys: list, default: Any,
                             func: Optional[Callable] = None) -> None:
        func = func or (lambda x: x)
        text, text2 = self.eval_dict_default(data, keys)
        try:
            value = eval(f'data{text2}')  # noqa
        except ValueError:
            value = default  # noqa
        exec(f'data{text} = func(value)')

    def load_config(self) -> Optional[Tuple[dict, list]]:
        try:
            config = self.load_json('config')
        except (json.decoder.JSONDecodeError, UnicodeDecodeError) as e:
            self.send(
                (f'{self.format_exception(e)}\n{e}\n'
                 + self.l(
                     'load_failed_json',
                     'config',
                     default=(
                         "'{0}' ファイルの読み込みに失敗しました。正しく書き込めているか確認してください\n"
                         "Failed to load '{0}' file. Make sure you wrote correctly"
                     )
                 )),
                file=sys.stderr
            )
            return None, None
        except FileNotFoundError as e:
            self.send(
                (f'{self.format_exception(e)}\n{e}\n'
                 + self.l(
                     'load_failed_not_found',
                     'config',
                     default=(
                         "'{0}' ファイルが存在しません\n"
                         "'{0}' file does not exist"
                     )
                 )),
                file=sys.stderr
            )
            return None, None
        self.set_dict_key_default(config, ['clients'], [])
        self.set_dict_key_default(config, ['web'], {})
        self.set_dict_key_default(config, ['web', 'enabled'], True)
        self.set_dict_key_default(config, ['web', 'ip'], '{ip}')
        self.set_dict_key_default(config, ['web', 'port'], 8000)
        self.set_dict_key_default(config, ['check_update_on_startup'], True)
        self.set_dict_key_default(config, ['lang'], 'en')
        self.set_dict_key_default(config, ['api'], 'BenBot')
        self.set_dict_key_default(config, ['api_key'], None)
        self.set_dict_key_default(config, ['discord_log'], None)
        self.set_dict_key_default(config, ['loglevel'], 'normal')
        self.set_dict_key_default(config, ['no_logs'], 'normal')
        self.set_dict_key_default(config, ['debug'], False)
        self.set_dict_key_default(config, ['status'], 0)

        if self.mode != 'pc':
            replace = '0.0.0.0'
        else:
            replace = 'localhost'
        config['web']['ip'] = config['web']['ip'].format(ip=replace)

        error_config = []
        self.tag_check(config, error_config, '', self.config_tags)
        if config['loglevel'] == 'debug':
            self.send(json.dumps(config, indent=4, ensure_ascii=False),
                      color=yellow, add_d=lambda x: f'{self.debug_message(x)}\n')
        self.save_json('config', config)
        if config['api'] == 'FortniteApi.io' and not config['api_key']:
            self.send(
                self.l('api_key_required'),
                add_p=self.time,
                file=sys.stderr
            )
            error_config.append("['api_key']")

        return config, error_config

    def load_localize(self, lang: str) -> Optional[dict]:
        try:
            localize = self.load_json(f'{self.lang_dir}/{lang}', force_file=True)
        except (json.decoder.JSONDecodeError, UnicodeDecodeError) as e:
            self.send(
                (f'{self.format_exception(e)}\n{e}\n'
                 + self.l(
                     'load_failed_json',
                     f'{self.lang_dir}/{lang}',
                     default=(
                         "'{0}' ファイルの読み込みに失敗しました。正しく書き込めているか確認してください\n"
                         "Failed to load '{0}' file. Make sure you wrote correctly"
                     )
                 )),
                file=sys.stderr
            )
            return None
        except FileNotFoundError as e:
            self.send(
                (f'{self.format_exception(e)}\n{e}\n'
                 + self.l(
                     'load_failed_not_found',
                     f'{self.lang_dir}/{lang}',
                     default=(
                         "'{0}' ファイルが存在しません\n"
                         "'{0}' file does not exist"
                     )
                 )),
                file=sys.stderr
            )
            return None
        return localize

    def load_commands(self) -> Optional[Tuple[dict, list]]:
        try:
            commands = self.load_json('commands')
        except (json.decoder.JSONDecodeError, UnicodeDecodeError) as e:
            self.send(
                (f'{self.format_exception(e)}\n{e}\n'
                 + self.l(
                     'load_failed_json',
                     'commands',
                     default=(
                         "'{0}' ファイルの読み込みに失敗しました。正しく書き込めているか確認してください\n"
                         "Failed to load '{0}' file. Make sure you wrote correctly"
                     )
                 )),
                file=sys.stderr
            )
            return None, None
        except FileNotFoundError as e:
            self.send(
                (f'{self.format_exception(e)}\n{e}\n'
                 + self.l(
                     'load_failed_not_found',
                     'commands',
                     default=(
                         "'{0}' ファイルが存在しません\n"
                         "'{0}' file does not exist"
                     )
                 )),
                file=sys.stderr
            )
            return None, None

        error_commands = []
        self.tag_check(commands, error_commands, '', self.commands_tags)
        if self.config['loglevel'] == 'debug':
            self.send(json.dumps(commands, indent=4, ensure_ascii=False),
                      color=yellow, add_d=lambda x: f'{self.debug_message(x)}\n')
        self.save_json('commands', commands)

        return commands, error_commands

    def load_custom_commands(self) -> Optional[Tuple[dict, list]]:
        try:
            custom_commands = self.load_json('custom_commands')
        except (json.decoder.JSONDecodeError, UnicodeDecodeError) as e:
            self.send(
                (f'{self.format_exception(e)}\n{e}\n'
                 + self.l(
                     'load_failed_json',
                     'custom_commands',
                     default=(
                         "'{0}' ファイルの読み込みに失敗しました。正しく書き込めているか確認してください\n"
                         "Failed to load '{0}' file. Make sure you wrote correctly"
                     )
                 )),
                file=sys.stderr
            )
            return None, None
        except FileNotFoundError as e:
            self.send(
                (f'{self.format_exception(e)}\n{e}\n'
                 + self.l(
                     'load_failed_not_found',
                     'custom_commands',
                     default=(
                         "'{0}' ファイルが存在しません\n"
                         "'{0}' file does not exist"
                     )
                 )),
                file=sys.stderr
            )
            return None, None

        error_custom_commands = []
        self.tag_check(custom_commands, error_custom_commands, '', self.custom_commands_tags)
        if self.config['loglevel'] == 'debug':
            self.send(json.dumps(custom_commands, indent=4, ensure_ascii=False),
                      color=yellow, add_d=lambda x: f'{self.debug_message(x)}\n')
        self.save_json('custom_commands', custom_commands)

        return custom_commands, error_custom_commands

    def load_replies(self) -> Optional[Tuple[dict, list]]:
        try:
            replies = self.load_json('replies')
        except (json.decoder.JSONDecodeError, UnicodeDecodeError) as e:
            self.send(
                (f'{self.format_exception(e)}\n{e}\n'
                 + self.l(
                     'load_failed_json',
                     'replies',
                     default=(
                         "'{0}' ファイルの読み込みに失敗しました。正しく書き込めているか確認してください\n"
                         "Failed to load '{0}' file. Make sure you wrote correctly"
                     )
                 )),
                file=sys.stderr
            )
            return None, None
        except FileNotFoundError as e:
            self.send(
                (f'{self.format_exception(e)}\n{e}\n'
                 + self.l(
                     'load_failed_not_found',
                     'replies',
                     default=(
                         "'{0}' ファイルが存在しません\n"
                         "'{0}' file does not exist"
                     )
                 )),
                file=sys.stderr
            )
            return None, None

        error_replies = []
        self.tag_check(replies, error_replies, '', self.replies_tags)
        if self.config['loglevel'] == 'debug':
            self.send(json.dumps(replies, indent=4, ensure_ascii=False),
                      color=yellow, add_d=lambda x: f'{self.debug_message(x)}\n')
        self.save_json('replies', replies)

        return replies, error_replies

    def get_select_tag(self, data: list) -> Optional[str]:
        for tag in data:
            if isinstance(tag, str) and tag.startswith('select'):
                return tag

    def get_multiple_select_tag(self, data: list) -> Optional[str]:
        for tag in data:
            if isinstance(tag, str) and tag.startswith('multiple_select'):
                return tag

    def get_config_tag(self, data: list) -> Optional[str]:
        for tag in data:
            if isinstance(tag, str) and tag.endswith('_config'):
                return tag

    def flat_dict(self, data: dict) -> dict:
        final = {}
        for key, value in data.items():
            if isinstance(value, dict):
                for k, v in self.flat_dict(value).items():
                    final[f"[{repr(key)}]{k}"] = v
            elif isinstance(value, list):
                for num, val in enumerate(value):
                    if isinstance(val, dict):
                        for k, v in self.flat_dict(val).items():
                            final[f"[{repr(key)}][{num}]{k}"] = v
                    elif isinstance(val, list):
                        for n, v in enumerate(val):
                            final[f"[{repr(key)}][{num}][{n}]"] = v
                    else:
                        final[f"[{repr(key)}][{num}]"] = val
                        
            else:
                final[f"[{repr(key)}]"] = value
        return final

    def tag_check(self, data: dict, error_list: list,
                  prefix: str, tag_data: dict) -> None:
        for key, tags in tag_data.items():
            self.value_check(data, error_list, prefix, key, tags)

    def value_check(self, data: dict, error_list: list,
                    prefix: str, key: str, tags: list) -> None:
        try:
            value = eval(f'data{key}')
        except Exception:
            self.send(
                self.l(
                    'is_missing',
                    f'{prefix}{key}',
                    default=(
                        "{0} がありません\n"
                        "{0} is missing"
                    )
                ),
                file=sys.stderr
            )
            error_list.append(f'{prefix}{key}')
        else:
            select_tag = self.get_select_tag(tags)
            multiple_select_tag = self.get_multiple_select_tag(tags)
            config_tag = self.get_config_tag(tags)
            valid_tags = (tags[0],)
            if tags[0] is float:
                valid_tags = (*valid_tags, int)
            if 'can_be_none' in tags:
                valid_tags = (*valid_tags, None.__class__)
                if select_tag is not None:
                    tag_data = getattr(self, select_tag)
                    if self.none_data not in tag_data:
                        tag_data.append(self.none_data)
                if multiple_select_tag is not None:
                    tag_data = getattr(self, multiple_select_tag)
                    if self.none_data not in tag_data:
                        tag_data.append(self.none_data)

            if not isinstance(value, valid_tags):
                expected = f'{tags[0].__name__}'
                if 'can_be_none' in tags:
                    expected += f', {None.__class__.__name__}'
                provided = type(value).__name__

                converter = None
                if tags[0] is bool:
                    if isinstance(value, str):
                        converter = 'self.str_to_bool(value)'
                    else:
                        converter = 'tags[0](value)'
                elif tags[0] in [str, int]:
                    converter = 'tags[0](value)'
                elif tags[0] is list:
                    if tags[1] is list:
                        converter = 'json.loads(value)'
                    elif tags[1] is str:
                        if isinstance(value, str):
                            converter = 'value.split(",")'
                    elif tags[1] is int:
                        if isinstance(value, int):
                            converter = '[value]'
                        else:
                            converter = '[int(value)]'
                    
                success = False
                if converter is not None:
                    try:
                        exec(f'data{key} = {converter}')
                        value = eval(f'data{key}')
                    except Exception as e:
                        self.debug_print_exception(e)
                    else:
                        success = True
                if not success:
                    self.send(
                        self.l(
                            'type_mismatch',
                            f'{prefix}{key}',
                            expected,
                            provided,
                            default=(
                                "'{0}' 型が一致しません(予想: '{1}' 実際: '{2}')\n"
                                "'{0}' type mismatch(Expected: '{1}' Provided: '{2}')\n"
                            )
                        ),
                        file=sys.stderr
                    )
                    error_list.append(f'{prefix}{key}')
                else:
                    self.send(
                        self.l(
                            'type_mismatch_fixed',
                            f'{prefix}{key}',
                            expected,
                            provided,
                            eval(f'data{key}'),
                            default=(
                                "'{0}' 型が一致しません(予想: '{1}' 実際: '{2}') -> 修正されました: '{3}'\n"
                                "'{0}' type mismatch(Expected: '{1}' Provided: '{2}') -> Fixed to: '{3}'\n"
                            )
                        ),
                        color=yellow,
                        add_d=self.discord_error
                    )

            if f'{prefix}{key}' not in error_list:
                if tags[0] is list and value is not None:
                    try:
                        exec(f'data{key} = self.cleanup_list(value, "accept_empty" not in tags)')
                    except Exception as e:
                        self.debug_print_exception(e)
                    else:
                        if config_tag is None:
                            for num, val in enumerate(value):
                                tags_ = tags[1:].copy()
                                if select_tag is not None:
                                    tags_.remove(select_tag)
                                if multiple_select_tag is not None:
                                    tags_.remove(multiple_select_tag)
                                self.value_check(data, error_list,
                                                 prefix,
                                                 f'{key}[{num}]',
                                                 tags_)

                if select_tag is not None:
                    values = [
                        (i['real_value'].lower()
                            if isinstance(i['real_value'], str) else
                            i['real_value'])
                        for i in getattr(self, select_tag)
                    ]
                    if (value.lower()
                            if isinstance(value, str) else
                            value) not in values:
                        self.send(
                            self.l(
                                'not_in_select',
                                f'{prefix}{key}',
                                value,
                                values,
                                default=(
                                    "'{0}' '{1}' は {2} のどれにも一致しません\n"
                                    "'{0}' '{1}' don't match to any of {2}\n"
                                )
                            ),
                            file=sys.stderr
                        )
                        error_list.append(f'{prefix}{key}')
                    else:
                        v = CaseInsensitiveDict({i['real_value']: i for i in getattr(self, select_tag)})
                        exec(f"data{key} = v[value]['real_value']")
                if multiple_select_tag is not None and value is not None:
                    values = [
                        (i['real_value'].lower()
                            if isinstance(i['real_value'], str) else
                            i['real_value'])
                        for i in getattr(self, multiple_select_tag)
                    ]
                    for num, val in enumerate(value):
                        if (val.lower()
                                if isinstance(val, str) else
                                val) not in values:
                            self.send(
                                self.l(
                                    'not_in_select',
                                    f'{prefix}{key}',
                                    value,
                                    values,
                                    default=(
                                        "'{0}' '{1}' は {2} のどれにも一致しません\n"
                                        "'{0}' '{1}' don't match to any of {2}\n"
                                    )
                                ),
                                file=sys.stderr
                            )
                            error_list.append(f'{prefix}{key}')
                            break
                        else:
                            v = CaseInsensitiveDict({i['real_value']: i for i in getattr(self, multiple_select_tag)})
                            value[num] = v[val]['real_value']

                func_str = tags[-1]
                if isinstance(func_str, str) and func_str.startswith('lambda '):
                    try:
                        func = eval(func_str, {**globals(), **locals()})
                    except Exception:
                        pass
                    else:
                        if not func(value):
                            self.send(
                                self.l(
                                    'check_failed',
                                    f'{prefix}{key}',
                                    value,
                                    func_str,
                                    default=(
                                        "{0} '{1}' はチェック '{2}' に一致しません\n"
                                        "{0} '{1}' don't match to check '{2}'\n"
                                    )
                                ),
                                file=sys.stderr
                            )
                            error_list.append(f'{prefix}{key}')

                if config_tag is not None:
                    for num, val in enumerate(value):
                        self.tag_check(eval(f'data{key}[{num}]'),
                                       error_list, f'{prefix}{key}[{num}]',
                                       getattr(self, f'{config_tag}_tags'))

    def cleanup_email(self, email: str) -> str:
        return re.sub(r'\.|\+', '', email).lower()

    def cleanup_code(self, content: str) -> str:
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])
        return content.strip(' \n')

    def cleanup_list(self, data: list, remove_empty: Optional[bool] = True) -> list:
        return [d for d in data if d is not None and (d != '' if remove_empty else True)]

    def cleanup_channel_name(self, text: str) -> str:
        converter = {
            ' ': '-',
            '.': '-',
            ',': '-',
            '--': '-'
        }
        for word, replace in converter.items():
            text = text.replace(word, replace)
        return text.lower()

    def convert_backend_type(self, backendType: str) -> str:
        return self.BACKEND_TO_API_CONVERTER.get(backendType)

    def convert_to_backend_type(self, type: str) -> str:
        return self.API_TO_BACKEND_CONVERTER.get(type)

    def convert_backend_to_key(self, backendType: str) -> str:
        return self.BACKEND_TO_KEY_CONVERTER.get(backendType)

    def convert_backend_to_id(self, backendType: str) -> str:
        return self.BACKEND_TO_ID_CONVERTER.get(backendType)

    def convert_variant(self, variants: list) -> list:
        if variants is None:
            return None
        return [
            {
                'name': option['name'],
                'variants': [
                    {
                        'c': variant['channel'],
                        'v': (
                            option['tag']
                            if any([option['tag'].startswith(fmt) for fmt in self.VARIANT_FORMATS]) else
                            f'Color.{option["tag"]}'
                        ),
                        'dE': 0
                    }
                ]
            } for variant in variants for option in variant.get('options', [])
        ]

    def get_item_str(self, item: dict) -> str:
        return "<Item name='{0[name]}' id='{0[id]}' path='{0[path]}'>".format(
            item
        )

    def get_playlist_str(self, playlist: dict) -> str:
        return '<Playlist name={0[name]!r} id={0[id]!r}>'.format(
            playlist
        )

    def get_variant_str(self, variant: dict) -> str:
        return ('<Variant name={0[name]!r} '
                'channel={1[c]!r} '
                'tag={1[v]!r}>'.format(
                    variant,
                    variant['variants'][0]
                ))

    def get_config_item_id(self, text: str) -> str:
        if text is None:
            return None
        match = self.config_item_pattern.match(text)
        if match is None:
            return None
        return match.group('id')

    def get_config_item_path(self, text: str) -> str:
        if text is None:
            return None
        match = self.config_item_pattern.match(text)
        if match is None:
            return None
        return match.group('path')

    def get_config_playlist_id(self, text: str) -> str:
        if text is None:
            return None
        match = self.config_playlist_pattern.match(text)
        if match is None:
            return None
        return match.group('id')

    def get_config_variant(self, text: str) -> dict:
        if text is None:
            return None
        match = self.config_variant_pattern.match(text)
        if match is None:
            return None
        return {
            'name': match.group('name'),
            'variants': [
                {
                    'c': match.group('channel'),
                    'v': match.group('tag'),
                    'dE': 0
                }
            ]
        }

    def port_file(self, filename: str, backup: Optional[bool] = True) -> None:
        if self.mode == 'repl' and os.path.isfile(f'{filename}.json'):
            data = self.load_json(filename, force_file=True)
            if backup:
                if self.isfile(f'{filename}_old', force_file=True):
                    self.remove(f'{filename}_old', force_file=True)
                self.rename(filename, f'{filename}_old', force_file=True)
            try:
                self.remove(filename, force_file=True)
            except Exception as e:
                self.debug_print_exception(e)
            self.save_json(filename, data)

    def remove_unneeded_files(self) -> None:
        pc_only = [
            'INSTALL.bat',
            'requirements.txt',
            'RUN.bat'
        ]
        repl_only = [
            '.replit',
            'pyproject.toml'
        ]

        if self.mode == 'pc':
            for filename in repl_only:
                if os.path.isfile(filename):
                    os.remove(filename)
            windows_only = [
                'INSTALL.bat',
                'RUN.bat'
            ]
            else_only = [
                'INSTALL.sh',
                'RUN.sh'
            ]
            if sys.platform == 'win32':
                for filename in else_only:
                    if os.path.isfile(filename):
                        os.remove(filename)
            else:
                for filename in windows_only:
                    if os.path.isfile(filename):
                        os.remove(filename)
        elif self.mode == 'repl':
            for filename in pc_only:
                if os.path.isfile(filename):
                    os.remove(filename)

    def setup(self) -> None:
        self.remove_unneeded_files()
        files = [
            ('config',),
            ('commands',),
            ('custom_commands',),
            ('replies',),
            ('cosmetic_preset',),
            ('command_stats', False),
            ('device_auths', False)
        ]
        for detail in files:
            self.port_file(*detail)

        self.config, self.error_config = self.load_config()
        if self.config is None and self.error_config is None:
            sys.exit(1)
        if self.error_config:
            self.send(
                self.l(
                    'error_keys',
                    '\n'.join(self.error_config),
                    default=(
                        "以下のキーに問題がありました\n{0}\n"
                        "There was an error on these keys\n{0}\n"
                    )
                ),
                file=sys.stderr
            )
        self.webhook = WebhookClient(self, self, self.loop, self.http)
        self.webhook.start()
        if self.config['discord']['enabled']:
            self.discord_client = DiscordClient(self, self.config, loop=self.loop)

        if self.isfile(f"{self.lang_dir}/{self.config['lang']}", force_file=True):
            self.localize = self.load_localize(self.config['lang'])
        else:
            self.localize = self.load_localize('en')

        self.commands, self.error_commands = self.load_commands()
        if self.commands is None and self.error_commands is None:
            sys.exit(1)
        if self.error_commands:
            self.send(
                self.l(
                    'error_keys',
                    '\n'.join(self.error_commands),
                    default=(
                        "以下のキーに問題がありました\n{0}\n"
                        "There was an error on keys\n{0}\n"
                    )
                ),
                file=sys.stderr
            )

        self.custom_commands, self.error_custom_commands = self.load_custom_commands()
        if self.custom_commands is None and self.error_custom_commands is None:
            sys.exit(1)
        if self.error_custom_commands:
            self.send(
                self.l(
                    'error_keys',
                    '\n'.join(self.error_custom_commands),
                    default=(
                        "以下のキーに問題がありました\n{0}\n"
                        "There was an error on keys\n{0}\n"
                    )
                ),
                file=sys.stderr
            )

        self.replies, self.error_replies = self.load_replies()
        if self.replies is None and self.error_replies is None:
            sys.exit(1)
        if self.error_replies:
            self.send(
                self.l(
                    'error_keys',
                    '\n'.join(self.error_replies),
                    default=(
                        "以下のキーに問題がありました\n{0}\n"
                        "There was an error on keys\n{0}\n"
                    )
                ),
                file=sys.stderr
            )

        ids = [f'{prefix}_'.lower() for prefix in self.BACKEND_TO_ID_CONVERTER.values()]
        self.whitelist_commands = []
        for identifier in self.commands['whitelist_commands']:
            identifier = identifier.lower()
            command = self.all_commands.get(identifier)
            if command is None and identifier not in [*ids, 'playlist_', 'item_search']:
                self.send(
                    self.l(
                        'command_not_found',
                        self.l('whitelist_command'),
                        identifier
                    )
                )
            else:
                self.whitelist_commands.append(identifier)

        self.user_commands = []
        for identifier in self.commands['user_commands']:
            identifier = identifier.lower()
            command = self.all_commands.get(identifier)
            if command is None and identifier not in [*ids, 'playlist_', 'item_search']:
                self.send(
                    self.l(
                        'command_not_found',
                        self.l('user_command'),
                        identifier
                    )
                )
            else:
                self.user_commands.append(identifier)

        if not self.is_error():
            self.send(
                self.l(
                    'load_success',
                    default=(
                        "正常に読み込みが完了しました\n"
                        "Loading successfully finished\n"
                    )
                ),
                color=green
            )
        elif self.config['web']['enabled']:
            self.send(
                self.l(
                    'load_failed_web',
                    default=(
                        "正常に読み込みが完了しませんでした。ファイルを直接修正するか、Webから修正してください\n"
                        "Loading didn't finish successfully. Please fix files directly or fix from web\n"
                    )
                ),
                file=sys.stderr
            )
        else:
            self.send(
                self.l(
                    'load_failed',
                    default=(
                        "正常に読み込みが完了しませんでした。ファイルを修正してください\n"
                        "Loading didn't finish successfully. Please fix files\n"
                    )
                ),
                file=sys.stderr
            )
            sys.exit(1)

        try:
            self.cosmetic_presets = self.get_cosmetic_presets()
        except (json.decoder.JSONDecodeError, UnicodeDecodeError) as e:
            self.debug_print_exception(e)
            if self.isfile('cosmetic_presets_old'):
                self.remove('cosmetic_presets_old')
            self.rename('cosmetic_presets', 'cosmetic_presets_old')
            try:
                self.remove('cosmetic_presets')
            except Exception as e:
                self.debug_print_exception(e)
            self.cosmetic_presets = {}

        try:
            self.command_stats = self.get_command_stats()
        except (json.decoder.JSONDecodeError, UnicodeDecodeError) as e:
            self.debug_print_exception(e)
            if self.isfile('command_stats_old'):
                self.remove('command_stats_old')
            self.rename('command_stats', 'command_stats_old')
            try:
                self.remove('command_stats')
            except Exception as e:
                self.debug_print_exception(e)
            self.command_stats = {}


    async def aexec(self, body: str, variables: dict) -> Tuple[Any, str, str]:
        body = self.cleanup_code(body)
        stdout = io.StringIO()
        stderr = io.StringIO()

        exc = f"async def __exc__():\n{textwrap.indent(body,'  ')}"
        exec(exc, variables)

        func = variables['__exc__']
        with redirect_stdout(stdout), redirect_stderr(stderr):
            return await func(), stdout.getvalue(), stderr.getvalue()


    def format_item(self, data: dict, mode: str) -> dict:
        if mode == 'BenBot':
            return {
                'id': data['id'],
                'path': f"{self.convert_backend_type(data['backendType'])}ItemDefinition'{data['path'].replace('FortniteGame/Content', '/Game')}.{data['path'].split('/')[-1]}'",
                'name': data['name'],
                'url':  data['icons']['icon'],
                'type': {
                    'value': self.convert_backend_type(data['backendType']),
                    'displayValue': data['shortDescription'],
                    'backendValue': data['backendType']
                },
                'set': data['set'],
                'variants': self.convert_variant(data['variants'])
            }
        elif mode == 'Fortnite-API':
            return {
                'id': data['id'],
                'path': f"{data['type']['backendValue']}ItemDefinition'{data['path'].replace('FortniteGame/Content', '/Game')}.{data['path'].split('/')[-1]}'",
                'name': data['name'],
                'url': data['images']['icon'],
                'type': data['type'],
                'set': data['set']['value'] if data['set'] is not None else None,
                'variants': self.convert_variant(data['variants'])
            }
        elif mode == 'FortniteApi.io':
            return {
                'id': data['id'],
                'path': MyClientPartyMember.get_asset_path(self.convert_to_backend_type(data['type']), data['id']),
                'name': data['name'],
                'url': data['images']['icon'],
                'type': {
                    'value': data['type'],
                    'displayValue': (
                        self.l(data['type']).get_text()
                    ),
                    'backendValue': self.convert_to_backend_type(data['type'])
                },
                'set': data['set'] if data['set'] else None,
                'variants': None
            }

    def format_items(self, data: list, mode: str) -> list:
        types = [
            'AthenaCharacter',
            'AthenaBackpack',
            'AthenaPet',
            'AthenaPetCarrier',
            'AthenaPickaxe',
            'AthenaDance',
            'AthenaEmoji',
            'AthenaToy'
        ]
        return [item for item in [
            self.format_item(item, mode)
            for item in sorted(data, key=lambda x: x['id'])
        ] if item['type']['backendValue'] in types]

    async def get_item_data(self, lang: str) -> list:
        if self.config['api'] == 'BenBot':
            return self.format_items(await self.http.get(
                'http://benbot.app/api/v1/cosmetics/br',
                params={'lang': lang}
            ), self.config['api'])
        elif self.config['api'] == 'Fortnite-API':
            return self.format_items((await self.http.get(
                'https://fortnite-api.com/v2/cosmetics/br',
                params={'language': lang}
            ))['data'], self.config['api'])
        elif self.config['api'] == 'FortniteApi.io':
            items = (await self.http.get(
                'https://fortniteapi.io/v1/items/list',
                params={'lang': lang},
                headers={'Authorization': self.config['api_key']}
            ))['items']
            return self.format_items(
                sum(
                    [v for k, v in items.items() if k not in [
                        'bannertoken',
                        'bundle',
                        'cosmeticvariant'
                    ]],
                    []
                ),
                self.config['api']
            )

    async def store_item_data(self, lang: str) -> None:
        if self.isfile(f'{self.item_dir}/items_{lang}', force_file=True):
            items = await self.aload_json(f'{self.item_dir}/items_{lang}', force_file=True)
            items['items'] = CaseInsensitiveDict(items['items'])
        else:
            items = {'api': None, 'items': CaseInsensitiveDict()}
        data = await self.get_item_data(lang)
        if self.config['api'] == 'FortniteApi.io':
            for item in data:
                i = items['items'].get(item['id'])
                if i is None:
                    items['items'][item['id']] = item
                elif i['variants'] is not None:
                    item['variants'] = i['variants']
                    items['items'][item['id']] = item
        else:
            for item in data:
                items['items'][item['id']] = item
        items['api'] = self.config['api']
        self.save_json(
            f'{self.item_dir}/items_{lang}',
            items,
            force_file=True,
            compact=True
        )

    async def get_new_item_data(self, lang: str) -> list:
        if self.config['api'] == 'BenBot':
            return self.format_items((await self.http.get(
                'http://benbot.app/api/v1/newCosmetics',
                params={'lang': lang}
            ))['items'], self.config['api'])
        elif self.config['api'] == 'Fortnite-API':
            return self.format_items((await self.http.get(
                'https://fortnite-api.com/v2/cosmetics/br/new',
                params={'language': lang}
            ))['data']['items'], self.config['api'])
        elif self.config['api'] == 'FortniteApi.io':
            return self.format_items((await self.http.get(
                'https://fortniteapi.io/v1/items/upcoming',
                params={'lang': lang},
                headers={'Authorization': self.config['api_key']}
            ))['items'], self.config['api'])

    async def store_new_item_data(self, lang: str) -> None:
        if self.isfile(f'{self.item_dir}/new_items_{lang}', force_file=True):
            items = await self.aload_json(f'{self.item_dir}/new_items_{lang}', force_file=True)
            items['items'] = CaseInsensitiveDict(items['items'])
        else:
            items = {'api': None, 'items': CaseInsensitiveDict()}
        data = {i['id']: i for i in await self.get_new_item_data(lang)}
        if self.config['api'] == 'FortniteApi.io':
            for item in items['items'].values():
                i = data.get(item['id'])
                if i is None:
                    continue
                if item['variants'] is not None:
                    data[item['id']]['variants'] = item['variants']
        items['api'] = self.config['api']
        self.save_json(
            f'{self.item_dir}/new_items_{lang}',
            {'api': self.config['api'], 'items': data},
            force_file=True,
            compact=True
        )


    def format_playlist(self, data: dict, mode: str) -> dict:
        if mode == 'Fortnite-API':
            return {
                'id': data['id'],
                'name': data['name']
            }
        elif mode == 'FortniteApi.io':
            return {
                'id': f'Playlist_{data["id"]}',
                'name': data['name']
            }

    def format_playlists(self, data: list, mode: str) -> list:
        return [
            self.format_playlist(playlist, mode)
            for playlist in sorted(data, key=lambda x: x['id'])
        ]

    async def get_playlists_data(self, lang: str) -> list:
        if self.config['api'] == 'BenBot':
            return []
        elif self.config['api'] == 'Fortnite-API':
            return self.format_playlists(
                (await self.http.get(
                    'https://fortnite-api.com/v1/playlists',
                    params={'language': lang}
                ))['data'], self.config['api']
            )
        elif self.config['api'] == 'FortniteApi.io':
            return self.format_playlists(
                (await self.http.get(
                    'https://fortniteapi.io/v1/game/modes',
                    params={'lang': lang},
                    headers={'Authorization': self.config['api_key']}
                ))['modes'], self.config['api']
            )

    async def store_playlists_data(self, lang: str) -> None:
        if self.isfile(f'{self.item_dir}/playlists_{lang}', force_file=True):
            playlists = await self.aload_json(f'{self.item_dir}/playlists_{lang}', force_file=True)
            playlists['playlists'] = CaseInsensitiveDict(playlists['playlists'])
        else:
            playlists = {'api': None, 'playlists': CaseInsensitiveDict()}
        data = await self.get_playlists_data(lang)
        for playlist in data:
            playlists['playlists'][playlist['id']] = playlist
        playlists['api'] = self.config['api']
        self.save_json(
            f'{self.item_dir}/playlists_{lang}',
            playlists,
            force_file=True,
            compact=True
        )


    async def get_banner_data(self) -> dict:
        if self.config['api'] == 'BenBot':
            data = await self.http.get(
                'https://benbot.app/api/v1/files/search',
                params={
                    'matchMethod': 'starts',
                    'path': 'FortniteGame/Content/Items/BannerIcons/'
                }
            )
            url = 'https://benbot.app/api/v1/exportAsset?path={}&rawIcon=true'
            return {
                banner[39:-7]: url.format(banner) for banner in data
            }
        elif self.config['api'] == 'Fortnite-API':
            data = (await self.http.get(
                'https://fortnite-api.com/v1/banners'
            ))['data']
            return {
                banner['id']: banner['images']['icon'] for banner in data
            }
        elif self.config['api'] == 'FortniteApi.io':
            return {}

    async def store_banner_data(self) -> None:
        if self.isfile(f'{self.item_dir}/banners', force_file=True):
            banners = await self.aload_json(f'{self.item_dir}/banners', force_file=True)
            banners['banners'] = CaseInsensitiveDict(banners['banners'])
        else:
            banners = {'api': None, 'banners': CaseInsensitiveDict()}
        data = await self.get_banner_data()
        for id, image in data.items():
            banners['banners'][id] = image
        banners['api'] = self.config['api']
        self.save_json(
            f'{self.item_dir}/banners',
            banners,
            force_file=True,
            compact=True
        )

    def get_banner_url(self, banner_id: str) -> Optional[str]:
        return self.banners.get(banner_id, self.web.url_for('static', filename='images/banner.jpg'))


    async def error_callback(self, client: Client, e: Exception):
        if isinstance(e, fortnitepy.AuthException):
            if 'Invalid device auth details passed.' in e.args[0]:
                self.debug_print_exception(e)
                self.send(
                    self.l(
                        'device_auth_error',
                        client.config['fortnite']['email']
                    ),
                    add_p=self.time,
                    file=sys.stderr
                )
                details = self.get_device_auth_details()
                details.pop(client.config['fortnite']['email'])
                self.save_json('device_auths', details)
            else:
                self.print_exception(e)
                self.send(
                    self.l(
                        'login_failed',
                        client.config['fortnite']['email']
                    ),
                    add_p=self.time,
                    file=sys.stderr
                )
        else:
            self.print_exception(e)
            self.send(
                self.l(
                    'login_failed',
                    client.config['fortnite']['email']
                ),
                add_p=self.time,
                file=sys.stderr
            )

    async def all_ready_callback(self):
        if len(self.clients) > 1:
            await asyncio.gather(*[client.wait_until_ready() for client in self.clients])
            self.send(
                self.l(
                    'all_login'
                ),
                color=green,
                add_p=self.time
            )

    async def update_data(self) -> None:
        # Cosmetics
        tasks = []
        if self.isfile(f"{self.item_dir}/items_{self.config['search_lang']}", force_file=True):
            try:
                items = await self.aload_json(f"{self.item_dir}/items_{self.config['search_lang']}", force_file=True)
            except json.decoder.JSONDecodeError as e:
                self.debug_print_exception(e)
                await self.aremove(f"{self.item_dir}/items_{self.config['search_lang']}", force_file=True)
                flag = True
            else:
                if items['api'] != self.config['api']:
                    flag = True
                else:
                    flag = self.is_not_edited_for(
                        f"{self.item_dir}/items_{self.config['search_lang']}",
                        datetime.timedelta(hours=2),
                        force_file=True
                    )
        else:
            flag = True
        if flag:
            tasks.append(self.loop.create_task(self.store_item_data(self.config['search_lang'])))

        if self.isfile(f"{self.item_dir}/items_{self.config['sub_search_lang']}", force_file=True):
            try:
                items = await self.aload_json(f"{self.item_dir}/items_{self.config['sub_search_lang']}", force_file=True)
            except json.decoder.JSONDecodeError as e:
                self.debug_print_exception(e)
                await self.aremove(f"{self.item_dir}/items_{self.config['sub_search_lang']}", force_file=True)
                flag = True
            else:
                if items['api'] != self.config['api']:
                    flag = True
                else:
                    flag = self.is_not_edited_for(
                        f"{self.item_dir}/items_{self.config['sub_search_lang']}",
                        datetime.timedelta(hours=2),
                        force_file=True
                    )
        else:
            flag = True
        if flag:
            tasks.append(self.loop.create_task(self.store_item_data(self.config['sub_search_lang'])))

        exception = False
        if tasks:
            done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)
            for p in pending:
                if not p.done():
                    p.cancel()
            for d in done:
                if d.exception() is not None:
                    exception = True
                    self.print_exception(d.exception())
            if exception:
                self.send(
                    self.l(
                        'get_item_failed'
                    ),
                    file=sys.stderr
                )
                for lang in (self.config['search_lang'], self.config['sub_search_lang']):
                    if not self.isfile(f'{self.item_dir}/items_{lang}', force_file=True):
                        sys.exit(1)

        # New cosmetics
        tasks = []
        if self.isfile(f"{self.item_dir}/new_items_{self.config['search_lang']}", force_file=True):
            try:
                items = await self.aload_json(f"{self.item_dir}/new_items_{self.config['search_lang']}", force_file=True)
            except json.decoder.JSONDecodeError as e:
                self.debug_print_exception(e)
                await self.aremove(f"{self.item_dir}/new_items_{self.config['search_lang']}", force_file=True)
                flag = True
            else:
                if items['api'] != self.config['api']:
                    flag = True
                else:
                    flag = self.is_not_edited_for(
                        f"{self.item_dir}/new_items_{self.config['search_lang']}",
                        datetime.timedelta(hours=2),
                        force_file=True
                    )
        else:
            flag = True
        if flag:
            try:
                await self.store_new_item_data(self.config['search_lang'])
            except Exception as e:
                self.print_exception(e)
                self.send(
                    self.l(
                        'get_item_failed'
                    ),
                    file=sys.stderr
                )

        # Playlists
        tasks = []
        if self.isfile(f"{self.item_dir}/playlists_{self.config['search_lang']}", force_file=True):
            try:
                playlists = await self.aload_json(f"{self.item_dir}/playlists_{self.config['search_lang']}", force_file=True)
            except json.decoder.JSONDecodeError as e:
                self.debug_print_exception(e)
                await self.aremove(f"{self.item_dir}/playlists_{self.config['search_lang']}", force_file=True)
                flag = True
            else:
                if playlists['api'] != self.config['api']:
                    flag = True
                else:
                    flag = self.is_not_edited_for(
                        f"{self.item_dir}/playlists_{self.config['search_lang']}",
                        datetime.timedelta(hours=2),
                        force_file=True
                    )
        else:
            flag = True
        if flag:
            tasks.append(self.loop.create_task(self.store_playlists_data(self.config['search_lang'])))

        if self.isfile(f"{self.item_dir}/playlists_{self.config['sub_search_lang']}", force_file=True):
            try:
                playlists = await self.aload_json(f"{self.item_dir}/playlists_{self.config['sub_search_lang']}", force_file=True)
            except json.decoder.JSONDecodeError as e:
                self.debug_print_exception(e)
                await self.aremove(f"{self.item_dir}/playlists_{self.config['sub_search_lang']}", force_file=True)
                flag = True
            else:
                if playlists['api'] != self.config['api']:
                    flag = True
                else:
                    flag = self.is_not_edited_for(
                        f"{self.item_dir}/playlists_{self.config['sub_search_lang']}",
                        datetime.timedelta(hours=2),
                        force_file=True
                    )
        else:
            flag = True
        if flag:
            tasks.append(self.loop.create_task(self.store_playlists_data(self.config['sub_search_lang'])))

        exception = False
        if tasks:
            done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)
            for p in pending:
                if not p.done():
                    p.cancel()
            for d in done:
                if d.exception() is not None:
                    exception = True
                    self.print_exception(d.exception())
            if exception:
                self.send(
                    self.l(
                        'get_playlist_failed'
                    ),
                    file=sys.stderr
                )
                for lang in (self.config['search_lang'], self.config['sub_search_lang']):
                    if not self.isfile(f'{self.item_dir}/playlists_{lang}', force_file=True):
                        sys.exit(1)

        # Banner
        if not exception:
            if self.isfile(f'{self.item_dir}/banners', force_file=True):
                try:
                    banners = await self.aload_json(f"{self.item_dir}/banners", force_file=True)
                except json.decoder.JSONDecodeError as e:
                    self.debug_print_exception(e)
                    await self.aremove(f"{self.item_dir}/banners", force_file=True)
                    flag = True
                else:
                    if banners['api'] != self.config['api']:
                        flag = True
                    else:
                        flag = self.is_not_edited_for(
                            f'{self.item_dir}/banners',
                            datetime.timedelta(hours=2),
                            force_file=True
                        )
            else:
                flag = True
            if flag:
                await self.store_banner_data()

    def load_data(self) -> None:
        self.main_items = CaseInsensitiveDict(self.load_json(
            f'{self.item_dir}/items_{self.config["search_lang"]}',
            force_file=True
        )['items'])
        self.sub_items = CaseInsensitiveDict(self.load_json(
            f'{self.item_dir}/items_{self.config["sub_search_lang"]}',
            force_file=True
        )['items'])
        self.new_items = CaseInsensitiveDict(self.load_json(
            f'{self.item_dir}/new_items_{self.config["search_lang"]}',
            force_file=True
        )['items'])
        self.main_playlists = CaseInsensitiveDict(self.load_json(
            f'{self.item_dir}/playlists_{self.config["search_lang"]}',
            force_file=True
        )['playlists'])
        self.sub_playlists = CaseInsensitiveDict(self.load_json(
            f'{self.item_dir}/playlists_{self.config["sub_search_lang"]}',
            force_file=True
        )['playlists'])
        self.banners = CaseInsensitiveDict(self.load_json(
            f'{self.item_dir}/banners',
            force_file=True
        )['banners'])

    def fix_config(self, config: dict) -> None:
        if isinstance(config['fortnite']['party']['privacy'], str):
            config['fortnite']['party']['privacy'] = getattr(
                PartyPrivacy,
                config['fortnite']['party']['privacy'].upper()
            )
        if isinstance(config['fortnite']['platform'], str):
            config['fortnite']['platform'] = fortnitepy.Platform(
                config['fortnite']['platform'].upper()
            )
        for num, channel in enumerate(config['discord']['channels']):
            config['discord']['channels'][num] = self.cleanup_channel_name(channel)
        if isinstance(config['discord']['status_type'], str):
            config['discord']['status_type'] = getattr(
                discord.ActivityType,
                config['discord']['status_type'].lower()
            )
        if config['fortnite']['ng_platforms'] is not None:
            for num, ng_platform in enumerate(config['fortnite']['ng_platforms']):
                config['fortnite']['ng_platforms'][num] = fortnitepy.Platform(
                    ng_platform.upper()
                )
        self.fix_cosmetic_config(config)

    def fix_config_all(self) -> None:
        if isinstance(self.config['discord']['status_type'], str):
            self.config['discord']['status_type'] = getattr(
                discord.ActivityType,
                self.config['discord']['status_type'].lower()
            )
        for num, channel in enumerate(self.config['discord']['channels']):
            self.config['discord']['channels'][num] = self.cleanup_channel_name(channel)
        for config in self.config['clients']:
            self.fix_config(config)

    def fix_cosmetic_config(self, config: dict) -> None:
        if config['fortnite']['party']['playlist']:
            if self.get_config_playlist_id(config['fortnite']['party']['playlist']) is None:
                playlist = self.searcher.get_playlist(
                    config['fortnite']['party']['playlist']
                )
                if playlist is None:
                    playlists = self.searcher.search_playlist_name_id(
                        config['fortnite']['party']['playlist']
                    )
                    if len(playlists) != 0:
                        playlist = playlists[0]
                if playlist is not None:
                    config['fortnite']['party']['playlist'] = (
                        self.get_playlist_str(playlist)
                    )
                else:
                    self.send(
                        self.l(
                            'not_found',
                            self.l('playlist'),
                            config['fortnite']['party']['playlist']
                        ),
                        add_p=self.time,
                        file=sys.stderr
                    )

        for item in ['AthenaCharacter',
                     'AthenaBackpack,AthenaPet,AthenaPetCarrier',
                     'AthenaPickaxe',
                     'AthenaDance,AthenaEmoji,AthenaToy']:
            lang_key = self.convert_backend_type(item.split(",")[0])
            for prefix in ['', 'join_', 'leave_']:
                key = f'{prefix}{lang_key}'
                style_key = f'{key}_style'
                if not config['fortnite'][key]:
                    continue

                def fix_cosmetic_style_config():
                    if 'AthenaDance' in item or not config['fortnite'][style_key]:
                        return
                    for num, style_info in enumerate(config['fortnite'][style_key]):
                        if self.get_config_variant(style_info) is not None:
                            continue
                        styles = self.searcher.search_style(
                            self.get_config_item_id(config['fortnite'][key]),
                            style_info
                        )
                        if len(styles) != 0:
                            style = styles[0]
                            config['fortnite'][style_key][num] = (
                                self.get_variant_str(style)
                            )
                        else:
                            self.send(
                                self.l(
                                    'not_found',
                                    self.l('style'),
                                    config['fortnite'][key]
                                ),
                                add_p=self.time,
                                file=sys.stderr
                            )

                if self.get_config_item_id(config['fortnite'][key]) is not None:
                    fix_cosmetic_style_config()
                    continue
                if config['fortnite'][key]:
                    old = re.compile(
                        r"<Item name='(?P<name>.+)' "
                        r"id='(?P<id>.+)'>"
                    )
                    match = old.match(config['fortnite'][key])
                    cosmetic = self.searcher.get_item(
                        match.group('id') if match is not None else config['fortnite'][key]
                    )
                    if cosmetic is None:
                        cosmetics = self.searcher.search_item_name_id(
                            config['fortnite'][key],
                            item
                        )
                        if len(cosmetics) != 0:
                            cosmetic = cosmetics[0]
                    if cosmetic is not None:
                        config['fortnite'][key] = (
                            self.get_item_str(cosmetic)
                        )
                        fix_cosmetic_style_config()
                    else:
                        self.send(
                            self.l(
                                'not_found',
                                self.l(lang_key),
                                config['fortnite'][key]
                            ),
                            add_p=self.time,
                            file=sys.stderr
                        )

            key = f'ng_{lang_key}s'
            if not config['fortnite'][key]:
                continue
            for num, value in enumerate(config['fortnite'][key]):
                if self.get_config_item_id(value) is not None:
                    continue
                if value:
                    cosmetic = self.searcher.get_item(
                        value
                    )
                    if cosmetic is None:
                        cosmetics = self.searcher.search_item_name_id(
                            value,
                            item
                        )
                        if len(cosmetics) != 0:
                            cosmetic = cosmetics[0]
                    if cosmetic is not None:
                        config['fortnite'][key][num] = (
                            self.get_item_str(cosmetic)
                        )
                    else:
                        self.send(
                            self.l(
                                'not_found',
                                self.l(lang_key),
                                value
                            ),
                            add_p=self.time,
                            file=sys.stderr
                        )

    def fix_cosmetic_config_all(self) -> None:
        for config in self.config['clients']:
            self.fix_cosmetic_config(config)

    async def reboot(self) -> None:
        await self.close()
        os.execv(sys.executable, [sys.executable, sys.argv[0], *sys.argv[1:]])

    async def close(self) -> None:
        if self.server is not None:
            await self.server.close()

        coros = {client.wait_until_ready() for client in self.clients}
        if coros:
            await asyncio.wait(coros)
        await fortnitepy.close_multiple(
            [client for client in self.clients if client.is_ready() or client.is_booting()]
        )
        await self.http.close()

    async def rebooter(self) -> None:
        await asyncio.sleep(self.config['restart_in'])
        await self.reboot()

    async def save_command_stats(self) -> None:
        while True:
            await asyncio.sleep(60)
            self.store_command_stats()

    async def keep_alive(self) -> None:
        url = None
        if self.mode == 'glitch':
            url = f'https://{os.getenv("PROJECT_DOMAIN")}.glitch.me'
        elif self.mode == 'repl':
            url = f'https://{os.getenv("REPL_SLUG")}.{os.getenv("REPL_OWNER")}.repl.co'
        await self.http.post('https://PublicPinger.gomashio1596.repl.co/api/add', json={'url': url})
        while True:
            await asyncio.sleep(300)
            await self.http.get(url)

    async def start(self) -> None:
        self.send(
            self.l('credit'),
            color=cyan
        )
        self.send(
             f'{self.l("loglevel", self.l("loglevel_" + self.config["loglevel"]))}\n',
            color=green
        )

        if self.config['debug']:
            logger = logging.getLogger('fortnitepy.auth')
            logger.setLevel(level=logging.DEBUG)
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(logging.Formatter('\u001b[35m %(asctime)s:%(levelname)s:%(name)s: %(message)s \u001b[0m'))
            logger.addHandler(handler)

            logger = logging.getLogger('fortnitepy.http')
            logger.setLevel(level=logging.DEBUG)
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(logging.Formatter('\u001b[35m %(asctime)s:%(levelname)s:%(name)s: %(message)s \u001b[0m'))
            logger.addHandler(handler)

            logger = logging.getLogger('fortnitepy.xmpp')
            logger.setLevel(level=logging.DEBUG)
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(logging.Formatter('\u001b[35m %(asctime)s:%(levelname)s:%(name)s: %(message)s \u001b[0m'))
            logger.addHandler(handler)

        version = sys.version_info
        if version.minor != 7:
            self.send(
                self.l(
                    'not_recommended_version',
                    platform.python_version()
                ),
                color=yellow
            )
        python_64bit = sys.maxsize > 2 ** 32
        if sys.platform == 'win32':
            os_64bit = os.getenv('PROCESSOR_ARCHITECTURE') != 'x86'
        elif sys.platform == 'linux':
            output = subprocess.check_output(['uname', '-a']).decode()
            os_64bit = 'x86_64' in output or 'amd64' in output
        elif sys.platform == 'darwin':
            os_64bit = (
                subprocess.check_output(['uname', '-a']).decode()
            ).endswith('x86_64')
        else:
            os_64bit = python_64bit
        if os_64bit and not python_64bit:
            self.send(
                self.l(
                    'bit_mismatch',
                    '64' if python_64bit else '32',
                    '64' if os_64bit else '32'
                ),
                color=yellow
            )

        if self.config['check_update_on_startup']:
            if await self.updater.check_updates(self.dev):
                await self.reboot()
                sys.exit(0)

        if not self.is_error() and self.config['status'] == 1:
            self.send(
                self.l(
                    'updating',
                ),
                add_p=self.time
            )
            await self.update_data()
            self.load_data()
            self.searcher = Searcher(
                self,
                self.main_items,
                self.sub_items,
                self.main_playlists,
                self.sub_playlists,
                True,
                False
            )
            self.send(
                self.l(
                    'booting',
                ),
                add_p=self.time
            )
            if self.config['restart_in']:
                self.loop.create_task(self.rebooter())
            self.loop.create_task(self.save_command_stats())
            if self.mode != 'pc' and self.config['web']['enabled']:
                self.loop.create_task(self.keep_alive())
        if self.config['web']['enabled'] or self.config['status'] == 0:
            if not self.config['web']['access_log']:
                logger = getLogger('sanic.root')
                logger.setLevel(WARNING)
            try:
                self.server = await self.web.create_server(
                    host=self.config['web']['ip'],
                    port=self.config['web']['port'],
                    access_log=self.config['web']['access_log'],
                    return_asyncio_server=True
                )
            except OSError as e:
                self.debug_print_exception(e)
                self.send(
                    self.l(
                        'web_already_running'
                    ),
                    add_p=self.time,
                    file=sys.stderr
                )
            else:
                if self.mode == 'glitch':
                    url = f'https://{os.getenv("PROJECT_DOMAIN")}.glitch.me'
                elif self.mode == 'repl':
                    url = f'https://{os.getenv("REPL_SLUG")}--{os.getenv("REPL_OWNER")}.repl.co'
                else:
                    url = f"http://{self.config['web']['ip']}:{self.config['web']['port']}"
                self.send(
                    self.l(
                        'web_running',
                        url
                    ),
                    color=green,
                    add_p=self.time
                )
                if (self.mode == 'repl' and (not self.config['web']['login_required']
                        or (self.config['web']['login_required'] and not self.config['web']['password']))):
                    self.send(
                        self.l('password_not_set'),
                        color=yellow
                    )

        if not self.is_error() and self.config['status'] == 1:
            self.fix_config_all()
            self.save_json('config', self.config)
            refresh_tokens = {}
            device_auths = {}
            if self.use_device_auth:
                try:
                    device_auths = self.get_device_auth_details()
                except (json.decoder.JSONDecodeError, UnicodeDecodeError) as e:
                    self.debug_print_exception(e)
                    if self.isfile('device_auths_old'):
                        self.remove('device_auths_old')
                    self.rename('device_auths', 'device_auths_old')
                    try:
                        self.remove('device_auths')
                    except Exception as e:
                        self.debug_print_exception(e)
            else:
                try:
                    refresh_tokens = self.get_refresh_tokens()
                except (json.decoder.JSONDecodeError, UnicodeDecodeError) as e:
                    self.debug_print_exception(e)
                    if self.isfile('refresh_tokens_old'):
                        self.remove('refresh_tokens_old')
                    self.rename('refresh_tokens', 'refresh_tokens_old')
                    try:
                        self.remove('refresh_tokens')
                    except Exception as e:
                        self.debug_print_exception(e)

            def session_id(email):
                async def _session_id():
                    while True:
                        text = self.l('session_id', email).get_text()
                        self.web_text = text
                        data = await ainput(f'{text}\n')
                        match = re.search(r'[a-z0-9]{32}', data)
                        if match is not None:
                            return match.group()

                return _session_id

            for num, config in enumerate(self.config['clients']):
                refresh_token = refresh_tokens.get(config['fortnite']['email'].lower(), None)
                device_auth_details = device_auths.get(config['fortnite']['email'].lower(), {})

                party_meta = []
                if config['fortnite']['party']['playlist']:
                    party_meta.append(partial(
                        MyClientParty.set_playlist,
                        playlist=(self.get_config_playlist_id(config['fortnite']['party']['playlist'])
                                  or config['fortnite']['party']['playlist'])
                    ))
                if config['fortnite']['party']['disable_voice_chat']:
                    party_meta.append(partial(
                        MyClientParty.disable_voice_chat
                    ))

                member_meta = [
                    partial(
                        MyClientPartyMember.set_banner,
                        icon=config['fortnite']['banner_id'],
                        color=config['fortnite']['banner_color'],
                        season_level=config['fortnite']['level']
                    ),
                    partial(
                        MyClientPartyMember.set_battlepass_info,
                        has_purchased=True,
                        level=config['fortnite']['tier']
                    )
                ]
                items = [
                    'AthenaCharacter',
                    'AthenaBackpack',
                    'AthenaPickaxe',
                    'AthenaDance'
                ]
                for item in items:
                    conf = self.convert_backend_type(item)
                    variants = []
                    if item != 'AthenaDance' and config['fortnite'][f'{conf}_style'] is not None:
                        for style in config['fortnite'][f'{conf}_style']:
                            variant = self.get_config_variant(style)
                            if variant is not None:
                                variants.extend(variant['variants'])
                    section = 0
                    if item == 'AthenaDance':
                        section = config['fortnite'][f'{conf}_section']
                    coro = fortnitepy.EditEntry(
                        MyClientPartyMember.change_asset,
                        item,
                        (self.get_config_item_path(config['fortnite'][conf])
                         or config['fortnite'][conf]),
                        variants=variants,
                        section=section,
                        keep=False,
                        name=f'ClientPartyMember.set_{conf}'
                    )
                    member_meta.append(coro)

                avatar = fortnitepy.kairos.get_random_default_avatar()
                background_colors = (
                    config['fortnite']['avatar_color'].split(',')
                    if ',' in config['fortnite']['avatar_color'] else
                    getattr(fortnitepy.KairosBackgroundColorPreset, config['fortnite']['avatar_color'].upper())
                )

                auth = None
                if self.use_device_auth and device_auth_details:
                    auth = fortnitepy.DeviceAuth(**device_auth_details)
                if auth is None:
                    if self.use_device_code:
                        auth = MyAdvancedAuth(refresh_token)
                    else:
                        auth = MyAdvancedAuth(refresh_token, session_id(config['fortnite']['email']))

                client = Client(
                    self,
                    config,
                    num,
                    auth=auth,
                    avatar=fortnitepy.Avatar(
                        asset=(
                            config['fortnite']['avatar_id']
                            or avatar.asset
                        ),
                        background_colors=(
                            background_colors
                            if config['fortnite']['avatar_color'] else
                            avatar.background_colors
                        )
                    ),
                    status=config['fortnite']['status'],
                    platform=config['fortnite']['platform'],
                    wait_for_member_meta_in_events=False,
                    loop=self.loop
                )

                client.default_party_config = fortnitepy.DefaultPartyConfig(
                    cls=MyClientParty,
                    privacy=config['fortnite']['party']['privacy'],
                    team_change_allowed=config['fortnite']['party']['allow_swap'],
                    max_size=config['fortnite']['party']['max_size'],
                    meta=party_meta
                )
                client.default_party_member_config = fortnitepy.DefaultPartyMemberConfig(
                    cls=MyClientPartyMember,
                    meta=member_meta
                )
                self.clients.append(client)

            if len(self.clients) == 0:
                self.send(
                    self.l('no_clients')
                )
                while True:
                    await asyncio.sleep(0.1)
            else:
                tasks = [
                    fortnitepy.start_multiple(
                        self.clients,
                        shutdown_on_error=False,
                        error_callback=self.error_callback,
                        all_ready_callback=self.all_ready_callback
                    )
                ]
                if self.discord_client is not None and self.config['discord']['token']:
                    tasks.append(self.discord_client.start(self.config['discord']['token']))

                try:
                    await asyncio.gather(*tasks)
                except Exception as e:
                    self.print_exception(e)
        while True:
            await asyncio.sleep(0.1)

    async def process_command(self, message: MyMessage, *args: Any, **kwargs: Any) -> None:
        if not message.args:
            return
        for client in self.clients:
            message.client = client
            self.loop.create_task(client.process_command(message, None))
