from typing import Any

from fortnitepy.http import EpicGames
from fortnitepy.auth import *


class SessionIDAuth(ExchangeCodeAuth):
    def __init__(self, sid: StrOrMaybeCoro,
                 **kwargs: Any) -> None:
        super().__init__(sid, **kwargs)

    async def fetch_xsrf_token(self) -> str:
        response = await self.client.http.epicgames_get_csrf()
        return response.cookies['XSRF-TOKEN'].value

    async def set_sid(self, sid: str, priority: int = 0) -> str:
        r = EpicGames('/id/api/set-sid')
        return await self.client.http.get(
            r,
            params={'sid': sid},
            priority=priority
        )

    async def ios_authenticate(self) -> dict:
        self.resolved_code = await self.resolve(self.code)

        try:
            await self.set_sid(self.resolved_code)
        except HTTPException as e:
            m = 'errors.com.epicgames.accountportal.session_id_invalid'
            if e.message_code == m:
                raise AuthException(
                    'Invalid session id supplied',
                    e
                ) from e

            raise

        log.info('Fetching valid xsrf token.')
        token = await self.fetch_xsrf_token()
        await self.client.http.epicgames_reputation(token)

        log.info('Fetching exchange code.')
        data = await self.client.http.epicgames_get_exchange_data(token)

        data = await self.exchange_code_for_session(
            self.ios_token,
            data['code']
        )
        return data
