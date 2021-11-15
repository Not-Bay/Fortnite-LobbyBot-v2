# -*- coding: utf-8 -*-
import asyncio
import datetime
import importlib
import inspect
import io
import random
import re
import sys
from functools import partial
from typing import (TYPE_CHECKING, Any, Awaitable, Callable, Dict, List,
                    Optional, Tuple, Type, Union)

import jaconv

from .colors import blue, green, magenta, yellow
from .commands import (Command, DummyMessage, DummyUser, FindUserMatchMethod,
                       FindUserMode, MyMessage)
from .cosmetics import Searcher
from .discord_client import DiscordClient
from .localize import LocalizedText
from .web import auth
from .webhook import WebhookClient

if TYPE_CHECKING:
    from .bot import Bot

aioxmpp = importlib.import_module('aioxmpp')
discord = importlib.import_module('discord')
fortnitepy = importlib.import_module('fortnitepy')


class MyClientPartyMember(fortnitepy.ClientPartyMember):
    ASSET_CONVERTER = {
        'AthenaCharacter': fortnitepy.ClientPartyMember.outfit,
        'AthenaBackpack': fortnitepy.ClientPartyMember.backpack,
        'AthenaPet': fortnitepy.ClientPartyMember.backpack,
        'AthenaPetCarrier': fortnitepy.ClientPartyMember.backpack,
        'AthenaPickaxe': fortnitepy.ClientPartyMember.pickaxe,
        'AthenaDance': fortnitepy.ClientPartyMember.emote,
        'AthenaEmoji': fortnitepy.ClientPartyMember.emote,
        'AthenaToy': fortnitepy.ClientPartyMember.emote,
        'AthenaConsumableEmote': fortnitepy.ClientPartyMember.emote
    }
    VARIANTS_CONVERTER = {
        'AthenaCharacter': fortnitepy.ClientPartyMember.outfit_variants,
        'AthenaBackpack': fortnitepy.ClientPartyMember.backpack_variants,
        'AthenaPet': fortnitepy.ClientPartyMember.backpack_variants,
        'AthenaPetCarrier': fortnitepy.ClientPartyMember.backpack_variants,
        'AthenaPickaxe': fortnitepy.ClientPartyMember.pickaxe_variants,
        'AthenaDance': None,
        'AthenaEmoji': None,
        'AthenaToy': None,
        'AthenaConsumableEmote': None
    }
    ASSET_PATH_CONVERTER = {
        'AthenaCharacter': ("AthenaCharacterItemDefinition'/Game/Athena/Items/"
                            "Cosmetics/Characters/{0}.{0}'"),
        'AthenaBackpack': ("AthenaBackpackItemDefinition'/Game/Athena/Items/"
                           "Cosmetics/Backpacks/{0}.{0}'"),
        'AthenaPet': ("AthenaPetItemDefinition'/Game/Athena/Items/"
                      "Cosmetics/Pets/{0}.{0}'"),
        'AthenaPetCarrier': ("AthenaPetCarrierItemDefinition'/Game/Athena/Items/"
                             "Cosmetics/PetCarriers/{0}.{0}'"),
        'AthenaPickaxe': ("AthenaPickaxeItemDefinition'/Game/Athena/Items/"
                          "Cosmetics/Pickaxes/{0}.{0}'"),
        'AthenaDance': ("AthenaDanceItemDefinition'/Game/Athena/Items/"
                        "Cosmetics/Dances/{0}.{0}'"),
        'AthenaEmoji': ("AthenaDanceItemDefinition'/Game/Athena/Items/"
                        "Cosmetics/Dances/Emoji/{0}.{0}'"),
        'AthenaToy': ("AthenaToyItemDefinition'/Game/Athena/Items/"
                      "Cosmetics/Toys/{0}.{0}'"),
        'AthenaConsumableEmote': ("AthenaConsumableEmoteItemDefinition'/Game/Athena/Items/"
                                  "Cosmetics/ConsumableEmotes/{0}.{0}"),
        'HolidayCracker': ("AthenaDanceItemDefinition'/Game/Athena/Items/"
                           "Cosmetics/Dances/HolidayCracker/{0}.{0}'"),
        'PapayaComms': ("AthenaDanceItemDefinition'/Game/Athena/Items/"
                        "Cosmetics/Dances/PapayaComms/{0}.{0}'"),
        'Chugga': ("AthenaDanceItemDefinition'/Game/Athena/Items/"
                   "Cosmetics/Dances/Chugga/{0}.{0}'"),
        'PatPat': ("AthenaDanceItemDefinition'/Game/Athena/Items/"
                   "Cosmetics/Dances/PatPat/{0}.{0}'")
    }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.ASSET_FUNCTION_CONVERTER = {
            'AthenaCharacter': self.set_outfit,
            'AthenaBackpack': self.set_backpack,
            'AthenaPet': self.set_backpack,
            'AthenaPetCarrier': self.set_backpack,
            'AthenaPickaxe': self.set_pickaxe,
            'AthenaDance': self.set_emote,
            'AthenaEmoji': self.set_emote,
            'AthenaToy': self.set_emote,
            'AthenaConsumableEmote': self.set_emote
        }

    @classmethod
    def get_asset_path(cls, item: str, asset: Optional[str] = None) -> str:
        if asset is not None:
            if asset != '' and '.' not in asset:
                if item == 'AthenaDance':
                    if asset.lower().startswith('eid_holidaycracker'):
                        item = 'HolidayCracker'
                    elif asset.lower().endswith('papayacomms'):
                        item = 'PapayaComms'
                    elif  asset.lower().startswith('eid_chugga'):
                        item = 'Chugga'
                    elif  asset.lower().startswith('eid_patpat'):
                        item = 'PatPat'
                asset = cls.ASSET_PATH_CONVERTER[item].format(asset)
        return asset

    def asset(self, item: str) -> Optional[str]:
        p = self.ASSET_CONVERTER.get(item)
        if p is None:
            return None
        return p.fget(self)

    def variants(self, item: str) -> list:
        p = self.VARIANTS_CONVERTER.get(item)
        if p is None:
            return []
        return p.fget(self)

    async def change_asset(self, item: str,
                           asset: Optional[str] = None,
                           keep: Optional[bool] = True,
                           do_point: Optional[bool] = True, **kwargs: Any) -> bool:
        asset = self.get_asset_path(item, asset)
        if item == 'AthenaPickaxe' and not asset:
            asset = 'DefaultPickaxe'
        kwargs['variants'] = kwargs.get('variants', []) or []
        if asset is not None and 'banner' in asset.lower():
            kwargs['variants'].extend(self.create_variant(
                profile_banner='ProfileBanner'
            ))
        kwargs['enlightenment'] = kwargs.get('enlightenment') or None
        kwargs['corruption'] = kwargs.get('corruption') or None
        kwargs['run_for'] = kwargs.get('run_for')
        kwargs['section'] = kwargs.get('section')

        func = self.ASSET_FUNCTION_CONVERTER[item]
        if item in ['AthenaCharacter', 'AthenaBackpack', 'AthenaPet', 'AthenaPetCarrier']:  # outfit and backpack
            keys = ['run_for', 'section']
            for key in keys:
                kwargs.pop(key, None)
            if self.client.config['fortnite']['avatar_id'] == '{bot}':
                self.client.set_avatar(fortnitepy.Avatar(
                    asset=asset.split('/')[-1].split('.')[0],
                    background_colors=(
                        self.client.avatar.background_colors
                        if self.client.avatar is not None else
                        None
                    )
                ))
            if keep:
                await self.edit_and_keep(
                    partial(func, asset=asset, **kwargs)
                )
            else:
                await func(asset=asset, **kwargs)
        elif item in ['AthenaDance', 'AthenaEmoji', 'AthenaToy']:  # emote
            keys = ['variants', 'enlightenment', 'corruption']
            for key in keys:
                kwargs.pop(key, None)
            if asset is None:
                await self.clear_emote()
                if keep:
                    self.client.emote = None
                    self.client.emote_section = None
            else:
                asset_id = re.search(r".*\.([^\'\"]*)", asset.strip("'"))
                if (self.asset(item) is not None and asset_id is not None
                        and self.asset(item).lower() == asset_id.group(1).lower()):
                    await self.clear_emote()
                await func(asset=asset, **kwargs)
                if keep:
                    self.client.emote = asset
                    self.client.emote_section = kwargs.get('section')
        else:  # other things
            keys = ['enlightenment', 'corruption', 'run_for', 'section']
            for key in keys:
                kwargs.pop(key, None)
            if keep:
                await self.edit_and_keep(
                    partial(func, asset=asset, **kwargs)
                )
            else:
                await func(asset=asset, **kwargs)
            if item == 'AthenaPickaxe' and do_point and self.client.do_point:
                await self.change_asset(
                    'AthenaDance',
                    'EID_IceKing',
                    keep=False
                )
        return True

    async def hide(self) -> None:
        if self.client.is_creating_party():
            return

        if not self.party.me.leader:
            raise fortnitepy.Forbidden('You must be the party leader '
                                       'to perform this action')
        party = self.party
        if party != self.client.party:
            raise fortnitepy.PartyError('Client is not belong to '
                                        'this member\'s party')

        if not isinstance(self.party, fortnitepy.ClientParty):
            party = self.client.party

        if party.add_hide_user(self.id):
            await party.refresh_squad_assignments()

    async def show(self) -> None:
        if self.client.is_creating_party():
            return

        if not self.party.me.leader:
            raise fortnitepy.Forbidden('You must be the party leader '
                                       'to perform this action')
        party = self.party
        if party != self.client.party:
            raise fortnitepy.PartyError('Client is not belong to '
                                        'this member\'s party')

        if not isinstance(self.party, fortnitepy.ClientParty):
            party = self.client.party

        if party.remove_hide_user(self.id):
            await party.refresh_squad_assignments()


class MyClientParty(fortnitepy.ClientParty):
    def __init__(self, client: 'Client', data: dict) -> None:
        super().__init__(client, data)
        self._hides = []
        self.party_chat = []

    @property
    def voice_chat_enabled(self) -> bool:
        return self.meta.get_prop('VoiceChat:implementation_s') in [
            'VivoxVoiceChat',
            'EOSVoiceChat'
        ]

    def update_hide_users(self, user_ids: List[str]) -> None:
        self._hides = user_ids

    def add_hide_user(self, user_id: str) -> bool:
        if user_id not in self._hides:
            self._hides.append(user_id)
            return True
        return False

    def remove_hide_user(self, user_id: str) -> bool:
        if user_id in self._hides:
            self._hides.remove(user_id)
            return True
        return False

    async def hide(self, member: fortnitepy.PartyMember) -> None:
        if self.me is not None and not self.me.leader:
            raise fortnitepy.Forbidden('You have to be leader for this action to work.')

        self.add_hide_user(member.id)
        if member.id in self._members.keys():
            await self.refresh_squad_assignments()

    async def show(self, member: fortnitepy.PartyMember) -> None:
        if self.me is not None and not self.me.leader:
            raise fortnitepy.Forbidden('You have to be leader for this action to work.')

        self.remove_hide_user(member.id)
        if member.id in self._members.keys():
            await self.refresh_squad_assignments()

    def _convert_squad_assignments(self, assignments):
        results = []
        sub = 0
        for member, assignment in assignments.items():
            if assignment.hidden or member.id in self._hides:
                sub += 1
                continue

            results.append({
                'memberId': member.id,
                'absoluteMemberIdx': assignment.position - sub,
            })

        return results

    async def disable_voice_chat(self) -> None:
        if self.me is not None and not self.me.leader:
            raise fortnitepy.Forbidden('You have to be leader for this action to work.')

        prop = self.meta.set_voicechat_implementation('None')
        if not self.edit_lock.locked():
            await self.patch(updated=prop)

    async def enable_voice_chat(self) -> None:
        if self.me is not None and not self.me.leader:
            raise fortnitepy.Forbidden('You have to be leader for this action to work.')

        prop = self.meta.set_voicechat_implementation('EOSVoiceChat')
        if not self.edit_lock.locked():
            await self.patch(updated=prop)

    def construct_presence(self, text: Optional[str] = None) -> dict:
        perm = self.config['privacy']['presencePermission']
        if perm == 'Noone' or (perm == 'Leader' and (self.me is not None
                                                     and not self.me.leader)):
            join_data = {
                'bInPrivate': True
            }
        else:
            join_data = {
                'sourceId': self.client.user.id,
                'sourceDisplayName': self.client.user.display_name,
                'sourcePlatform': self.client.platform.value,
                'partyId': self.id,
                'partyTypeId': 286331153,
                'key': 'k',
                'appId': 'Fortnite',
                'buildId': self.client.party_build_id,
                'partyFlags': -2024557306,
                'notAcceptingReason': 0,
                'pc': self.member_count,
            }

        status = text or self.client.status
        kairos_profile = self.client.avatar.to_dict()
        kairos_profile['avatar'] = kairos_profile['avatar'].format(
            bot=self.me.outfit
        )

        try:
            status  = self.client.eval_format(
                status,
                self.client.variables
            )
        except Exception:
            status = None

        _default_status = {
            'Status': status,
            'bIsPlaying': False,
            'bIsJoinable': False,
            'bHasVoiceSupport': False,
            'SessionId': '',
            'ProductName': 'Fortnite',
            'Properties': {
                'KairosProfile_j': kairos_profile,
                'party.joininfodata.286331153_j': join_data,
                'FortBasicInfo_j': {
                    'homeBaseRating': 1,
                },
                'FortLFG_I': '0',
                'FortPartySize_i': 1,
                'FortSubGame_i': 1,
                'InUnjoinableMatch_b': False,
                'FortGameplayStats_j': {
                    'state': '',
                    'playlist': 'None',
                    'numKills': 0,
                    'bFellToDeath': False,
                },
                'GamePlaylistName_s': self.meta.playlist_info[0],
                'Event_PlayersAlive_s': '0',
                'Event_PartySize_s': str(len(self._members)),
                'Event_PartyMaxSize_s': str(self.max_size),
            },
        }
        return _default_status


class Client(fortnitepy.Client):
    ASSET_CONVERTER = {
        'AthenaCharacter': fortnitepy.PartyMember.outfit,
        'AthenaBackpack': fortnitepy.PartyMember.backpack,
        'AthenaPet': fortnitepy.PartyMember.backpack,
        'AthenaPetCarrier': fortnitepy.PartyMember.backpack,
        'AthenaPickaxe': fortnitepy.PartyMember.pickaxe,
        'AthenaDance': fortnitepy.PartyMember.emote,
        'AthenaEmoji': fortnitepy.PartyMember.emote,
        'AthenaToy': fortnitepy.PartyMember.emote,
        'AthenaConsumableEmote': fortnitepy.PartyMember.emote
    }
    VARIANTS_CONVERTER = {
        'AthenaCharacter': fortnitepy.PartyMember.outfit_variants,
        'AthenaBackpack': fortnitepy.PartyMember.backpack_variants,
        'AthenaPet': fortnitepy.PartyMember.backpack_variants,
        'AthenaPetCarrier': fortnitepy.PartyMember.backpack_variants,
        'AthenaPickaxe': fortnitepy.PartyMember.pickaxe_variants,
        'AthenaDance': None,
        'AthenaEmoji': None,
        'AthenaToy': None,
        'AthenaConsumableEmote': None
    }
    PLATFORM_CONVERTER = {
        fortnitepy.Platform.WINDOWS: "Windows",
        fortnitepy.Platform.MAC: "Mac",
        fortnitepy.Platform.PLAYSTATION: "PlayStation 4",
        fortnitepy.Platform.PLAYSTATION_5: "PlayStation 5",
        fortnitepy.Platform.XBOX: "Xbox One",
        fortnitepy.Platform.XBOX_X: "Xbox One X",
        fortnitepy.Platform.XBOX_S: "Xbox One S",
        fortnitepy.Platform.XBOX_SERIES_X: "Xbox Series X",
        fortnitepy.Platform.XBOX_SERIES_S: "Xbox Series S",
        fortnitepy.Platform.SWITCH: "Switch",
        fortnitepy.Platform.IOS: "IOS",
        fortnitepy.Platform.ANDROID: "Android"
    }

    def __init__(self, bot: 'Bot', config: dict, num: int,
                 auth: fortnitepy.Auth, *, loop: asyncio.AbstractEventLoop = None,
                 **kwargs) -> None:
        self.bot = bot
        self.config = config
        self.num = num
        self.commands = self.bot.commands
        self.localize = self.bot.localize
        self.all_commands = self.bot.all_commands
        self.whitelist_commands = self.bot.whitelist_commands
        self.user_commands = self.bot.user_commands
        self.custom_commands = self.bot.custom_commands
        self.replies = self.bot.replies
        self.disabled_replies = []
        self.searcher = Searcher(
            self.bot,
            self.bot.main_items,
            self.bot.sub_items,
            self.bot.main_playlists,
            self.bot.sub_playlists,
            self.config['case_insensitive'],
            self.config['convert_kanji']
        )

        super().__init__(auth, loop=loop, **kwargs)

        self._is_booting = False
        self.booted_at = None
        self.emote = None
        self.emote_section = None
        self.do_point = self.config['fortnite']['do_point']

        self.email = self.config['fortnite']['email']
        self.config_user_pattern = re.compile(
            r"<User id='(?P<id>[a-z0-9]{32})' "
            r"display_name=(?P<display_name>('.+'|None)) "
            r"external_auths=(?P<external_auths>\["
            r"(\"<ExternalAuth external_id=('.+'|None) "
            r"external_display_name=('.+'|None) "
            r"type='.+'>\")?(, \"<ExternalAuth external_id=('.+'|None) "
            r"external_display_name=('.+'|None) "
            r"type='.+'>\")*"
            r"\])>"
        )
        self.return_pattern = re.compile(
            r"(?P<space>\s*)(return|return\s+(?P<text>.*))\s*"
        )
        self.muc_pattern = re.compile(
            r"Party-(?P<party_id>.+)@muc.prod.ol.epicgames.com"
        )
        self._members = {}

        _events = [
            'party_member_kick',
            'party_member_zombie',
            'party_member_reconnect',
            'party_member_expire',
            'party_member_update',
            'party_member_join',
            'party_member_leave'
        ]
        for event in _events:
            self.add_event_handler(event, self.store_member_event)
        self.add_event_handler('party_member_chatban', self.store_chatban_event)
        self.add_event_handler('party_member_promote', self.store_leader_event)
        self.add_event_handler('party_member_confirm', self.store_join_confirmation_event)

        self.webhook = WebhookClient(self, self.bot, self.loop, self.bot.http)
        self.webhook.start()

        self.prev = {}
        self.select = {}
        self.party_hides = {}
        self.join_requests = {}
        self.invites = {}
        self.stoppable_tasks = []
        self.invite_interval = False
        self.invite_interval_handle = None

        self.outfit_mimic = []
        self.backpack_mimic = []
        self.pickaxe_mimic = []
        self.emote_mimic = []
        self._owner = {}
        self._whitelist = {}
        self._blacklist = {}
        self._botlist = {}
        self._invitelist = {}
        self.whisper = {}
        self.party_chat = {
            'party_id': None,
            'party_chat': []
        }

        async def _store_whisper(to, author, content):
            if to not in self.whisper:
                self.whisper[to] = {'display_name': (await self.fetch_user(to, cache=True)).display_name, 'content': []}
            self.whisper[to]['content'].append({
                'author': {
                    'id': author.id,
                    'display_name': author.display_name
                },
                'content': content,
                'received_at': self.bot.strftime(datetime.datetime.utcnow())
            })
            self.dispatch_event(
                'store_whisper',
                to,
                self.whisper[to]['content'][-1]
            )

        async def store_whisper(message):
            await _store_whisper(message.author.id, message.author, message.content)

        self.add_event_handler('friend_message', store_whisper)

        async def store_sent_whisper(author, content):
            await _store_whisper(author.id, self.user, content)

        self.add_event_handler('friend_message_send', store_sent_whisper)

        def _store_party_chat(party, author, content):
            if party.id != self.party_id or self.party_id is None:
                return
            if self.party_chat['party_id'] is None:
                self.party_chat['party_id'] = self.party_id
            if self.party_id != self.party_chat['party_id']:
                self.party_chat['party_id'] = self.party_id
                self.party_chat['party_chat'].clear()
                self.dispatch_event('clear_party_chat')
            self.party_chat['party_chat'].append({
                'author': {
                    'id': author.id,
                    'display_name': author.display_name
                },
                'content': content,
                'received_at': self.bot.strftime(datetime.datetime.utcnow())
            })
            self.dispatch_event(
                'store_party_chat',
                self.party_chat['party_chat'][-1]
            )

        async def store_party_chat(message):
            _store_party_chat(message.author.party, message.author, message.content)

        self.add_event_handler('party_message', store_party_chat)

        async def store_sent_party_chat(party, content):
            _store_party_chat(party, self.user, content)

        self.add_event_handler('party_message_send', store_sent_party_chat)

        async def store_member_join(member):
            system = fortnitepy.User.__new__(fortnitepy.User)
            system._epicgames_display_name = 'System'
            system._external_display_name = 'System'
            system._id = None
            system._external_auths = []
            _store_party_chat(
                member.party,
                system,
                self.bot.web.l('party_joined', member.display_name).get_text()
            )

        self.add_event_handler('party_member_join', store_member_join)

        async def store_member_leave(member):
            system = fortnitepy.User.__new__(fortnitepy.User)
            system._epicgames_display_name = 'System'
            system._external_display_name = 'System'
            system._id = None
            system._external_auths = []
            _store_party_chat(
                member.party,
                system,
                self.bot.web.l('party_left', member.display_name).get_text()
            )

        self.add_event_handler('party_member_leave', store_member_leave)
        self.add_event_handler('party_member_kick', store_member_leave)

        self.OPERATION_FUNC_CONVERTER = {
            'kick': fortnitepy.PartyMember.kick,
            'chatban': fortnitepy.PartyMember.chatban,
            'remove': fortnitepy.Friend.remove,
            'block': fortnitepy.User.block,
            'blacklist': self.add_to_blacklist
        }

        if self.config['discord']['enabled']:
            self.discord_client = DiscordClient(self, self.config, loop=self.loop)
        else:
            self.discord_client = None

    # Overrides
    @property
    def _caches(self) -> dict:
        return {
            **self._members,
            **self._blocked_users,
            **self._pending_friends,
            **self._friends,
            **self._users
        }

    def is_booting(self) -> bool:
        return self._is_booting

    def is_incoming_pending(self, user_id: str) -> bool:
        return self.get_incoming_pending_friend(user_id) is not None

    def is_outgoing_pending(self, user_id: str) -> bool:
        return self.get_outgoing_pending_friend(user_id) is not None

    def store_member(self, member: fortnitepy.party.PartyMemberBase,
                     *, try_cache: bool = True) -> fortnitepy.party.PartyMemberBase:
        try:
            if try_cache:
                return self._members[member.id]
        except KeyError:
            pass

        self._members[member.id] = member
        return member

    def get_member(self, user_id: str) -> Optional[fortnitepy.party.PartyMemberBase]:
        return self._members.get(user_id)

    def get_as_user(self, user: Type[fortnitepy.user.UserBase]) -> fortnitepy.User:
        return fortnitepy.User(self, user.get_raw())

    def get_cache_user(self, user_id: str) -> Optional[fortnitepy.User]:
        tries = [
            self.get_user,
            self.get_friend,
            self.get_pending_friend,
            self.get_blocked_user,
            self.get_member
        ]
        for func in tries:
            u = func(user_id)
            if u is not None:
                return self.get_as_user(u)

    def refresh_caches(self, priority: int = 0) -> callable:
        self._members.clear()
        return super().refresh_caches(priority)

    async def store_member_event(self, member: fortnitepy.PartyMember) -> None:
        self.store_member(member)

    async def store_chatban_event(self, member: fortnitepy.PartyMember, reason: Optional[str]) -> None:
        self.store_member(member)

    async def store_leader_event(self, old: fortnitepy.PartyMember, new: fortnitepy.PartyMember) -> None:
        self.loop.create_task(self.store_member_event(old))
        self.loop.create_task(self.store_member_event(new))

    async def store_join_confirmation_event(self, confirmation: fortnitepy.PartyJoinConfirmation) -> None:
        self.store_user(confirmation.user.get_raw())

    async def fetch_users(self, users, *,
                          cache: bool = False,
                          raw: bool = False) -> List[fortnitepy.User]:
        if len(users) == 0:
            return []

        _users = []
        new = []
        tasks = []

        def find_by_display_name(dn):
            if cache:
                for u in self._caches.values():
                    try:
                        if u.display_name is not None:
                            if u.display_name.casefold() == dn.casefold():
                                _users.append(u)
                                return
                    except AttributeError:
                        pass

            task = self.http.account_graphql_get_by_display_name(elem)
            tasks.append(task)

        for elem in users:
            if self.is_display_name(elem):
                find_by_display_name(elem)
            else:
                if cache:
                    p = self.get_cache_user(elem)
                    if p:
                        if raw:
                            _users.append(p.get_raw())
                        else:
                            _users.append(p)
                        continue
                new.append(elem)

        if len(tasks) > 0:
            pfs = await asyncio.gather(*tasks)
            for p_data in pfs:
                accounts = p_data['account']
                for account_data in accounts:
                    if account_data['displayName'] is not None:
                        new.append(account_data['id'])
                        break
                else:
                    for account_data in accounts:
                        if account_data['displayName'] is None:
                            new.append(account_data['id'])
                            break

        chunk_tasks = []
        chunks = [new[i:i + 100] for i in range(0, len(new), 100)]
        for chunk in chunks:
            task = self.http.account_graphql_get_multiple_by_user_id(chunk)
            chunk_tasks.append(task)

        if len(chunks) > 0:
            d = await asyncio.gather(*chunk_tasks)
            for results in d:
                for result in results['accounts']:
                    if raw:
                        _users.append(result)
                    else:
                        u = self.store_user(result, try_cache=cache)
                        _users.append(u)
        return _users

    async def fetch_multiple_users(self, user_ids: List[str]) -> Dict[str, fortnitepy.User]:
        if len(user_ids) == 0:
            return {}

        chunk_tasks = []
        chunks = [user_ids[i:i + 100] for i in range(0, len(user_ids), 100)]
        for chunk in chunks:
            task = self.http.account_graphql_get_multiple_by_user_id(chunk)
            chunk_tasks.append(task)

        users = {}
        if len(chunks) > 0:
            d = await asyncio.gather(*chunk_tasks)
            for results in d:
                for result in results['accounts']:
                    users[result['id']] = self.store_user(result, try_cache=False)
        return users

    async def join_party(self, party_id: str) -> fortnitepy.ClientParty:
        hides = self.party_hides.get(party_id)
        if hides is None:
            self.party_hides[party_id] = []
        party = await super().join_party(party_id)
        party.update_hide_users(self.party_hides[party_id])
        return party

    async def join_party_ping(self, party_id: str,
                              pinger_id: str) -> fortnitepy.ClientParty:
        hides = self.party_hides.get(party_id)
        if hides is None:
            self.party_hides[party_id] = []
        party = await super().join_party_ping(party_id, pinger_id)
        party.update_hide_users(self.party_hides[party_id])
        return party

    async def set_presence(self, status: str, *,
                           away: fortnitepy.AwayStatus = fortnitepy.AwayStatus.ONLINE) -> Callable:
        if not isinstance(status, str):
            raise TypeError('status must be a str')

        self.status = status
        self.away = away
        if self.party is not None:
            status = self.party.construct_presence(status)

        await self.xmpp.send_presence(
            status=status,
            show=away.value
        )

    async def send_presence(self, status: Union[str, dict], *,
                            away: fortnitepy.AwayStatus = fortnitepy.AwayStatus.ONLINE,
                            to: Optional[aioxmpp.JID] = None) -> None:
        if isinstance(status, str) and self.party is not None:
            status = self.party.construct_presence(status)

        await self.xmpp.send_presence(
            status=status,
            show=away.value,
            to=to
        )

    async def close(self, *args: Any, **kwargs: Any) -> None:
        tasks = [super().close(*args, **kwargs)]
        if self.discord_client is not None:
            tasks.append(self.discord_client.close())
        await asyncio.gather(*tasks)

    async def start(self, *args: Any, **kwargs: Any) -> None:
        self._is_booting = True
        try:
            tasks = [super().start(*args, **kwargs)]
            if self.discord_client is not None and self.discord_client.config['discord']['token']:
                tasks.append(self.discord_client.start(self.discord_client.config['discord']['token']))
            await asyncio.gather(*tasks)
        finally:
            self._is_booting = False


    # Error handling functions
    async def send_friend_request(self, user: Type[fortnitepy.user.UserBase],
                                  message: Optional[MyMessage] = None) -> Optional[Exception]:
        try:
            await user.add()
        except fortnitepy.DuplicateFriendship as e:
            self.debug_print_exception(e)
            text = self.l(
                'error_duplicate_friendship',
                self.name(user)
            )
            self.send(
                text,
                add_p=self.time,
                file=sys.stderr
            )
            if message is not None:
                await message.reply(text)
            return e
        except fortnitepy.FriendshipRequestAlreadySent as e:
            self.debug_print_exception(e)
            text = self.l(
                'error_friendship_request_already_sent',
                self.name(user)
            )
            self.send(
                text,
                add_p=self.time,
                file=sys.stderr
            )
            if message is not None:
                await message.reply(text)
            return e
        except fortnitepy.MaxFriendshipsExceeded as e:
            self.debug_print_exception(e)
            text = self.l(
                'error_max_friendships_exceeded_send',
                self.name(user)
            )
            self.send(
                text,
                add_p=self.time,
                file=sys.stderr
            )
            if message is not None:
                await message.reply(text)
            return e
        except fortnitepy.InviteeMaxFriendshipRequestsExceeded as e:
            self.debug_print_exception(e)
            text = self.l(
                'error_invitee_max_friendship_requests_exceeded',
                self.name(user)
            )
            self.send(
                text,
                add_p=self.time,
                file=sys.stderr
            )
            if message is not None:
                await message.reply(text)
            return e
        except fortnitepy.Forbidden as e:
            self.debug_print_exception(e)
            text = self.l(
                'error_forbidden_send',
                self.name(user)
            )
            self.send(
                text,
                add_p=self.time,
                file=sys.stderr
            )
            if message is not None:
                await message.reply(text)
            return e
        except Exception as e:
            m = 'errors.com.epicgames.friends.outgoing_friendships_limit_exceeded'
            if isinstance(e, fortnitepy.HTTPException) and e.message_code == m:
                self.debug_print_exception(e)
                text = self.l(
                    'error_max_outgoing_requests_exceeded',
                    self.name(user)
                )
                self.send(
                    text,
                    add_p=self.time,
                    file=sys.stderr
                )
                if message is not None:
                    await message.reply(text)
            else:
                self.print_exception(e)
                text = self.l(
                    'error_while_accepting_friend_request',
                    self.name(user)
                )
                self.send(
                    text,
                    add_p=self.time,
                    file=sys.stderr
                )
                if message is not None:
                    await message.reply(text)
            return e

    async def remove_friend(self, friend: fortnitepy.Friend,
                            message: Optional[MyMessage] = None) -> Optional[Exception]:
        try:
            await friend.remove()
        except Exception as e:
            self.print_exception(e)
            text = self.l(
                'error_while_removing_friend',
                self.name(friend)
            )
            self.send(
                text,
                add_p=self.time,
                file=sys.stderr
            )
            if message is not None:
                await message.reply(text)
            return e

    async def accept_request(self, request: fortnitepy.IncomingPendingFriend,
                             message: Optional[MyMessage] = None) -> Union[fortnitepy.Friend, Exception]:
        try:
            return await request.accept()
        except fortnitepy.DuplicateFriendship as e:
            self.debug_print_exception(e)
            text = self.l(
                'error_duplicate_friendship',
                self.name(request)
            )
            self.send(
                text,
                add_p=self.time,
                file=sys.stderr
            )
            if message is not None:
                await message.reply(text)
            return e
        except fortnitepy.FriendshipRequestAlreadySent as e:
            self.debug_print_exception(e)
            text = self.l(
                'error_friendship_request_already_sent',
                self.name(request)
            )
            self.send(
                text,
                add_p=self.time,
                file=sys.stderr
            )
            if message is not None:
                await message.reply(text)
            return e
        except fortnitepy.MaxFriendshipsExceeded as e:
            self.debug_print_exception(e)
            text = self.l(
                'error_max_friendships_exceeded_accept',
                self.name(request)
            )
            self.send(
                text,
                add_p=self.time,
                file=sys.stderr
            )
            if message is not None:
                await message.reply(text)
            return e
        except fortnitepy.InviteeMaxFriendshipsExceeded as e:
            self.debug_print_exception(e)
            text = self.l(
                'error_invitee_max_friendships_exceeded',
                self.name(request)
            )
            self.send(
                text,
                add_p=self.time,
                file=sys.stderr
            )
            if message is not None:
                await message.reply(text)
            return e
        except Exception as e:
            self.print_exception(e)
            text = self.l(
                'error_while_accepting_friend_request',
                self.name(request)
            )
            self.send(
                text,
                add_p=self.time,
                file=sys.stderr
            )
            if message is not None:
                await message.reply(text)
            return e

    async def decline_request(self, request: Union[fortnitepy.IncomingPendingFriend, fortnitepy.OutgoingPendingFriend],
                              message: Optional[MyMessage] = None) -> Optional[Union[fortnitepy.Friend, Exception]]:
        try:
            if isinstance(request, fortnitepy.IncomingPendingFriend):
                return await request.decline()
            else:
                return await request.cancel()
        except Exception as e:
            self.print_exception(e)
            text = self.l(
                'error_while_declining_fiend_request',
                self.name(request)
            )
            self.send(
                text,
                add_p=self.time,
                file=sys.stderr
            )
            if message is not None:
                await message.reply(text)
            return e

    async def join_party_friend(self, friend: fortnitepy.Friend,
                                message: Optional[MyMessage] = None) -> Union[fortnitepy.ClientParty, Exception]:
        presence = friend.last_presence
        party = None
        if presence is not None and presence.party is not None:
            party = presence.party
        try:
            return await friend.join_party()
        except fortnitepy.PartyError as e:
            self.debug_print_exception(e)
            if self.config['loglevel'] == 'normal' or party is None:
                text = self.l(
                    'already_member_of_this_party_friend',
                    self.name(friend)
                )
            else:
                text = self.l(
                    'already_member_of_this_party_friend_info',
                    self.name(friend),
                    party.id
                )
            self.send(
                text,
                add_p=self.time,
                file=sys.stderr
            )
            if message is not None:
                await message.reply(text)
            return e
        except fortnitepy.PartyIsFull as e:
            self.debug_print_exception(e)
            if self.config['loglevel'] == 'normal' or party is None:
                text = self.l(
                    'party_full_friend',
                    self.name(friend)
                )
            else:
                text = self.l(
                    'party_full_friend_info',
                    self.name(friend),
                    party.id
                )
            self.send(
                text,
                add_p=self.time,
                file=sys.stderr
            )
            if message is not None:
                await message.reply(text)
            return e
        except fortnitepy.NotFound as e:
            self.debug_print_exception(e)
            if self.config['loglevel'] == 'normal' or party is None:
                text = self.l(
                    'party_not_found_friend',
                    self.name(friend)
                )
            else:
                text = self.l(
                    'party_not_found_friend_info',
                    self.name(friend),
                    party.id
                )
            self.send(
                text,
                add_p=self.time,
                file=sys.stderr
            )
            if message is not None:
                await message.reply(text)
            return e
        except fortnitepy.Forbidden as e:
            self.debug_print_exception(e)
            if self.config['loglevel'] == 'normal' or party is None:
                text = self.l(
                    'not_allowed_to_join_this_party_friend',
                    self.name(friend)
                )
            else:
                text = self.l(
                    'not_allowed_to_join_this_party_friend_info',
                    self.name(friend),
                    party.id
                )
            self.send(
                text,
                add_p=self.time,
                file=sys.stderr
            )
            if message is not None:
                await message.reply(text)
            return e
        except Exception as e:
            self.print_exception(e)
            if self.config['loglevel'] == 'normal' or party is None:
                text = self.l(
                    'error_while_joining_party_friend',
                    self.name(friend)
                )
            else:
                text = self.l(
                    'error_while_joining_party_friend_info',
                    self.name(friend),
                    party.id
                )
            self.send(
                text,
                add_p=self.time,
                file=sys.stderr
            )
            if message is not None:
                await message.reply(text)
            return e

    async def join_party_id(self, party_id: str,
                            message: Optional[MyMessage] = None) -> fortnitepy.ClientParty:
        try:
            return await self.join_party(party_id=party_id)
        except fortnitepy.PartyError as e:
            self.debug_print_exception(e)
            if self.config['loglevel'] == 'normal':
                text = self.l('already_member_of_this_party')
            else:
                text = self.l(
                    'already_member_of_this_party_info',
                    party_id
                )
            self.send(
                text,
                add_p=self.time,
                file=sys.stderr
            )
            if message is not None:
                await message.reply(text)
            return e
        except fortnitepy.PartyIsFull as e:
            self.debug_print_exception(e)
            if self.config['loglevel'] == 'normal':
                text = self.l('party_full')
            else:
                text = self.l(
                    'party_full_info',
                    party_id
                )
            self.send(
                text,
                add_p=self.time,
                file=sys.stderr
            )
            if message is not None:
                await message.reply(text)
            return e
        except fortnitepy.NotFound as e:
            self.debug_print_exception(e)
            if self.config['loglevel'] == 'normal':
                text = self.l('party_not_found')
            else:
                text = self.l(
                    'party_not_found_info',
                    party_id
                )
            self.send(
                text,
                add_p=self.time,
                file=sys.stderr
            )
            if message is not None:
                await message.reply(text)
            return e
        except fortnitepy.Forbidden as e:
            self.debug_print_exception(e)
            if self.config['loglevel'] == 'normal':
                text = self.l('not_allowed_to_join_this_party')
            else:
                text = self.l(
                    'not_allowed_to_join_this_party_info',
                    party_id
                )
            self.send(
                text,
                add_p=self.time,
                file=sys.stderr
            )
            if message is not None:
                await message.reply(text)
            return e
        except Exception as e:
            self.print_exception(e)
            if self.config['loglevel'] == 'normal':
                text = self.l('error_while_joining_party')
            else:
                text = self.l(
                    'error_while_joining_party_info',
                    party_id
                )
            self.send(
                text,
                add_p=self.time,
                file=sys.stderr
            )
            if message is not None:
                await message.reply(text)
            return e

    async def send_join_request(self, friend: fortnitepy.Friend,
                                message: Optional[MyMessage] = None) -> Optional[Exception]:
        try:
            await friend.request_to_join()
        except fortnitepy.PartyError as e:
            self.debug_print_exception(e)
            if self.config['loglevel'] == 'normal':
                text = self.l(
                    'already_member_of_this_party_friend',
                    self.name(friend)
                )
            else:
                text = self.l(
                    'already_member_of_this_party_friend_info',
                    self.name(friend),
                    self.party.id
                )
            self.send(
                text,
                add_p=self.time,
                file=sys.stderr
            )
            if message is not None:
                await message.reply(text)
            return e
        except Exception as e:
            self.print_exception(e)
            if self.config['loglevel'] == 'normal':
                text = self.l(
                    'error_while_inviting_friend',
                    self.name(friend)
                )
            else:
                text = self.l(
                    'error_while_inviting_friend_info',
                    self.name(friend),
                    self.party.id
                )
            self.send(
                text,
                add_p=self.time,
                file=sys.stderr
            )
            if message is not None:
                await message.reply(text)
            return e

    async def invite_friend(self, friend: fortnitepy.Friend,
                            message: Optional[MyMessage] = None) -> fortnitepy.SentPartyInvitation:
        try:
            await friend.invite()
        except fortnitepy.PartyError as e:
            self.debug_print_exception(e)
            if self.party.get_member(friend.id) is not None:
                if self.config['loglevel'] == 'normal':
                    text = self.l(
                        'already_member_of_this_party_friend',
                        self.name(friend)
                    )
                else:
                    text = self.l(
                        'already_member_of_this_party_friend_info',
                        self.name(friend),
                        self.party.id
                    )
            else:
                if self.config['loglevel'] == 'normal':
                    text = self.l('party_full')
                else:
                    text = self.l(
                        'party_full_info',
                        self.party.id
                    )
            self.send(
                text,
                add_p=self.time,
                file=sys.stderr
            )
            if message is not None:
                await message.reply(text)
            return e
        except Exception as e:
            self.print_exception(e)
            if self.config['loglevel'] == 'normal':
                text = self.l(
                    'error_while_inviting_friend',
                    self.name(friend)
                )
            else:
                text = self.l(
                    'error_while_inviting_friend_info',
                    self.name(friend),
                    self.party.id
                )
            self.send(
                text,
                add_p=self.time,
                file=sys.stderr
            )
            if message is not None:
                await message.reply(text)
            return e

    async def user_block(self, user: Type[fortnitepy.user.UserBase],
                         message: Optional[MyMessage] = None) -> Optional[Exception]:
        try:
            await user.block()
        except Exception as e:
            self.print_exception(e)
            text = self.l(
                'error_while_blocking_user',
                self.name(user)
            )
            self.send(
                text,
                add_p=self.time,
                file=sys.stderr
            )
            if message is not None:
                await message.reply(text)
            return e

    async def user_unblock(self, blocked_user: fortnitepy.BlockedUser,
                           message: Optional[MyMessage] = None) -> Optional[Exception]:
        try:
            await blocked_user.unblock()
        except Exception as e:
            self.print_exception(e)
            text = self.l(
                'error_while_unblocking_user',
                self.name(blocked_user)
            )
            self.send(
                text,
                add_p=self.time,
                file=sys.stderr
            )
            if message is not None:
                await message.reply(text)
            return e

    async def promote_member(self, member: fortnitepy.PartyMember,
                             message: Optional[MyMessage] = None) -> Optional[Exception]:
        try:
            await member.promote()
        except fortnitepy.Forbidden as e:
            self.debug_print_exception(e)
            text = self.l('not_a_party_leader')
            self.send(
                text,
                add_p=self.time,
                file=sys.stderr
            )
            if message is not None:
                await message.reply(text)
            return e
        except fortnitepy.PartyError as e:
            self.debug_print_exception(e)
            text = self.l('already_party_leader')
            self.send(
                text,
                add_p=self.time,
                file=sys.stderr
            )
            if message is not None:
                await message.reply(text)
            return e
        except Exception as e:
            self.print_exception(e)
            text = self.l(
                'error_while_promoting_leader',
                self.name(member)
            )
            self.send(
                text,
                add_p=self.time,
                file=sys.stderr
            )
            if message is not None:
                await message.reply(text)
            return e

    async def kick_member(self, member: fortnitepy.PartyMember,
                          message: Optional[MyMessage] = None) -> Optional[Exception]:
        try:
            await member.kick()
        except fortnitepy.Forbidden as e:
            self.debug_print_exception(e)
            text = self.l('not_a_party_leader')
            self.send(
                text,
                add_p=self.time,
                file=sys.stderr
            )
            if message is not None:
                await message.reply(text)
            return e
        except fortnitepy.PartyError as e:
            self.debug_print_exception(e)
            text = self.l('cant_kick_myself')
            self.send(
                text,
                add_p=self.time,
                file=sys.stderr
            )
            if message is not None:
                await message.reply(text)
            return e
        except Exception as e:
            self.print_exception(e)
            text = self.l(
                'error_while_kicking_member',
                self.name(member)
            )
            self.send(
                text,
                add_p=self.time,
                file=sys.stderr
            )
            if message is not None:
                await message.reply(text)
            return e

    async def chatban_member(self, member: fortnitepy.PartyMember,
                             reason: Optional[str] = None,
                             message: Optional[MyMessage] = None) -> Optional[Exception]:
        try:
            await member.chatban()
        except fortnitepy.Forbidden as e:
            self.debug_print_exception(e)
            text = self.l('not_a_party_leader')
            self.send(
                text,
                add_p=self.time,
                file=sys.stderr
            )
            if message is not None:
                await message.reply(text)
            return e
        except fortnitepy.PartyError as e:
            self.debug_print_exception(e)
            text = self.l('cant_chatban_myself')
            self.send(
                text,
                add_p=self.time,
                file=sys.stderr
            )
            if message is not None:
                await message.reply(text)
            return e
        except fortnitepy.NotFound as e:
            self.debug_print_exception(e)
            text = self.l(
                'not_found',
                self.l('party_member'),
                self.name(member)
            )
            self.send(
                text,
                add_p=self.time,
                file=sys.stderr
            )
            if message is not None:
                await message.reply(text)
            return e
        except ValueError as e:
            self.debug_print_exception(e)
            text = self.l(
                'already_chatbanned',
                self.name(member)
            )
            self.send(
                text,
                add_p=self.time,
                file=sys.stderr
            )
            if message is not None:
                await message.reply(text)
            return e
        except Exception as e:
            self.print_exception(e)
            text = self.l(
                'error_while_kicking_member',
                self.name(member)
            )
            self.send(
                text,
                add_p=self.time,
                file=sys.stderr
            )
            if message is not None:
                await message.reply(text)
            return e

    async def hide_member(self, member: fortnitepy.PartyMember,
                          message: Optional[str] = None) -> Optional[Exception]:
        try:
            await self.party.hide(member)
        except Exception as e:
            self.print_exception(e)
            text = self.l(
                'error_while_hiding_member',
                self.name(member)
            )
            self.send(
                text,
                add_p=self.time,
                file=sys.stderr
            )
            if message is not None:
                await message.reply(text)
            return e

    async def show_member(self, member: fortnitepy.PartyMember,
                          message: Optional[str] = None) -> Optional[Exception]:
        try:
            await self.party.show(member)
        except Exception as e:
            self.print_exception(e)
            text = self.l(
                'error_while_showing_member',
                self.name(member)
            )
            self.send(
                text,
                add_p=self.time,
                file=sys.stderr
            )
            if message is not None:
                await message.reply(text)
            return e

    async def swap_member(self, member: fortnitepy.PartyMember,
                          message: Optional[str] = None) -> Optional[Exception]:
        try:
            await member.swap_position()
        except Exception as e:
            self.print_exception(e)
            text = self.l(
                'error_while_swapping_member',
                self.name(member)
            )
            self.send(
                text,
                add_p=self.time,
                file=sys.stderr
            )
            if message is not None:
                await message.reply(text)
            return e


    # Config controls
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

    def is_blacklist(self, user_id: str) -> bool:
        return self._blacklist.get(user_id) is not None

    @property
    def botlist(self) -> list:
        return self.bot.loaded_client_ids + list(self._botlist.values())

    def is_bot(self, user_id: str) -> bool:
        if user_id in self.bot.loaded_client_ids:
            return True
        if self._botlist.get(user_id) is not None:
            return True
        return False

    @property
    def invitelist(self) -> list:
        return list(self._invitelist.values())

    def is_invitelist(self, user_id: str) -> bool:
        return self._invitelist.get(user_id) is not None

    def get_user_type(self, user_id: Optional[str]) -> str:
        if self.is_owner(user_id):
            return 'owner'
        elif self.is_whitelist(user_id):
            return 'whitelist'
        elif self.is_blacklist(user_id):
            return 'blacklist'
        elif self.is_bot(user_id):
            return 'bot'
        elif user_id is None or len(user_id) == auth.id_len:
            return 'owner'
        return 'user'

    def is_for(self, config_key: str, user_type: str, fortnite: Optional[bool] = True) -> bool:
        if fortnite:
            config = self.config['fortnite'][config_key]
        else:
            config = self.config[config_key]
        if config is None:
            return False
        return user_type in config

    def is_outfit_mimic_for(self, user_type: str) -> bool:
        return self.is_for('outfit_mimic_for', user_type)

    def is_outfit_lock_for(self, user_type: str) -> bool:
        return self.is_for('outfit_lock_for', user_type)

    def is_backpack_mimic_for(self, user_type: str) -> bool:
        return self.is_for('backpack_mimic_for', user_type)

    def is_backpack_lock_for(self, user_type: str) -> bool:
        return self.is_for('backpack_lock_for', user_type)

    def is_pickaxe_mimic_for(self, user_type: str) -> bool:
        return self.is_for('pickaxe_mimic_for', user_type)

    def is_pickaxe_lock_for(self, user_type: str) -> bool:
        return self.is_for('pickaxe_lock_for', user_type)

    def is_emote_mimic_for(self, user_type: str) -> bool:
        return self.is_for('emote_mimic_for', user_type)

    def is_emote_lock_for(self, user_type: str) -> bool:
        return self.is_for('emote_lock_for', user_type)

    def is_ng_platform_for(self, user_type: str) -> bool:
        return self.is_for('ng_platform_for', user_type)

    def is_ng_name_for(self, user_type: str) -> bool:
        return self.is_for('ng_name_for', user_type)

    def is_accept_invite_for(self, user_type: str) -> bool:
        return self.is_for('accept_invite_for', user_type)

    def is_decline_invite_when(self, user_type: str) -> bool:
        return self.is_for('decline_invite_when', user_type)

    def is_invite_interval_for(self, user_type: str) -> bool:
        return self.is_for('invite_interval_for', user_type)

    def is_accept_friend_for(self, user_type: str) -> bool:
        return self.is_for('accept_friend_for', user_type)

    def is_whisper_enable_for(self, user_type: str) -> bool:
        return self.is_for('whisper_enable_for', user_type)

    def is_party_chat_enable_for(self, user_type: str) -> bool:
        return self.is_for('party_chat_enable_for', user_type)

    def is_accept_join_for(self, user_type: str) -> bool:
        return self.is_for('accept_join_for', user_type)

    def is_chat_max_for(self, user_type: str) -> bool:
        return self.is_for('chat_max_for', user_type)

    def is_hide_for(self, user_type: str) -> bool:
        return self.is_for('hide_for', user_type)

    def is_ng_word_for(self, user_type: str) -> bool:
        return self.is_for('ng_word_for', user_type, fortnite=False)

    async def get_user_operation_func(self, config_key: str, user_id: str, fortnite: Optional[bool] = True) -> List[Callable]:
        if fortnite:
            config = self.config['fortnite'][config_key]
        else:
            config = self.config[config_key]

        user = await self.fetch_user(user_id, cache=True)
        if user is None:
            return []

        is_leader = getattr(getattr(getattr(self, 'party', None), 'me', None), 'leader', False)

        functions = []
        if config:
            for operation in config:
                if operation == 'kick':
                    if getattr(self, 'party', None) is None or not is_leader:
                        continue
                    member = self.party.get_member(user.id)
                    if member is None:
                        continue
                    functions.append(member.kick)
                elif operation == 'chatban':
                    if getattr(self, 'party', None) is None or not is_leader:
                        continue
                    member = self.party.get_member(user.id)
                    if member is None:
                        continue
                    functions.append(member.chatban)
                elif operation == 'remove':
                    friend = self.get_friend(user.id)
                    if friend is None:
                        continue
                    functions.append(friend.remove)
                elif operation == 'block':
                    if user is None:
                        continue
                    functions.append(user.block)
                elif operation == 'blacklist':
                    functions.append(partial(self.add_to_blacklist, user=user))

        return functions

    def get_ng_platform_operation(self, user_id: str) -> Awaitable:
        return self.get_user_operation_func('ng_platform_operation', user_id)

    def get_ng_name_operation(self, user_id: str) -> Awaitable:
        return self.get_user_operation_func('ng_name_operation', user_id)

    def get_permission_command_operation(self, user_id: str) -> Awaitable:
        return self.get_user_operation_func('permission_command_operation', user_id)

    def get_chat_max_operation(self, user_id: str) -> Awaitable:
        return self.get_user_operation_func('chat_max_operation', user_id)

    def get_blacklist_operation(self, user_id: str) -> Awaitable:
        return self.get_user_operation_func('blacklist_operation', user_id)

    def get_botlist_operation(self, user_id: str) -> Awaitable:
        return self.get_user_operation_func('botlist_operation', user_id)

    def get_ng_word_operation(self, user_id: str) -> Awaitable:
        return self.get_user_operation_func('ng_word_operation', user_id, fortnite=False)

    def get_user_str(self, user: Type[fortnitepy.user.UserBase]) -> str:
        return ('<User id={0.id!r} display_name={0.display_name!r} '
                'external_auths={1!r}>'.format(
                    user,
                    [self.get_external_auth_str(auth)
                        for auth in user.external_auths]
                ))

    def get_external_auth_str(self, external_auth: fortnitepy.ExternalAuth) -> str:
        return ('<ExternalAuth external_id={0.external_id!r} '
                'external_display_name={0.external_display_name!r} '
                'type={0.type!r}>'.format(external_auth))

    def get_config_user_id(self, text: str) -> Optional[str]:
        if text is None:
            return None
        match = self.config_user_pattern.match(text)
        if match is None:
            return None
        return match.group('id')

    def add_to_blacklist(self, user: fortnitepy.User) -> None:
        if user.id not in self._blacklist:
            self.config['fortnite']['blacklist'].append(self.get_user_str(user))
            self._blacklist[user.id] = user

    def get_config_item_path(self, text: str) -> str:
        return self.bot.get_config_item_path(text)

    def get_config_playlist_id(self, text: str) -> str:
        return self.bot.get_config_playlist_id(text)

    def get_config_variant(self, text: str) -> str:
        return self.bot.get_config_variant(text)

    # Basic functions
    @property
    def party_id(self) -> Optional[str]:
        return getattr(getattr(self, 'party', None), 'id', None)

    @property
    def variables(self) -> dict:
        user = getattr(self, 'user', None)
        party = getattr(self, 'party', None)
        uptime = (datetime.datetime.now() - self.booted_at) if self.booted_at is not None else None
        if uptime is not None:
            d, h, m, s = self.bot.convert_td(uptime)
        else:
            d = h = m = s = None
        online_friends = [f for f in self.friends if f.is_online()]
        offline_friends = [f for f in self.friends if not f.is_online()]
        return {
            **globals(),
            'self': self,
            'client': self,
            'discord_bot': self.discord_client,
            'party': party,
            'party_id': getattr(party, 'id', None),
            'party_size': getattr(party, 'member_count', None),
            'party_max_size': getattr(party, 'config', {}).get('max_size'),
            'friends': self.friends,
            'friend_count': len(self.friends),
            'online_friend_count': len(online_friends),
            'online_friends': online_friends,
            'offline_friends': offline_friends,
            'offline_friend_count': len(offline_friends),
            'pending_friends': self.pending_friends,
            'pending_count': len(self.pending_friends),
            'incoming_pending_friends': self.incoming_pending_friends,
            'incoming_pending_count': len(self.incoming_pending_friends),
            'outgoing_pending_friends': self.outgoing_pending_friends,
            'outgoing_pending_count': len(self.outgoing_pending_friends),
            'blocked_users': self.blocked_users,
            'block_count': len(self.blocked_users),
            'display_name': getattr(user, 'display_name', None),
            'account_id': getattr(user, 'id', None),
            'uptime': uptime,
            'uptime_days': d,
            'uptime_hours': h,
            'uptime_minutes': m,
            'uptime_seconds': s,
            'owner': self.owner,
            'whitelist': self.whitelist,
            'blacklist': self.blacklist,
            'botlist': self.botlist,
            'invitelist': self.invitelist
        }

    @property
    def variables_without_self(self) -> dict:
        var = self.variables
        var.pop('self')
        return var

    def convert_td(self, td: datetime.timedelta) -> Tuple[int, int, int, int]:
        return self.bot.convert_td(td)

    def eval_format(self, text: str, variables: dict) -> str:
        return self.bot.eval_format(text, variables)

    def get_list_index(self, data: list, index: int, default: Optional[str] = None) -> Any:
        return self.bot.get_list_index(data, index, default)

    def get_dict_key(self, data: dict, keys: list,
                     func: Optional[Callable] = None) -> Any:
        return self.bot.get_dict_key(data, keys, func)

    def get_dict_key_default(self, data: dict, keys: list, default: Any,
                             func: Optional[Callable] = None) -> Any:
        return self.bot.get_dict_key_default(data, keys, default, func)

    def cleanup_channel_name(self, text: str) -> str:
        return self.bot.cleanup_channel_name(text)

    def l(self, key: str, *args: tuple, default: Optional[str] = '', **kwargs: dict) -> LocalizedText:
        return LocalizedText(self.bot, ['client', key], default, *args, **kwargs)

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
        if not self.config['no_logs']:
            text = content
            for func in add_p:
                text = func(text)
            print(color(text), file=file)

        if self.webhook:
            content = discord.utils.escape_markdown(content)
            name = user_name or self.user.display_name
            text = content
            for func in add_d:
                text = func(text)
            self.webhook.send(text, name)

    def now(self) -> str:
        return self.bot.now()

    def time(self, text: str) -> str:
        return f'[{self.now()}] [{self.user.display_name}] {text}'

    def time_party(self, text: str, name: Optional[str] = None) -> str:
        name = name or self.user.display_name
        if getattr(self, 'party', None) is None:
            return self.time(text)
        else:
            if self.config['loglevel'] == 'normal':
                return (f'[{self.now()}] [{self.l("party")}] '
                        f'[{name}] {text}')
            else:
                return (f'[{self.now()}] [{self.l("party")}/{self.party.id}] '
                        f'[{name}] {text}')

    def discord_party(self, text: str, name: Optional[str] = None) -> str:
        name = name or self.user.display_name
        if getattr(self, 'party', None) is None:
            return self.time(text)
        else:
            if self.config['loglevel'] == 'normal':
                return (f'[{self.l("party")}] '
                        f'[{name}] {text}')
            else:
                return (f'[{self.l("party")}/{self.party.id}] '
                        f'[{name}] {text}')

    def discord_error(self, text: str) -> str:
        return self.bot.discord_error(text)

    def debug_message(self, text: str) -> str:
        return self.bot.debug_message(text)

    def name(self, user: Optional[fortnitepy.User] = None, *, force_info: Optional[bool] = False) -> str:
        user = user or self.user
        if self.config['loglevel'] == 'normal' and not force_info:
            return user.display_name
        else:
            append = ''
            if getattr(user, 'platform', None) is not None:
                if getattr(user, 'input', None) is not None:
                    append += f' [{self.platform_to_str(user.platform)}/{user.input}]'
                else:
                    append += f' [{self.platform_to_str(user.platform)}]'
            elif getattr(user, 'input', None) is not None:
                append += f' [{user.input}]'
            if getattr(user, 'nickname', None) is None:
                return '{0.display_name} / {0.id}{1}'.format(user, append)
            else:
                return '{0.nickname}({0.display_name}) / {0.id}{1}'.format(user, append)

    def name_cosmetic(self, item: dict) -> str:
        if self.config['loglevel'] == 'normal':
            return item['name']
        else:
            return f'{item["name"]} | {item["id"]}'

    def format_exception(self, exc: Optional[Exception] = None) -> str:
        return self.bot.print_exception(exc)

    def print_exception(self, exc: Optional[Exception] = None) -> None:
        return self.bot.print_exception(exc)

    def debug_print_exception(self, exc: Optional[Exception] = None) -> None:
        return self.bot.debug_print_exception(exc)

    def section(self, member: Optional[fortnitepy.PartyMember] = None) -> int:
        member = member or self.party.me
        base = member.meta.get_prop('Default:FrontendEmote_j')
        return base['FrontendEmote']['emoteSection']

    def asset(self, item: str,
              member: Optional[fortnitepy.PartyMember] = None) -> Optional[str]:
        member = member or self.party.me
        p = self.ASSET_CONVERTER.get(item)
        if p is None or member is None:
            return None
        return p.fget(member)

    def variants(self, item: str,
                 member: Optional[fortnitepy.PartyMember] = None) -> list:
        member = member or self.party.me
        p = self.VARIANTS_CONVERTER.get(item)
        if p is None or member is None:
            return []
        return p.fget(member)

    def platform_to_str(self, platform: fortnitepy.Platform) -> str:
        return self.PLATFORM_CONVERTER.get(platform)

    def find_users(self, user: str, *,
                   mode: FindUserMode,
                   method: FindUserMatchMethod,
                   users: List[fortnitepy.User] = None,
                   me: Optional[fortnitepy.User] = None,
                   ) -> List[fortnitepy.User]:
        if me is not None and user in self.commands['me']:
            return [me]

        if mode is FindUserMode.NAME_ID:
            name_users = self.find_users(
                user,
                users=users,
                mode=FindUserMode.DISPLAY_NAME,
                method=method
            )
            id_users = self.find_users(
                user,
                users=users,
                mode=FindUserMode.ID,
                method=method
            )
            name_users += [u for u in id_users if u not in name_users]
            return name_users
        if self.config['case_insensitive']:
            user = jaconv.kata2hira(user.casefold())
        if self.config['convert_kanji']:
            user = self.bot.converter.do(user)

        if users is None:
            users = self._caches.values()
        _users = []
        for u in users:
            if self.get_as_user(u) in _users:
                continue
            user_name = u.display_name
            if self.config['case_insensitive']:
                user_name = jaconv.kata2hira(user_name.casefold())
            if self.config['convert_kanji']:
                user_name = self.bot.converter.do(user_name)

            if method is FindUserMatchMethod.FULL:
                if mode is FindUserMode.DISPLAY_NAME:
                    if u.display_name == user:
                        _users.append(self.get_as_user(u))
                elif mode is FindUserMode.ID:
                    if u.id == user:
                        _users.append(self.get_as_user(u))

            elif method is FindUserMatchMethod.CONTAINS:
                if mode is FindUserMode.DISPLAY_NAME:
                    if user in user_name:
                        _users.append(self.get_as_user(u))
                elif mode is FindUserMode.ID:
                    if user in u.id:
                        _users.append(self.get_as_user(u))

            elif method is FindUserMatchMethod.STARTS:
                if mode is FindUserMode.DISPLAY_NAME:
                    if user_name.startswith(user):
                        _users.append(self.get_as_user(u))
                elif mode is FindUserMode.ID:
                    if u.id.startswith(user):
                        _users.append(self.get_as_user(u))

            elif method is FindUserMatchMethod.ENDS:
                if mode is FindUserMode.DISPLAY_NAME:
                    if user_name.endswith(user):
                        _users.append(self.get_as_user(u))
                elif mode is FindUserMode.ID:
                    if u.id.endswith(user):
                        _users.append(self.get_as_user(u))
        return _users

    async def aexec(self, body: str, variables: dict) -> Optional[bool]:
        flag = False
        for line in body.split('\n'):
            match = self.return_pattern.fullmatch(line)
            if match is not None:
                flag = True
                break
        try:
            _, o, _ = await self.bot.aexec(body, variables)
            print(o)
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
                              for stack in reversed(inspect.stack()[1:])])
                 + f'{e.__class__.__name__}: {e}'),
                file=sys.stderr
            )
            return None
        return True

    async def exec_event(self, event: str, variables: dict) -> None:
        if self.config['fortnite']['exec'][event]:
            ret = await self.aexec(
                '\n'.join(self.config['fortnite']['exec'][event]),
                variables
            )
            if ret is None:
                for line in self.config['fortnite']['exec'][event]:
                    try:
                        await self.bot.aexec(line, variables)
                    except Exception as e:
                        mes = DummyMessage(self, None, content=line, author=DummyUser())
                        await self.process_command(MyMessage(self, mes), None)
                        if self.config['loglevel'] == 'debug':
                            self.send(
                                mes.result,
                                color=yellow
                            )
            else:
                return ret

    async def update_owner(self) -> None:
        self._owner = {}
        if self.config['fortnite']['owner'] is None:
            return
        owners = [(self.get_config_user_id(owner)
                   or owner)
                  for owner in self.config['fortnite']['owner']]
        users = await self.fetch_multiple_users(owners)
        for num, owner in enumerate(owners):
            user = users.get(owner)
            if user is None:
                user = await self.fetch_user(owner, cache=True)
            if user is None:
                self.send(
                    self.l(
                        'owner_not_found',
                        owner
                    ),
                    add_p=self.time
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
                self.config['fortnite']['owner'][num] = self.get_user_str(user)
                if not self.has_friend(user.id) and self.is_accept_friend_for(user.id):
                    pending = self.get_incoming_pending_friend(user.id)
                    if pending is not None:
                        await self.accept_request(pending)
                    elif not self.is_outgoing_pending(user.id):
                        await self.send_friend_request(user)

    async def _update_user_list(self, lists: list, data_list: list) -> None:
        users = await self.fetch_multiple_users(sum(lists, []))
        for (keys, add_friend), list_users in zip(data_list, lists):
            attr = keys[-1]
            setattr(self, f'_{attr}', {})
            for num, list_user in enumerate(list_users):
                user = users.get(list_user)
                if user is None:
                    user = await self.fetch_user(list_user, cache=True)
                if user is None:
                    self.send(
                        self.l(
                            'list_user_not_found',
                            self.l(attr),
                            list_user
                        ),
                        add_p=self.time,
                        file=sys.stderr
                    )
                else:
                    text = self.bot.eval_dict(self.config, keys)
                    exec(f'self.config{text}[{num}] = self.get_user_str(user)')

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
                    if add_friend:
                        if not self.has_friend(user.id) and self.is_accept_friend_for(user.id):
                            pending = self.get_incoming_pending_friend(user.id)
                            if pending is not None:
                                await self.accept_request(pending)
                            elif not self.is_outgoing_pending(user.id):
                                await self.send_friend_request(user)
                        friend = self.get_friend(user.id)
                        if friend is not None:
                            getattr(self, f'_{attr}')[user.id] = friend

    async def update_user_lists(self) -> None:
        data_list = [
            (['fortnite', 'whitelist'], False),
            (['fortnite', 'blacklist'], False),
            (['fortnite', 'invitelist'], True),
            (['fortnite', 'botlist'], False)
        ]
        lists = [self.bot.get_dict_key(self.config, keys)
                 for keys, _ in data_list
                 if self.bot.get_dict_key(self.config, keys) is not None]
        lists = [[(self.get_config_user_id(user)
                   or user)
                  for user in list_users]
                 for list_users in lists]
        await self._update_user_list(
            lists,
            data_list
        )

    async def _update_multiple_select_list(self, lists: list, keys_list: list) -> None:
        users = await self.fetch_multiple_users(sum(lists, []))
        for keys, list_users in zip(keys_list, lists):
            attr = keys[-1]
            setattr(self, f'_{attr}', {})
            for num, list_user in enumerate(list_users):
                if list_user in ['user', 'whitelist',
                                 'blacklist', 'owner', 'bot']:
                    getattr(self, f'_{attr}')[list_user] = list_user
                    continue
                user = users.get(list_user)
                if user is None:
                    user = await self.fetch_user(list_user, cache=True)
                if user is not None:
                    text = self.bot.eval_dict(self.config, keys)
                    exec(f'self.config{text}[{num}] = self.get_user_str(user)')
                    getattr(self, f'_{attr}')[user.id] = user
                    self.send(
                        self.l(
                            'multiple_select_user_log',
                            attr,
                            self.name(user)
                        ),
                        color=green,
                        add_p=self.time
                    )
                else:
                    self.send(
                        self.l(
                            'multiple_select_user_not_found',
                            attr,
                            list_user
                        ),
                        add_p=self.time,
                        file=sys.stderr
                    )

    async def update_multiple_select_lists(self) -> None:
        keys_list = [
            ['fortnite', 'outfit_mimic_for'],
            ['fortnite', 'outfit_lock_for'],
            ['fortnite', 'backpack_mimic_for'],
            ['fortnite', 'backpack_lock_for'],
            ['fortnite', 'pickaxe_mimic_for'],
            ['fortnite', 'pickaxe_lock_for'],
            ['fortnite', 'emote_mimic_for'],
            ['fortnite', 'emote_lock_for'],
            ['fortnite', 'accept_invite_for'],
            ['fortnite', 'decline_invite_when'],
            ['fortnite', 'whisper_enable_for'],
            ['fortnite', 'party_chat_enable_for'],
            ['fortnite', 'hide_for'],
            ['ng_word_for']
        ]
        lists = [self.bot.get_dict_key(self.config, keys)
                 for keys in keys_list
                 if self.bot.get_dict_key(self.config, keys) is not None]
        lists = [[(self.get_config_user_id(user)
                   or user)
                  for user in list_users]
                 for list_users in lists]
        await self._update_multiple_select_list(
            lists,
            keys_list
        )

    async def ng_check(self, member: fortnitepy.PartyMember) -> None:
        if member.id == self.user.id:
            return

        # Name
        if self.is_ng_name_for(self.get_user_type(member.id)):
            for ng in self.config['fortnite']['ng_names']:
                flag = False
                if ng['matchmethod'] == 'full' and member.display_name == ng['word']:
                    flag = True
                elif ng['matchmethod'] == 'contains' and ng['word'] in member.display_name:
                    flag = True
                elif ng['matchmethod'] == 'starts' and member.display_name.startswith(ng['word']):
                    flag = True
                elif ng['matchmethod'] == 'ends' and member.display_name.endswith(ng['word']):
                    flag = True

                if flag:
                    functions = await self.get_ng_name_operation(user_id=member.id)
                    for func in functions:
                        try:
                            if asyncio.iscoroutinefunction(func):
                                await func()
                            else:
                                func()
                        except Exception as e:
                            self.print_exception(e)

                    if self.config['fortnite']['ng_name_reply']:
                        var = self.variables
                        var.update({
                            'member': member,
                            'member_display_name': member.display_name,
                            'member_id': member.id
                        })
                        text = self.eval_format(
                            self.config['fortnite']['ng_name_reply'],
                            var
                        )
                        if self.party.get_member(member.id) is not None:
                            await self.party.send(text)
                        else:
                            friend = self.get_friend(member.id)
                            if friend is not None:
                                await friend.send(text)

        # Platform
        if (self.is_ng_platform_for(self.get_user_type(member.id))
                and self.config['fortnite']['ng_platforms'] is not None
                and member.platform in self.config['fortnite']['ng_platforms']):
            functions = await self.get_ng_platform_operation(user_id=member.id)
            for func in functions:
                try:
                    if asyncio.iscoroutinefunction(func):
                        await func()
                    else:
                        func()
                except Exception as e:
                    self.print_exception(e)

            if self.config['fortnite']['ng_platform_reply']:
                var = self.variables
                var.update({
                    'member': member,
                    'member_display_name': member.display_name,
                    'member_id': member.id
                })
                text = self.eval_format(
                    self.config['fortnite']['ng_platform_reply'],
                    var
                )
                if self.party.get_member(member.id) is not None:
                    await self.party.send(text)
                else:
                    friend = self.get_friend(member.id)
                    if friend is not None:
                        await friend.send(text)

        # Cosmetics
        items = [
            'AthenaCharacter',
            'AthenaBackpack',
            'AthenaPickaxe',
            'AthenaDance'
        ]
        for item in items:
            conf = self.bot.convert_backend_type(item)
            if not self.config['fortnite'][f'ng_{conf}s'] or self.asset(item, member) is None:
                continue
            ngs = [ng.lower() for ng in [
                (self.bot.get_config_item_path(cosmetic)
                 or cosmetic)
                for cosmetic in self.config['fortnite'][f'ng_{conf}s']
            ] if ng is not None]
            if (self.is_for(f'ng_{conf}_for', self.get_user_type(member.id))
                    and self.asset(item, member).lower() in ngs):
                functions = await self.get_user_operation_func(f'ng_{conf}_operation', user_id=member.id)
                for func in functions:
                    try:
                        if asyncio.iscoroutinefunction(func):
                            await func()
                        else:
                            func()
                    except Exception as e:
                        self.print_exception(e)

                if self.config['fortnite'][f'ng_{conf}_reply']:
                    var = self.variables
                    var.update({
                        'member': member,
                        'member_display_name': member.display_name,
                        'member_id': member.id
                    })
                    text = self.eval_format(
                        self.config['fortnite'][f'ng_{conf}_reply'],
                        var
                    )
                    if self.party.get_member(member.id) is not None:
                        await self.party.send(text)
                    else:
                        friend = self.get_friend(member.id)
                        if friend is not None:
                            await friend.send(text)

    async def ng_word_check(self, message: Union[fortnitepy.FriendMessage, fortnitepy.PartyMessage]) -> bool:
        if message.author.id == self.user.id:
            return True
        if not self.is_ng_word_for(self.get_user_type(message.author.id)):
            return True

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
                if self.user.id not in self.bot.command_stats:
                    self.bot.command_stats[self.user.id] = {'commands': {}, 'ngs': {}}
                stats = self.bot.command_stats[self.user.id]
                if message.author.id not in stats['ngs']:
                    stats['ngs'][message.author.id] = {}
                if match not in stats['ngs'][message.author.id]:
                    stats['ngs'][message.author.id][match] = 0
                stats['ngs'][message.author.id][match] += 1

                if stats['ngs'][message.author.id][match] >= ng['count']:
                    functions = await self.get_ng_word_operation(user_id=message.author.id)
                    for func in functions:
                        try:
                            if asyncio.iscoroutinefunction(func):
                                await func()
                            else:
                                func()
                        except Exception as e:
                            self.print_exception(e)

                    if self.config['ng_word_reply']:
                        var = self.variables
                        var.update({
                            'message': message,
                            'author': message.author,
                            'author_display_name': message.author.display_name,
                            'author_id': message.author.id
                        })
                        text = self.eval_format(
                            self.config['ng_word_reply'],
                            var
                        )
                        if (self.party.get_member(message.author.id) is not None
                                and isinstance(message, fortnitepy.PartyMessage)):
                            await self.party.send(text)
                        else:
                            friend = self.get_friend(message.author.id)
                            if friend is not None:
                                await friend.send(text)
                return False
        return True

    async def init_party(self) -> None:
        for member in self.party.members:
            if member.id == self.user.id:
                continue

            if self.party_hides.get(self.party.id) is None:
                self.party_hides[self.party.id] = []
            for m in self.party.members:
                if self.party.me.leader and self.is_hide_for(self.get_user_type(m.id)):
                    self.party_hides[self.party.id].append(m.id)
            self.party.update_hide_users(self.party_hides[self.party.id])

            await self.ng_check(member)

            if self.is_blacklist(member.id):
                functions = await self.get_blacklist_operation(user_id=member.id)
                for func in functions:
                    try:
                        if asyncio.iscoroutinefunction(func):
                            await func()
                        else:
                            func()
                    except Exception as e:
                        self.print_exception(e)
            if self.party.get_member(member.id) is None:
                continue

            if self.is_bot(member.id):
                functions = await self.get_botlist_operation(user_id=member.id)
                for func in functions:
                    try:
                        if asyncio.iscoroutinefunction(func):
                            await func()
                        else:
                            func()
                    except Exception as e:
                        self.print_exception(e)

        await self.party.refresh_squad_assignments()

        if (self.party.playlist_info[0].lower().strip()
                != self.config['fortnite']['party']['playlist'].lower().strip()
                and self.config['fortnite']['party']['playlist']):
            await self.party.set_playlist(
                self.bot.get_config_playlist_id(self.config['fortnite']['party']['playlist'])
            )
        if self.party.config['privacy'] != self.config['fortnite']['party']['privacy'].value:
            await self.party.set_privacy(self.config['fortnite']['party']['privacy'])
        if not self.party.voice_chat_enabled and self.config['fortnite']['party']['disable_voice_chat']:
            await self.party.disable_voice_chat()

    def is_valid_party(self, party_or_member: Union[fortnitepy.party.PartyBase, fortnitepy.PartyMember]) -> bool:
        if (self.party_id != (
                party_or_member.id
                if isinstance(party_or_member, fortnitepy.party.PartyBase) else
                party_or_member.party.id)):
            return False
        return True

    def is_most(self) -> str:
        name = self.user.display_name
        member_most = self.party.me
        for member in self.party.members:
            if member.id in self.bot.loaded_client_ids:
                if member.id != self.user.id:
                    name += f"/{member.display_name}"
                if member.joined_at < member_most.joined_at:
                    member_most = member
        if member_most.id == self.user.id:
            return name
        return None

    def invite_interval_callback(self) -> None:
        self.send(
            self.l('invite_interval')
        )
        self.invite_interval = False
        self.invite_interval_handle = None

    async def rebooter(self) -> None:
        await asyncio.sleep(self.config['relogin_in'])
        await self.restart()

    async def ready_init(self) -> bool:
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
        try:
            await self.update_multiple_select_lists()
        except Exception as e:
            self.send(
                (f'{self.format_exception(e)}\n{e}\n'
                 + self.l(
                     'error_while_updating_list'
                 )),
                file=sys.stderr
            )
        self.bot.save_json('config', self.bot.config)

        for pending in self.incoming_pending_friends:
            if self.is_accept_friend_for(self.get_user_type(pending.id)):
                await self.accept_request(pending)
        return True

    async def status_loop(self) -> None:
        while True:
            if self.party is not None:
                await self.send_presence(self.party.construct_presence())
            await asyncio.sleep(30)

    async def generate_device_auth(self) -> None:
        data = await self.auth.generate_device_auth()
        details = {
            'device_id': data['deviceId'],
            'account_id': data['accountId'],
            'secret': data['secret'],
        }
        self.bot.store_device_auth_details(self.email, details)

    # Events
    async def event_ready(self) -> None:
        if self.bot.use_device_auth and not isinstance(self.auth, (fortnitepy.AdvancedAuth, fortnitepy.DeviceAuth)):
            self.loop.create_task(self.generate_device_auth())

        self._is_booting = False
        self.booted_at = datetime.datetime.now()
        if self.config['relogin_in']:
            self.loop.create_task(self.rebooter())
        self.loop.create_task(self.status_loop())

        try:
            await self.send_presence(self.party.last_raw_status)
        except Exception as e:
            self.debug_print_exception(e)

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

        await self.ready_init()

    async def event_before_close(self) -> None:
        self._is_booting = False
        self.booted_at = None
        if getattr(self, 'user', None) is None:
            self.send(
                self.l(
                    'close',
                    self.email
                ),
                color=green,
                add_p=self.time
            )
        else:
            self.send(
                self.l(
                    'close',
                    self.name()
                ),
                color=green,
                add_p=self.time
            )

    async def event_restart(self) -> None:
        self.send(
            self.l(
                'restart',
                self.name()
            ),
            color=green,
            add_p=self.time
        )

    async def event_refresh_token_generate(self, details: dict) -> None:
        self.bot.store_refresh_token(self.email, details['refresh_token'])

    async def event_party_join_request(self, request: fortnitepy.PartyJoinRequest) -> None:
        if not self.is_ready():
            await self.wait_until_ready()

        self.join_requests[request.friend.id] = request

        def remove():
            if request.friend.id in self.join_requests:
                self.join_requests.pop(request.friend.id)

        self.loop.call_later((request.expires_at - datetime.datetime.utcnow()).total_seconds(), remove)

        if not self.is_valid_party(request):
            if self.config['loglevel'] == 'debug':
                self.send(
                    self.l(
                        'ignoring_event_party_id_mismatch',
                        'party_join_request',
                        self.party_id,
                        request.party.id
                    ),
                    color=yellow,
                    add_p=self.time_party,
                    add_d=[self.discord_party, self.debug_message]
                )
            return

        self.send(
            self.l(
                'party_join_request',
                self.name(request.friend)
            ),
            color=blue,
            add_p=self.time_party,
            add_d=self.discord_party
        )

        ret = await self.exec_event('party_join_request', {**locals(), **self.variables})
        if ret is False:
            return

    async def event_party_join_request_expire(self, friend: fortnitepy.Friend) -> None:
        if friend.id in self.join_requests:
            self.join_requests.pop(friend.id)

    async def event_party_invite(self, invitation: fortnitepy.ReceivedPartyInvitation) -> None:
        if not self.is_ready():
            await self.wait_until_ready()

        self.invites[invitation.sender.id] = invitation

        ret = await self.exec_event('party_invite', {**locals(), **self.variables})
        if ret is False:
            return

        if getattr(self, 'party', None) is not None:
            for member in self.party.members:
                user_type = self.get_user_type(invitation.sender.id)
                if (self.is_decline_invite_when(self.get_user_type(member.id))
                        and user_type not in ['whitelist', 'owner']):
                    self.send(
                        self.l(
                            ('invite_decline_when'
                             if self.config['loglevel'] == 'normal' else
                             'invite_decline_when_info'),
                            self.name(member),
                            (self.name(invitation.sender)
                                if user_type == 'user' else
                                f'{self.name(invitation.sender)}({self.l(user_type)})'),
                            invitation.party.id
                        ),
                        add_p=self.time
                    )
                    await invitation.sender.send(str(self.l(
                        'reply_invite_decline_when'
                    )))
                    await invitation.decline()
                    return

        if (self.invite_interval_handle is not None
                and self.invite_interval_handle.when() < self.loop.time()):
            self.invite_interval = False
            self.invite_interval_handle = None

        if self.is_invite_interval_for(self.get_user_type(invitation.sender.id)) and self.invite_interval:
            self.send(
                self.l(
                    ('invite_decline'
                        if self.config['loglevel'] == 'normal' else
                        'invite_decline_info'),
                    self.name(invitation.sender),
                    invitation.party.id
                ),
                add_p=self.time
            )
            await invitation.sender.send(str(self.l(
                'reply_invite_decline_interval',
                int(self.invite_interval_handle.when() - self.loop.time()),
                client=self
            )))
            await invitation.decline()
            if invitation.sender.id in self.invites:
                self.invites.pop(invitation.sender.id)
            return

        if self.is_accept_invite_for(self.get_user_type(invitation.sender.id)):
            self.send(
                self.l(
                    ('invite_accept'
                     if self.config['loglevel'] == 'normal' else
                     'invite_accept_info'),
                    self.name(invitation.sender),
                    invitation.party.id
                ),
                add_p=self.time
            )
            await invitation.accept()
            if self.config['fortnite']['invite_interval']:
                self.invite_interval = True
                self.invite_interval_handle = self.loop.call_later(
                    self.config['fortnite']['invite_interval'],
                    self.invite_interval_callback
                )
        else:
            self.send(
                self.l(
                    ('invite_decline'
                        if self.config['loglevel'] == 'normal' else
                        'invite_decline_info'),
                    self.name(invitation.sender),
                    invitation.party.id
                ),
                add_p=self.time
            )
            await invitation.decline()
            if invitation.sender.id in self.invites:
                self.invites.pop(invitation.sender.id)

    async def event_party_invite_decline(self, friend: fortnitepy.Friend) -> None:
        if friend.id in self.invites:
            self.invites.pop(friend.id)

    async def event_party_invite_cancel(self, friend: fortnitepy.Friend) -> None:
        if friend.id in self.invites:
            self.invites.pop(friend.id)

    async def event_friend_request(self, request: Union[fortnitepy.IncomingPendingFriend, fortnitepy.OutgoingPendingFriend]) -> None:
        if not self.is_ready():
            await self.wait_until_ready()

        if request.outgoing:
            self.send(
                self.l(
                    'friend_request_outgoing',
                    self.name(request)
                ),
                add_p=self.time
            )
            return
        self.send(
            self.l(
                'friend_request_incoming',
                self.name(request)
            ),
            add_p=self.time
        )

        ret = await self.exec_event('friend_request', {**locals(), **self.variables})
        if ret is False:
            return

        if self.is_accept_friend_for(self.get_user_type(request.id)):
            # This log will appear in friend_add
            await self.accept_request(request)
        else:
            self.send(
                self.l(
                    'friend_request_decline',
                    self.name(request)
                ),
                add_p=self.time
            )
            await self.decline_request(request)

    async def event_friend_add(self, friend: fortnitepy.Friend) -> None:
        if not self.is_ready():
            await self.wait_until_ready()

        if friend.outgoing:
            self.send(
                self.l(
                    'friend_add_outgoing',
                    self.name(friend)
                ),
                add_p=self.time
            )
        else:
            self.send(
                self.l(
                    'friend_add_incoming',
                    self.name(friend)
                ),
                add_p=self.time
            )
            if self.is_invitelist(friend.id):
                self._invitelist[friend.id] = friend

        ret = await self.exec_event('friend_add', {**locals(), **self.variables})
        if ret is False:
            return

    async def event_friend_remove(self, friend: fortnitepy.Friend) -> None:
        if not self.is_ready():
            await self.wait_until_ready()

        self.send(
            self.l(
                'friend_remove',
                self.name(friend)
            ),
            add_p=self.time
        )
        if self.is_invitelist(friend.id):
            self._invitelist[friend.id] = self.get_as_user(friend)

        ret = await self.exec_event('friend_remove', {**locals(), **self.variables})
        if ret is False:
            return

    async def event_party_member_join(self, member: fortnitepy.PartyMember) -> None:
        if not self.is_ready():
            await self.wait_until_ready()

        inviter = None
        if member.id == self.user.id:
            invite = discord.utils.find(
                lambda i: i.sender in self.party.members and i.party.id == self.party.id,
                self.invites.values()
            )
            if invite is not None:
                inviter = invite.sender

        if not self.is_valid_party(member):
            if self.config['loglevel'] == 'debug':
                self.send(
                    self.l(
                        'ignoring_event_party_id_mismatch',
                        'party_member_join',
                        self.party_id,
                        member.party.id
                    ),
                    color=yellow,
                    add_p=self.time_party,
                    add_d=[self.discord_party, self.debug_message]
                )
            return

        name = self.is_most()
        if name is not None:
            self.send(
                self.l(
                    'party_member_join',
                    self.name(member),
                    member.party.member_count
                ),
                user_name=name,
                color=blue,
                add_p=partial(self.time_party, name=name),
                add_d=self.discord_party
            )

        ret = await self.exec_event('party_member_join', {**locals(), **self.variables})
        if ret is False:
            return

        if (member.id == self.user.id and self.get_config_item_path(self.config['fortnite']['emote']) is not None
                and self.emote is None and self.emote_section is None):
            await self.party.me.change_asset(
                'AthenaDance',
                self.get_config_item_path(self.config['fortnite']['emote']),
                section=self.config['fortnite']['emote_section']
            )

        if self.party_hides.get(self.party.id) is None:
            self.party_hides[self.party.id] = []
        if self.party.me.leader and self.is_hide_for(self.get_user_type(member.id)):
            self.party_hides[self.party.id].append(member.id)
        self.party.update_hide_users(self.party_hides[self.party.id])

        await self.ng_check(member)

        if self.party.me.leader and member.id == self.user.id:
            self.loop.create_task(self.init_party())

        local = locals()

        async def send_messages():
            muc_party_id = None
            if self.xmpp.muc_room is not None:
                muc_party_id = self.xmpp.muc_room._mucjid.localpart[len('party-'):]
            if muc_party_id != self.party.id:
                await self.wait_for('muc_enter', timeout=5)

            var = self.variables
            var.update(local)
            var.update({
                'member': member,
                'member_display_name': member.display_name,
                'member_id': member.id
            })
            if self.config['fortnite']['join_message']:
                text = self.eval_format(
                    '\n'.join(self.config['fortnite']['join_message']),
                    var
                )
                try:
                    await self.party.send(text)
                except Exception as e:
                    self.print_exception(e)
            friend = self.get_friend(member.id)
            if friend is not None and self.config['fortnite']['join_message_whisper']:
                text = self.eval_format(
                    '\n'.join(self.config['fortnite']['join_message_whisper']),
                    var
                )
                try:
                    await friend.send(text)
                except Exception as e:
                    self.print_exception(e)

            if self.config['fortnite']['random_message']:
                text = self.eval_format(
                    '\n'.join(
                        random.choice(self.config['fortnite']['random_message'])
                    ),
                    var
                )
                try:
                    await self.party.send(text)
                    self.send(
                        self.l(
                            'random_message',
                            text
                        ),
                        add_p=self.time
                    )
                except Exception as e:
                    self.print_exception(e)
            if friend is not None and self.config['fortnite']['random_message_whisper']:
                text = self.eval_format(
                    '\n'.join(
                        random.choice(self.config['fortnite']['random_message_whisper'])
                    ),
                    var
                )
                try:
                    await friend.send(text)
                    self.send(
                        self.l(
                            'random_message',
                            text
                        ),
                        add_p=self.time
                    )
                except Exception as e:
                    self.print_exception(e)

        self.loop.create_task(send_messages())

        async def add_members():
            for member in self.party.members:
                if member.id == self.user.id or self.has_friend(member.id):
                    continue
                pending = self.get_incoming_pending_friend(member.id)
                if pending is not None:
                    await self.accept_request(pending)
                elif (not self.has_friend(member.id)
                      and not self.is_outgoing_pending(member.id)):
                    await self.send_friend_request(member)

        if (getattr(self, 'party', None) is not None
                and self.config['fortnite']['send_friend_request']):
            self.loop.create_task(add_members())

        await asyncio.sleep(0.1)  # Avoid to visual bug

        items = [
            'AthenaCharacter',
            'AthenaBackpack',
            'AthenaPickaxe',
            'AthenaDance'
        ]
        for item in items:
            conf = self.bot.convert_backend_type(item)

            if (not self.config['fortnite'][f'join_{conf}'] and item == 'AthenaDance'
                    and self.config['fortnite']['repeat_emote_when_join']):
                await self.party.me.change_asset(
                    item,
                    self.emote,
                    section=self.emote_section
                )
                continue

            if self.config['fortnite'][f'join_{conf}'] is None:
                continue

            variants = []
            if item != 'AthenaDance' and self.config['fortnite'][f'join_{conf}_style'] is not None:
                for style in self.config['fortnite'][f'join_{conf}_style']:
                    variant = self.get_config_variant(style)
                    if variant is not None:
                        variants.extend(variant['variants'])

            section = 0
            if item == 'AthenaDance':
                section = self.config['fortnite'][f'join_{conf}_section']

            flag = False
            if (member.id == self.user.id
                    and self.config['fortnite'][f'join_{conf}_on'] == 'me'):
                flag = True
            elif self.config['fortnite'][f'join_{conf}_on'] == 'user':
                flag = True

            if flag:
                await self.party.me.change_asset(
                    item,
                    (self.get_config_item_path(self.config['fortnite'][f'join_{conf}'])
                     or self.config['fortnite'][f'join_{conf}']),
                    variants=variants,
                    section=section,
                    do_point=False
                )

    async def event_party_member_leave(self, member: fortnitepy.PartyMember) -> None:
        if not self.is_ready():
            await self.wait_until_ready()

        if not self.is_valid_party(member) and member.id != self.user.id:
            if self.config['loglevel'] == 'debug':
                self.send(
                    self.l(
                        'ignoring_event_party_id_mismatch',
                        'party_member_leave',
                        self.party_id,
                        member.party.id
                    ),
                    color=yellow,
                    add_p=self.time_party,
                    add_d=[self.discord_party, self.debug_message]
                )
            return

        name = self.is_most()
        if name is not None:
            self.send(
                self.l(
                    'party_member_leave',
                    self.name(member),
                    member.party.member_count
                ),
                user_name=name,
                color=blue,
                add_p=partial(self.time_party, name=name),
                add_d=partial(self.discord_party, name=name)
            )

        ret = await self.exec_event('party_member_leave', {**locals(), **self.variables})
        if ret is False:
            return

        items = [
            'AthenaCharacter',
            'AthenaBackpack',
            'AthenaPickaxe',
            'AthenaDance'
        ]
        for item in items:
            conf = self.bot.convert_backend_type(item)
            if not self.config['fortnite'][f'leave_{conf}']:
                continue
            if self.config['fortnite'][f'leave_{conf}_on'] == 'user':
                await self.party.me.change_asset(
                    item,
                    (self.get_config_item_path(self.config['fortnite'][f'leave_{conf}'])
                     or self.config['fortnite'][f'leave_{conf}']),
                    do_point=False
                )

    async def event_before_leave_party(self) -> None:
        if not self.is_ready():
            return

        if getattr(self, 'party', None) is None:
            return

        for member in self.party.members:
            if not self.is_bot(member.id):
                break
        else:
            return

        items = [
            'AthenaCharacter',
            'AthenaBackpack',
            'AthenaPickaxe',
            'AthenaDance'
        ]
        flag = False
        for item in items:
            conf = self.bot.convert_backend_type(item)
            if not self.config['fortnite'][f'leave_{conf}']:
                continue

            variants = []
            if item != 'AthenaDance' and self.config['fortnite'][f'leave_{conf}_style'] is not None:
                for style in self.config['fortnite'][f'leave_{conf}_style']:
                    variant = self.get_config_variant(style)
                    if variant is not None:
                        variants.extend(variant['variants'])

            section = 0
            if item == 'AthenaDance':
                section = self.config['fortnite'][f'leave_{conf}_section']

            if self.config['fortnite'][f'leave_{conf}_on'] == 'me':
                await self.party.me.change_asset(
                    item,
                    (self.get_config_item_path(self.config['fortnite'][f'leave_{conf}'])
                     or self.config['fortnite'][f'leave_{conf}']),
                    variants=variants,
                    section=section,
                    do_point=False
                )
                flag = True
        if flag:
            await asyncio.sleep(self.config['fortnite']['leave_delay_for'])

    async def event_party_member_confirm(self, confirmation: fortnitepy.PartyJoinConfirmation) -> None:
        if not self.is_ready():
            await self.wait_until_ready()

        if not self.is_valid_party(confirmation):
            if self.config['loglevel'] == 'debug':
                self.send(
                    self.l(
                        'ignoring_event_party_id_mismatch',
                        'party_member_confirm',
                        self.party_id,
                        confirmation.party.id
                    ),
                    color=yellow,
                    add_p=self.time_party,
                    add_d=[self.discord_party, self.debug_message]
                )
            return

        if self.config['loglevel'] != 'normal':
            self.send(
                self.l(
                    'party_member_confirm',
                    self.name(confirmation.user)
                ),
                color=blue,
                add_p=self.time_party,
                add_d=self.discord_party
            )

        ret = await self.exec_event('party_member_confirm', {**locals(), **self.variables})
        if ret is False:
            return

        if self.is_accept_join_for(self.get_user_type(confirmation.user.id)):
            if self.party_hides.get(self.party.id) is None:
                self.party_hides[self.party.id] = []
            if self.party.me.leader and self.is_hide_for(self.get_user_type(confirmation.user.id)):
                self.party_hides[self.party.id].append(confirmation.user.id)
            self.party.update_hide_users(self.party_hides[self.party.id])

            try:
                await confirmation.confirm()
            except fortnitepy.HTTPException as e:
                self.print_exception(e)
                self.send(
                    self.l(
                        'error_while_confirming_join_request'
                    ),
                    file=sys.stderr
                )
        else:
            try:
                await confirmation.reject()
            except fortnitepy.HTTPException as e:
                self.print_exception(e)
                self.send(
                    self.l(
                        'error_while_rejecting_join_request'
                    ),
                    file=sys.stderr
                )

    async def event_party_member_kick(self, member: fortnitepy.PartyMember) -> None:
        if not self.is_ready():
            await self.wait_until_ready()

        if not self.is_valid_party(member) and member.id != self.user.id:
            if self.config['loglevel'] == 'debug':
                self.send(
                    self.l(
                        'ignoring_event_party_id_mismatch',
                        'party_member_kick',
                        self.party_id,
                        member.party.id
                    ),
                    color=yellow,
                    add_p=self.time_party,
                    add_d=[self.discord_party, self.debug_message]
                )
            return

        name = self.is_most()
        if name is not None:
            self.send(
                self.l(
                    'party_member_kick',
                    self.name(self.party.leader),
                    self.name(member),
                    member.party.member_count
                ),
                user_name=name,
                color=blue,
                add_p=partial(self.time_party, name=name),
                add_d=partial(self.discord_party, name=name)
            )

        ret = await self.exec_event('party_member_kick', {**locals(), **self.variables})
        if ret is False:
            return

    async def event_party_member_promote(self, old_leader: fortnitepy.PartyMember, new_leader: fortnitepy.PartyMember) -> None:
        if not self.is_ready():
            await self.wait_until_ready()

        if not self.is_valid_party(new_leader):
            if self.config['loglevel'] == 'debug':
                self.send(
                    self.l(
                        'ignoring_event_party_id_mismatch',
                        'party_member_promote',
                        self.party_id,
                        new_leader.party.id
                    ),
                    color=yellow,
                    add_p=self.time_party,
                    add_d=[self.discord_party, self.debug_message]
                )
            return

        name = self.is_most()
        if name is not None:
            self.send(
                self.l(
                    'party_member_promote',
                    self.name(old_leader),
                    self.name(new_leader)
                ),
                user_name=name,
                color=blue,
                add_p=partial(self.time_party, name=name),
                add_d=partial(self.discord_party, name=name)
            )

        ret = await self.exec_event('party_member_promote', {**locals(), **self.variables})
        if ret is False:
            return

        if new_leader.id == self.user.id:
            await self.init_party()

    async def event_party_update(self, party: fortnitepy.ClientParty) -> None:
        if not self.is_ready():
            await self.wait_until_ready()

        if not self.is_valid_party(party):
            if self.config['loglevel'] == 'debug':
                self.send(
                    self.l(
                        'ignoring_event_party_id_mismatch',
                        'event_party_update',
                        self.party_id,
                        party.id
                    ),
                    color=yellow,
                    add_p=self.time_party,
                    add_d=[self.discord_party, self.debug_message]
                )
            return

        name = self.is_most()
        if name is not None and self.config['loglevel'] != 'normal':
            self.send(
                self.l(
                    'party_update'
                ),
                user_name=name,
                color=blue,
                add_p=partial(self.time_party, name=name),
                add_d=partial(self.discord_party, name=name)
            )

        ret = await self.exec_event('party_update', {**locals(), **self.variables})
        if ret is False:
            return

    async def event_party_playlist_change(self, party: fortnitepy.ClientParty, before: tuple, after: tuple) -> None:
        if not self.is_ready():
            await self.wait_until_ready()

        if not self.is_valid_party(party):
            if self.config['loglevel'] == 'debug':
                self.send(
                    self.l(
                        'ignoring_event_party_id_mismatch',
                        'party_playlist_change',
                        self.party_id,
                        party.id
                    ),
                    color=yellow,
                    add_p=self.time_party,
                    add_d=[self.discord_party, self.debug_message]
                )
            return

        name = self.is_most()
        if name is not None and self.config['loglevel'] != 'normal':
            self.send(
                f'PlaylistID: {after[0]}',
                user_name=name,
                color=blue,
                add_p=partial(self.time_party, name=name),
                add_d=partial(self.discord_party, name=name)
            )

    async def event_party_member_update(self, member: fortnitepy.PartyMember) -> None:
        if not self.is_ready():
            await self.wait_until_ready()
        if member.id == self.user.id:
            return

        if not self.is_valid_party(member):
            if self.config['loglevel'] == 'debug':
                self.send(
                    self.l(
                        'ignoring_event_party_id_mismatch',
                        'party_playlist_change',
                        self.party_id,
                        member.party.id
                    ),
                    color=yellow,
                    add_p=self.time_party,
                    add_d=[self.discord_party, self.debug_message]
                )
            return

        name = self.is_most()
        if name is not None and self.config['loglevel'] != 'normal':
            self.send(
                self.l(
                    'party_member_update',
                    self.name(member)
                ),
                user_name=name,
                color=blue,
                add_p=partial(self.time_party, name=name),
                add_d=partial(self.discord_party, name=name)
            )

        ret = await self.exec_event('party_member_update', {**locals(), **self.variables})
        if ret is False:
            return

    async def party_member_asset_change(self, member: fortnitepy.PartyMember, item: str) -> None:
        if not self.is_ready():
            await self.wait_until_ready()
        if member.id == self.user.id:
            return

        if not self.is_valid_party(member):
            if self.config['loglevel'] == 'debug':
                self.send(
                    self.l(
                        'ignoring_event_party_id_mismatch',
                        'member_asset_change',
                        self.party_id,
                        member.party.id
                    ),
                    color=yellow,
                    add_p=self.time_party,
                    add_d=[self. discord_party, self.debug_message]
                )
            return

        await self.ng_check(member)

        asset = self.asset(item, member)
        name = self.is_most()
        if (name is not None and self.config['loglevel'] != 'normal'
                and asset):
            self.send(
                f"'{self.name(member)}': {self.bot.convert_backend_to_id(item)}: {asset}",
                user_name=name,
                color=blue,
                add_p=partial(self.time_party, name=name),
                add_d=partial(self.discord_party, name=name)
            )

        attr = f'is_{self.bot.convert_backend_to_key(item)}_mimic_for'
        attr2 = f'{self.bot.convert_backend_to_key(item)}_mimic'
        if getattr(self, attr)(self.get_user_type(member.id)) or member.id in getattr(self, attr2):
            if self.bot.convert_backend_to_key(item) == 'emote' and not asset:
                return

            attr = f'is_{self.bot.convert_backend_to_key(item)}_lock_for'
            if not getattr(self, attr)(self.get_user_type(member.id)):
                await self.party.me.change_asset(
                    item,
                    asset=asset or '',
                    variants=self.variants(item, member),
                    enlightenment=member.enlightenments,
                    section=self.section(member),
                    do_point=False
                )

    async def event_party_member_outfit_change(self, member: fortnitepy.PartyMember, before: str, after: str) -> None:
        await self.party_member_asset_change(member, 'AthenaCharacter')

    async def event_party_member_backpack_change(self, member: fortnitepy.PartyMember, before: str, after: str) -> None:
        await self.party_member_asset_change(member, 'AthenaCharacter')

    async def event_party_member_pet_change(self, member: fortnitepy.PartyMember, before: str, after: str) -> None:
        await self.party_member_asset_change(member, 'AthenaPetCarrier')

    async def event_party_member_pickaxe_change(self, member: fortnitepy.PartyMember, before: str, after: str) -> None:
        await self.party_member_asset_change(member, 'AthenaPickaxe')

    async def event_party_member_emote_change(self, member: fortnitepy.PartyMember, before: str, after: str) -> None:
        await self.party_member_asset_change(member, 'AthenaDance')

    async def event_party_member_emoji_change(self, member: fortnitepy.PartyMember, before: str, after: str) -> None:
        await self.party_member_asset_change(member, 'AthenaEmoji')

    async def event_party_member_zombie(self, member: fortnitepy.PartyMember) -> None:
        if not self.is_ready():
            await self.wait_until_ready()

        if not self.is_valid_party(member):
            if self.config['loglevel'] == 'debug':
                self.send(
                    self.l(
                        'ignoring_event_party_id_mismatch',
                        'party_member_zombie',
                        self.party_id,
                        member.party.id
                    ),
                    color=yellow,
                    add_p=self.time_party,
                    add_d=[self.discord_party, self.debug_message]
                )
            return

        name = self.is_most()
        if name is not None:
            self.send(
                self.l(
                    'party_member_zombie',
                    self.name(member)
                ),
                user_name=name,
                color=blue,
                add_p=partial(self.time_party, name=name),
                add_d=partial(self.discord_party, name=name)
            )

        ret = await self.exec_event('party_member_disconnect', {**locals(), **self.variables})
        if ret is False:
            return

        if self.party.me.leader and self.config['fortnite']['kick_disconnect']:
            await member.kick()

    async def event_party_member_in_match_change(self, member: fortnitepy.PartyMember, before: bool, after: bool) -> None:
        if not self.is_ready():
            await self.wait_until_ready()

        if not self.is_valid_party(member):
            if self.config['loglevel'] == 'debug':
                self.send(
                    self.l(
                        'ignoring_event_party_id_mismatch',
                        'party_member_in_match_change',
                        self.party_id,
                        member.party.id
                    ),
                    color=yellow,
                    add_p=self.time_party,
                    add_d=[self.discord_party, self.debug_message]
                )
            return

        name = self.is_most()
        if name is not None and self.config['loglevel'] != 'normal':
            self.send(
                self.l(
                    'party_member_in_match_change',
                    self.name(member)
                ),
                user_name=name,
                color=blue,
                add_p=partial(self.time_party, name=name),
                add_d=partial(self.discord_party, name=name)
            )

        if (self.party.me.leader and self.config['fortnite']['kick_in_match']
                and after):
            await member.kick()

    async def event_party_member_chatban(self, member: fortnitepy.PartyMember, reason: Optional[str]) -> None:
        if not self.is_ready():
            await self.wait_until_ready()

        if not self.is_valid_party(member):
            if self.config['loglevel'] == 'debug':
                self.send(
                    self.l(
                        'ignoring_event_party_id_mismatch',
                        'party_member_chatban',
                        self.party_id,
                        member.party.id
                    ),
                    color=yellow,
                    add_p=self.time_party,
                    add_d=[self.discord_party, self.debug_message]
                )
            return

        name = self.is_most()
        if name is not None and self.config['loglevel'] != 'normal':
            if not reason:
                self.send(
                    self.l(
                        'party_member_chatban',
                        self.name(member)
                    ),
                    user_name=name,
                    color=blue,
                    add_p=partial(self.time_party, name=name),
                    add_d=partial(self.discord_party, name=name)
                )
            else:
                self.send(
                    self.l(
                        'party_member_chatban_reason',
                        self.name(member),
                        reason
                    ),
                    user_name=name,
                    color=blue,
                    add_p=partial(self.time_party, name=name),
                    add_d=partial(self.discord_party, name=name)
                )

    async def event_party_message(self, message: fortnitepy.PartyMessage) -> None:
        if not self.is_ready():
            await self.wait_until_ready()

        if not self.is_valid_party(message.author):
            if self.config['loglevel'] == 'debug':
                self.send(
                    self.l(
                        'ignoring_event_party_id_mismatch',
                        'event_party_message',
                        self.party_id,
                        message.author.party.id
                    ),
                    color=yellow,
                    add_p=self.time_party,
                    add_d=[self.discord_party, self.debug_message]
                )
            return

        if (self.config['fortnite']['chat_max'] is not None
                and self.is_chat_max_for(self.get_user_type(message.author.id))
                and len(message.content) > self.config['fortnite']['chat_max']):
            functions = await self.get_chat_max_operation(user_id=message.author.id)
            for func in functions:
                try:
                    if asyncio.iscoroutinefunction(func):
                        await func()
                    else:
                        func()
                except Exception as e:
                    self.print_exception(e)
            return

        if not await self.ng_word_check(message):
            return

        if not self.is_party_chat_enable_for(self.get_user_type(message.author.id)):
            return

        self.send(
            message.content,
            user_name=self.name(message.author),
            add_p=[lambda x: f'{self.name(message.author)} | {x}', self.time_party],
            add_d=self.discord_party
        )

        mes = MyMessage(self, message)
        await self.process_command(mes, self.config['fortnite']['prefix'])

    async def event_friend_message(self, message: fortnitepy.FriendMessage) -> None:
        if not self.is_ready():
            await self.wait_until_ready()

        if (self.config['fortnite']['chat_max'] is not None
                and self.is_chat_max_for(self.get_user_type(message.author.id))
                and len(message.content) > self.config['fortnite']['chat_max']):
            functions = await self.get_chat_max_operation(user_id=message.author.id)
            for func in functions:
                try:
                    if asyncio.iscoroutinefunction(func):
                        await func()
                    else:
                        func()
                except Exception as e:
                    self.print_exception(e)
            return

        if not await self.ng_word_check(message):
            return

        if not self.is_whisper_enable_for(self.get_user_type(message.author.id)):
            return

        self.send(
            message.content,
            user_name=self.name(message.author),
            color=magenta,
            add_p=[lambda x: f'{self.name(message.author)} | {x}', self.time]
        )

        mes = MyMessage(self, message)
        await self.process_command(mes, self.config['fortnite']['prefix'])


    # Commands
    async def show_help(self, command: Command, message: MyMessage) -> None:
        await message.reply(
            self.l(
                'usage',
                self.eval_format(
                    command.usage,
                    {
                        **self.variables,
                        **{'name': self.commands['commands'][command.name][0]}
                    }
                )
            )
        )

    async def call_command(self, command: Command, message: MyMessage) -> None:
        try:
            await command.callback(self, message)
        except Exception as e:
            await message.reply(
                self.l('error') + f'\n{e.__class__.__name__}'
            )
            self.print_exception(e)

    async def process_command(self, message: MyMessage, prefixes: Optional[list]) -> None:
        if not message.args:
            return

        execute = True
        prefix_length = 0
        if prefixes:
            for prefix in prefixes:
                if message.content.startswith(prefix):
                    prefix_length = len(prefix)
                    break
            else:
                execute = False
        content = message.content[prefix_length:]
        args = re.split(r'\s', content)

        async def replies():
            flag = False
            if self.replies['prefix_to_replies']:
                if execute:
                    flag = True
            else:
                flag = True

            if not flag:
                return False

            for word in self.replies['replies']:
                if word in self.disabled_replies:
                    continue

                flag = False
                if word['matchmethod'] == 'full' and word['word'] == content:
                    flag = True
                elif word['matchmethod'] == 'contains' and word['word'] in content:
                    flag = True
                elif word['matchmethod'] == 'starts' and content.startswith(word['word']):
                    flag = True
                elif word['matchmethod'] == 'ends' and content.endswith(word['word']):
                    flag = True
                if flag:
                    def remove():
                        if word in self.disabled_replies:
                            self.disabled_replies.remove(word)

                    if word['ct']:
                        self.disabled_replies.append(word)
                        self.loop.call_later(
                            word['ct'],
                            remove
                        )
                    var = self.variables
                    var.update({
                        'message': message,
                        'author': message.author,
                        'author_display_name': message.author.display_name,
                        'author_id': message.author.id
                    })
                    text = self.eval_format('\n'.join(word['reply']), var)
                    await message.reply(text)
                    return True
            return False

        if self.replies['run_when'] == 'before_command':
            if await replies():
                return

        executed = False
        if execute:
            message.prev = self.prev.get(message.author.id)
            arg = args[0]
            if self.config['case_insensitive']:
                arg = jaconv.kata2hira(arg.lower())
            if self.config['convert_kanji']:
                arg = self.bot.converter.do(arg)

            async def missing_permission():
                await message.reply(
                    self.l('missing_permission')
                )
                if not message.is_discord_message():
                    functions = await self.get_permission_command_operation(user_id=message.author.id)
                    for func in functions:
                        try:
                            if asyncio.iscoroutinefunction(func):
                                await func()
                            else:
                                func()
                        except Exception as e:
                            self.print_exception(e)

            async def custom_commands():
                for command in self.custom_commands['commands']:
                    if command['word'] == content:
                        if message.user_type in command['allow_for']:
                            try:
                                var = self.variables
                                var.update({
                                    'message': message,
                                    'author': message.author,
                                    'author_display_name': message.author.display_name,
                                    'author_id': message.author.id
                                })
                                await self.bot.aexec('\n'.join(command['run']), var)
                            except Exception as e:
                                self.debug_print_exception(e)
                                for line in command['run']:
                                    try:
                                        var = self.variables
                                        var.update({
                                            'message': message,
                                            'author': message.author,
                                            'author_display_name': message.author.display_name,
                                            'author_id': message.author.id
                                        })
                                        await self.bot.aexec(line, var)
                                    except Exception as e:
                                        self.debug_print_exception(e)
                                        mes = DummyMessage(self, message, content=line)
                                        await self.process_command(MyMessage(self, mes), None)
                                        if self.config['loglevel'] == 'debug':
                                            self.send(
                                                mes.result,
                                                color=yellow
                                            )
                        else:
                            await missing_permission()
                        return True
                return False

            if self.custom_commands['run_when'] == 'before_command':
                if await custom_commands():
                    return

            tasks = []
            for identifier, command in self.all_commands.items():
                try:
                    if command.discord_required and self.discord_client is None:
                        continue

                    words = self.commands['commands'][identifier]
                    if self.config['case_insensitive']:
                        words = [jaconv.kata2hira(word.lower()) for word in words]
                    if self.config['convert_kanji']:
                        words = [self.bot.converter.do(word) for word in words]
                    if arg in words:
                        executed = True
                        if (message.user_type == 'owner'
                                or (identifier.lower() in self.whitelist_commands
                                    and message.user_type in ['owner', 'whitelist'])
                                or identifier.lower() in self.user_commands):
                            tasks.append(
                                self.loop.create_task(self.call_command(command, message))
                            )

                            if self.user.id not in self.bot.command_stats:
                                self.bot.command_stats[self.user.id] = {'commands': {}, 'ngs': {}}
                            stats = self.bot.command_stats[self.user.id]
                            if str(message.author.id) not in stats['commands']:
                                stats['commands'][str(message.author.id)] = {}
                            if identifier not in stats['commands'][str(message.author.id)]:
                                stats['commands'][str(message.author.id)][identifier] = 0
                            stats['commands'][str(message.author.id)][identifier] += 1
                        else:
                            await missing_permission()
                        break
                except KeyError as e:
                    self.debug_print_exception(e)

            if len(tasks) > 0:
                await asyncio.wait(tasks)

            if not executed and self.custom_commands['run_when'] == 'after_command':
                if await custom_commands():
                    return

            self.prev[message.author.id] = message

        execute_item_search = False
        if self.commands['prefix_to_item_search']:
            if execute:
                execute_item_search = True
        else:
            execute_item_search = True
        if execute_item_search:
            select = self.select.get(message.author.id)
            if select is not None and content.isdigit():
                executed = True
                num = int(content) - 1
                if len(select['variables']) < (num + 1):
                    await message.reply(
                        self.l('please_enter_valid_number')
                    )
                    return

                variables = globals()
                variables.update(select['globals'])
                variables.update(select['variables'][num])
                await self.bot.aexec(select['exec'], variables)

        if self.replies['run_when'] == 'after_command':
            if await replies():
                return

        if not executed and execute_item_search:
            for item, prefix in self.bot.BACKEND_TO_ID_CONVERTER.items():
                if args[0].lower().startswith(f'{prefix}_'.lower()):
                    if (message.user_type == 'owner'
                            or (f'{prefix}_'.lower() in self.whitelist_commands
                                and message.user_type in ['owner', 'whitelist'])
                            or f'{prefix}_'.lower() in self.user_commands):
                        key = self.bot.convert_backend_to_key(item)
                        attr = f'is_{key}_lock_for'
                        if getattr(self, attr)(message.user_type):
                            await message.reply(
                                self.l('cosmetic_locked')
                            )
                            return
                        await self.party.me.change_asset(
                            item,
                            args[0].replace('/', '').replace('\\', '')
                        )
                        await message.reply(
                            self.l(
                                'set_to',
                                self.bot.l(key),
                                args[0].replace('/', '').replace('\\', '')
                            )
                        )
                    else:
                        await message.reply(
                            self.l('missing_permission')
                        )
                        if not message.is_discord_message():
                            functions = await self.get_permission_command_operation(user_id=message.author.id)
                            for func in functions:
                                try:
                                    if asyncio.iscoroutinefunction(func):
                                        await func()
                                    else:
                                        func()
                                except Exception as e:
                                    self.print_exception(e)
                    return

            if args[0].lower().startswith('playlist_'):
                if (message.user_type == 'owner'
                        or (f'playlist_' in self.whitelist_commands
                            and message.user_type in ['owner', 'whitelist'])
                        or f'playlist_' in self.user_commands):
                    if not self.party.leader:
                        await message.reply(
                            self.l('not_a_party_leader')
                        )
                        return
                    try:
                        await self.party.set_playlist(args[0])
                    except fortnitepy.Forbidden:
                        await message.reply(
                            self.l('not_a_party_leader')
                        )
                        return
                    await message.reply(
                        self.l(
                            'set_to',
                            self.bot.l('playlist'),
                            args[0]
                        )
                    )
                else:
                    await message.reply(
                        self.l('missing_permission')
                    )
                    if not message.is_discord_message():
                        functions = await self.get_permission_command_operation(user_id=message.author.id)
                        for func in functions:
                            try:
                                if asyncio.iscoroutinefunction(func):
                                    await func()
                                else:
                                    func()
                            except Exception as e:
                                self.print_exception(e)
                return

            if (message.user_type == 'owner'
                    or ('item_search' in self.whitelist_commands
                        and message.user_type in ['owner', 'whitelist'])
                    or 'item_search' in self.user_commands):
                async def set_cosmetic(cosmetic):
                    item = cosmetic["type"]["backendValue"]
                    attr = f'is_{self.bot.convert_backend_to_key(item)}_lock_for'
                    if getattr(self, attr)(message.user_type):
                        await message.reply(
                            self.l('cosmetic_locked')
                        )
                        return
                    await self.party.me.change_asset(item, cosmetic['path'])
                    await message.reply(
                        self.l(
                            'set_to',
                            cosmetic['type']['displayValue'],
                            self.name_cosmetic(cosmetic)
                        )
                    )

                cosmetics = self.searcher.search_item_name_id(content)

                if self.config['search_max'] and len(cosmetics) > self.config['search_max']:
                    await message.reply(
                        self.l('too_many', self.l('item'), len(cosmetics))
                    )
                    return

                if len(cosmetics) == 0:
                    return

                if len(cosmetics) == 1:
                    await set_cosmetic(cosmetics[0])
                else:
                    self.select[message.author.id] = {
                        'exec': 'await set_cosmetic(cosmetic)',
                        'globals': {**globals(), **locals()},
                        'variables': [
                            {'cosmetic': cosmetic}
                            for cosmetic in cosmetics
                        ]
                    }
                    await message.reply(
                        ('\n'.join([f'{num}: {self.name_cosmetic(cosmetic)}'
                                    for num, cosmetic in enumerate(cosmetics, 1)])
                        + '\n' + self.l('enter_number_to_select', self.l('item')))
                    )
