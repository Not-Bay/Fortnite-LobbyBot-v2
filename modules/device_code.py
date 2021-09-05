import asyncio
import datetime
import importlib
import json
from typing import Any, Optional, Tuple, Union, TYPE_CHECKING

import aiohttp

if TYPE_CHECKING:
    from .bot import Bot

fortnitepy = importlib.import_module('fortnitepy')


ACCOUNT_PUBLIC_SERVICE = "https://account-public-service-prod03.ol.epicgames.com"
OAUTH_TOKEN = f"{ACCOUNT_PUBLIC_SERVICE}/account/api/oauth/token"
EXCHANGE = f"{ACCOUNT_PUBLIC_SERVICE}/account/api/oauth/exchange"
DEVICE_CODE = f"{ACCOUNT_PUBLIC_SERVICE}/account/api/oauth/deviceAuthorization"
ACCOUNT_BY_USER_ID = f"{ACCOUNT_PUBLIC_SERVICE}/account/api/public/account/" + "{user_id}"
DEVICE_AUTH_GENERATE = f"{ACCOUNT_PUBLIC_SERVICE}/account/api/public/account/" + "{account_id}/deviceAuth"


class HTTPException(Exception):
    def __init__(self, message_code: str, message: str) -> None:
        self.message_code = message_code
        super().__init__(message)


class HTTPClient:
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session

    @staticmethod
    async def read(response: aiohttp.ClientResponse) -> Union[bytes, dict, list, str]:
        text = await response.text(encoding='utf-8')
        if 'application/json' in response.headers.get('content-type', ''):
            return json.loads(text)
        return text

    async def close(self) -> None:
        await self.session.close()

    async def request(self, method: str, url: str,
                      raw: Optional[bool] = False, **kwargs: dict
                      ) -> Union[aiohttp.ClientResponse, Union[bytes, dict, list, str]]:
        async with self.session.request(method, url, **kwargs) as response:
            data = await self.read(response)
            if isinstance(data, dict) and 'errorCode' in data:
                raise HTTPException(data['errorCode'], data['errorMessage'])
            if raw:
                return response
            return data

    async def get(self, url: str, **kwargs: dict
                  ) -> Union[aiohttp.ClientResponse, Union[bytes, dict, list, str]]:
        return await self.request('GET', url, **kwargs)

    async def post(self, url: str, **kwargs: dict
                   ) -> Union[aiohttp.ClientResponse, Union[bytes, dict, list, str]]:
        return await self.request('POST', url, **kwargs)


class Auth:
    def __init__(self, bot: 'Bot',
                 http: HTTPClient) -> None:
        self.bot = bot

        fortnitepy_auth = fortnitepy.Auth()
        self._launcher_token = fortnitepy_auth.ios_token
        self._fortnite_token = fortnitepy_auth.fortnite_token
        self._switch_token = 'OThmN2U0MmMyZTNhNGY4NmE3NGViNDNmYmI0MWVkMzk6MGEyNDQ5YTItMDAxYS00NTFlLWFmZWMtM2U4MTI5MDFjNGQ3'

        self.http = http

    async def close(self) -> None:
        await self.http.close()

    async def fetch_launcher_access_token(self, payload: dict, launcher_token: Optional[str] = None
                                          ) -> Tuple[str, str, datetime.datetime, str]:
        data = await self.http.post(
            OAUTH_TOKEN,
            headers={
                'Authorization': f'basic {launcher_token or self._launcher_token}'
            },
            data=payload
        )
        return (
            data['access_token'],
            data['refresh_token'],
            fortnitepy.Client.from_iso(data['expires_at']),
            data['account_id']
        )

    async def fetch_client_credentials(self) -> Tuple[str, datetime.datetime]:
        data = await self.http.post(
            OAUTH_TOKEN,
            headers={
                'Authorization': f'basic {self._switch_token}'
            },
            data={
                'grant_type': 'client_credentials',
                'token_type': 'eg1'
            }
        )
        return data['access_token'], fortnitepy.Client.from_iso(data['expires_at'])

    async def get_exchange_code(self, access_token: str) -> str:
        data = await self.http.get(
            EXCHANGE,
            headers={
                'Authorization': f'bearer {access_token}'
            }
        )
        return data['code']

    async def exchange_code_for_session(self, token: str, code: str) -> dict:
        payload = {
            'grant_type': 'exchange_code',
            'exchange_code': code,
            'token_type': 'eg1',
        }

        return await self.http.post(
            OAUTH_TOKEN,
            headers={
                'Authorization': f'basic {token}'
            },
            data=payload
        )

    async def get_device_code(self, access_token: str) -> Tuple[str, str, str]:
        data = await self.http.post(
            DEVICE_CODE,
            headers={
                'Authorization': f'bearer {access_token}',
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            data={
                'prompt': 'login',
                'grant_type': 'device_code'
            }
        )
        return data['user_code'], data['device_code'], data['verification_uri_complete']

    async def generate_device_auth(self, account_id: str, access_token: str) -> Tuple[str, str, str]:
        data = await self.http.post(
            DEVICE_AUTH_GENERATE.format(account_id=account_id),
            headers={
                'Authorization': f'bearer {access_token}',
                'Content-Type': 'application/json'
            }
        )
        return data['deviceId'], data['accountId'], data['secret']

    async def account_by_user_id(self, access_token: str, user_id: str):
        data = await self.http.get(
            ACCOUNT_BY_USER_ID.format(user_id=user_id),
            headers={
                'Authorization': f'bearer {access_token}'
            }
        )
        return data

    async def device_code_auth(self, email: str) -> Tuple[str, str, datetime.datetime, str]:
        client_expires_at = None
        client_access_token = None
        access_token = None
        while True:
            if client_expires_at is None or (client_expires_at - datetime.timedelta(minutes=1)) > datetime.datetime.utcnow():
                client_access_token, client_expires_at = await self.fetch_client_credentials()
            _, device_code, uri = await self.get_device_code(client_access_token)

            payload = {
                'grant_type': 'device_code',
                'device_code': device_code,
                'token_type': 'eg1'
            }
            text = self.bot.l(
                'confirm_authorization',
                uri,
                email
            )
            self.bot.web_text = text.get_text()
            self.bot.send(text)
            while True:
                flag = False
                try:
                    access_token, _, _, account_id = await self.fetch_launcher_access_token(payload, self._switch_token)
                except HTTPException as e:
                    if e.message_code == 'errors.com.epicgames.not_found':
                        break
                    elif e.message_code == 'errors.com.epicgames.account.oauth.authorization_pending':
                        await asyncio.sleep(5)
                        continue
                    raise
                else:
                    code = await self.get_exchange_code(access_token)
                    fortnite_access_token = (await self.exchange_code_auth(code))[0]
                    user = await self.account_by_user_id(fortnite_access_token, account_id)
                    if self.bot.cleanup_email(user['email']) == self.bot.cleanup_email(email):
                        flag = True
                    else:
                        self.bot.send(
                            self.bot.l(
                                'account_incorrect',
                                user['email'],
                                email
                            )
                        )
                    break
            if flag:
                break
        self.bot.web_text = ''
        code = await self.get_exchange_code(access_token)
        return await self.exchange_code_auth(code)

    async def exchange_code_auth(self, code: str) -> Tuple[str, str, datetime.datetime, str]:
        payload = {
            'grant_type': 'exchange_code',
            'exchange_code': code,
            'token_type': 'eg1'
        }
        return await self.fetch_launcher_access_token(payload)

    async def authenticate(self, email: str) -> dict:
        access_token, _, _, account_id = await self.device_code_auth(email)
        device_id, account_id, secret = await self.generate_device_auth(account_id, access_token)
        return {
            'device_id': device_id,
            'account_id': account_id,
            'secret': secret
        }
