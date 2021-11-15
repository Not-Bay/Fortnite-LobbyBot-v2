import asyncio
import importlib
from typing import Any, Optional
from aioconsole import aprint

fortnitepy = importlib.import_module('fortnitepy')


class MyAdvancedAuth(fortnitepy.Auth):
    def __init__(self, refresh_token: Optional[str] = None,
                 session_id: Optional[fortnitepy.auth.StrOrMaybeCoro] = None,
                 **kwargs: Any):
        super().__init__(**kwargs)

        self.launcher_token = kwargs.get('launcher_token', 'MzRhMDJjZjhmNDQxNGUyOWIxNTkyMTg3NmRhMzZmOWE6ZGFhZmJjY2M3Mzc3NDUwMzlkZmZlNTNkOTRmYzc2Y2Y=')  # noqa

        self.refresh_token = refresh_token
        self.session_id = session_id
        self.kwargs = kwargs

    @property
    def identifier(self) -> str:
        return self.refresh_token or self.session_id

    def eula_check_needed(self) -> bool:
        return False

    def refresh_token_ready(self) -> bool:
        return self.refresh_token is not None

    def session_id_ready(self) -> bool:
        return self.session_id is not None

    async def run_refresh_token_authenticate(self) -> dict:
        auth = fortnitepy.RefreshTokenAuth(
            refresh_token=self.refresh_token,
            ios_token=self.launcher_token,
            **self.kwargs
        )
        auth.initialize(self.client)

        auth._update_ios_data(await auth.ios_authenticate())
        code = await auth.get_exchange_code(auth='bearer {0}'.format(auth.ios_access_token))
        data = await auth.exchange_code_for_session(
            self.ios_token,
            code
        )

        return data

    async def run_session_id_authenticate(self) -> dict:
        auth = SessionIDAuth(
            session_id=self.session_id,
            **self.kwargs
        )
        auth.initialize(self.client)

        return await auth.ios_authenticate()

    async def run_device_code_authenticate(self) -> dict:
        auth = DeviceCodeAuth(
            **self.kwargs
        )
        auth.initialize(self.client)

        return await auth.ios_authenticate()

    async def generate_refresh_token(self) -> str:
        code = await self.get_exchange_code()
        data = await self.exchange_code_for_session(
            self.launcher_token,
            code
        )

        return data

    async def ios_authenticate(self) -> dict:
        data = None

        if self.refresh_token_ready():
            try:
                data = await self.run_refresh_token_authenticate()
            except fortnitepy.HTTPException as e:
                m = 'errors.com.epicgames.account.auth_token.invalid_refresh_token'
                if e.message_code != m:
                    raise
        if data is None and self.session_id_ready():
            data = await self.run_session_id_authenticate()
        if data is None:
            data = await self.run_device_code_authenticate()
        self._update_ios_data(data)

        refresh_token = await self.generate_refresh_token()
        self.client.dispatch_event(
            'refresh_token_generate',
            refresh_token
        )

        return data

    async def authenticate(self, **kwargs) -> None:
        await self.ios_authenticate()

        if self.client.kill_other_sessions:
            await self.kill_other_sessions()

        code = await self.get_exchange_code()
        data = await self.exchange_code_for_session(
            self.fortnite_token,
            code
        )
        self._update_data(data)

    async def do_refresh(self) -> None:
        await super().do_refresh()

        refresh_token = await self.generate_refresh_token()
        self.client.dispatch_event(
            'refresh_token_generate',
            refresh_token
        )


class DeviceCodeAuth(fortnitepy.Auth):
    """Authenticates with device code.

    Parameters
    ----------
    timeout: Optional[]:class:`int`]
        How many seconds to wait for before user complete device code authorization.
        *Defaults to ``60``*
    switch_token: Optional[:class:`str`]
        The switch token to use with authentication. You should generally
        not need to set this manually.
    ios_token: Optional[:class:`str`]
        The ios token to use with authentication. You should generally
        not need to set this manually.
    fortnite_token: Optional[:class:`str`]
        The fortnite token to use with authentication. You should generally
        not need to set this manually.
    """

    def __init__(self, timeout: Optional[int] = 60, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.switch_token = kwargs.get('switch_token', 'OThmN2U0MmMyZTNhNGY4NmE3NGViNDNmYmI0MWVkMzk6MGEyNDQ5YTItMDAxYS00NTFlLWFmZWMtM2U4MTI5MDFjNGQ3')

        self.timeout = timeout
        self._device_code = None

    @property
    def client_authorization(self) -> str:
        return 'bearer {0}'.format(self.client_access_token)

    @property
    def switch_authorization(self) -> str:
        return 'bearer {0}'.format(self.switch_access_token)

    @property
    def identifier(self) -> str:
        return self._device_code

    def _update_client_data(self, data: dict) -> None:
        self.client_access_token = data['access_token']
        self.client_expires_in = data['expires_in']
        self.client_expires_at = self.client.from_iso(data["expires_at"])
        self.client_token_type = data['token_type']
        self.client_client_id = data['client_id']
        self.client_internal_client = data['internal_client']
        self.client_client_service = data['client_service']

    def _update_switch_data(self, data: dict) -> None:
        self.switch_access_token = data['access_token']
        self.switch_expires_in = data['expires_in']
        self.switch_expires_at = self.client.from_iso(data["expires_at"])
        self.switch_token_type = data['token_type']
        self.switch_refresh_token = data['refresh_token']
        self.switch_refresh_expires = data['refresh_expires']
        self.switch_refresh_expires_at = data['refresh_expires_at']
        self.switch_account_id = data['account_id']
        self.switch_client_id = data['client_id']
        self.switch_internal_client = data['internal_client']
        self.switch_client_service = data['client_service']
        self.switch_app = data['app']
        self.switch_in_app_id = data['in_app_id']

    async def get_device_code(self, priority: int = 0) -> dict:
        r = fortnitepy.http.AccountPublicService('/account/api/oauth/deviceAuthorization')
        payload = {
            'grant_type': 'device_code',
            'prompt': 'login'
        }
        return await self.client.http.post(
            r,
            auth=self.client_authorization,
            data=payload,
            priority=priority
        )

    async def wait_device_authorization(self, device_code: str, priority: int = 0) -> dict:
        payload = {
            'grant_type': 'device_code',
            'device_code': device_code,
            'token_type': 'eg1'
        }
        while True:
            try:
                return await self.client.http.account_oauth_grant(
                    auth='basic {0}'.format(self.switch_token),
                    data=payload,
                    priority=priority
                )
            except fortnitepy.HTTPException as e:
                m = 'errors.com.epicgames.account.oauth.authorization_pending'
                if e.message_code != m:
                    raise
            await asyncio.sleep(3)

    async def client_authenticate(self, priority: int = 0) -> dict:
        payload = {
            'grant_type': 'client_credentials',
            'token_type': 'eg1'
        }
        return await self.client.http.account_oauth_grant(
            auth='basic {0}'.format(self.switch_token),
            data=payload,
            priority=priority
        )

    async def switch_authenticate(self, priority: int = 0) -> dict:
        data = await self.client_authenticate(priority=priority)
        self._update_client_data(data)

        device_code = await self.get_device_code(priority=priority)
        self._device_code = device_code['device_code']
        text = 'Please confirm authorization in {0}'.format(device_code['verification_uri_complete'])
        await aprint(text, loop=self.client.loop)
        
        future = asyncio.ensure_future(self.wait_device_authorization(self._device_code, priority=priority))

        return await asyncio.wait_for(future, self.timeout)

    async def ios_authenticate(self, priority: int = 0) -> dict:
        data = await self.switch_authenticate(priority=priority)
        self._update_switch_data(data)

        code = await self.get_exchange_code(
            auth=self.switch_authorization,
            priority=priority
        )
        data = await self.exchange_code_for_session(
            self.ios_token,
            code,
            priority=priority
        )
        return data

    async def authenticate(self, priority: int = 0) -> None:
        data = await self.ios_authenticate(priority=priority)
        self._update_ios_data(data)

        code = await self.get_exchange_code(priority=priority)
        data = await self.exchange_code_for_session(
            self.fortnite_token,
            code,
            priority=priority
        )
        self._update_data(data)


class SessionIDAuth(fortnitepy.ExchangeCodeAuth):
    def __init__(self, session_id: fortnitepy.auth.StrOrMaybeCoro,
                 **kwargs: Any) -> None:
        super().__init__(session_id, **kwargs)

    async def fetch_xsrf_token(self) -> str:
        response = await self.client.http.epicgames_get_csrf()
        return response.cookies['XSRF-TOKEN'].value

    async def set_session_id(self, sid: str, priority: int = 0) -> str:
        r = fortnitepy.http.EpicGames('/id/api/set-sid')
        return await self.client.http.get(
            r,
            params={'sid': sid},
            priority=priority
        )

    async def ios_authenticate(self) -> dict:
        self.resolved_code = await self.resolve(self.code)

        try:
            await self.set_session_id(self.resolved_code)
        except fortnitepy.HTTPException as e:
            m = 'errors.com.epicgames.accountportal.session_id_invalid'
            if e.message_code == m:
                raise fortnitepy.AuthException(
                    'Invalid session id supplied',
                    e
                ) from e

            raise

        fortnitepy.auth.log.info('Fetching valid xsrf token.')
        token = await self.fetch_xsrf_token()
        await self.client.http.epicgames_reputation(token)

        fortnitepy.auth.log.info('Fetching exchange code.')
        data = await self.client.http.epicgames_get_exchange_data(token)

        data = await self.exchange_code_for_session(
            self.ios_token,
            data['code']
        )
        return data
