import importlib
from typing import Any, Union

import aiohttp

fortnitepy = importlib.import_module('fortnitepy')


class HTTPClient:
    def __init__(self, session: aiohttp.ClientSession) -> None:
        self.session = session

    async def close(self) -> None:
        await self.session.close()

    async def request(self, method: str, *args: Any, **kwargs: Any) -> Union[str, dict]:
        async with self.session.request(method, *args, **kwargs) as response:
            return await fortnitepy.http.HTTPClient.json_or_text(response)

    async def get(self, *args: Any, **kwargs: Any) -> Union[str, dict]:
        return await self.request('GET', *args, **kwargs)

    async def post(self, *args: Any, **kwargs: Any) -> Union[str, dict]:
        return await self.request('POST', *args, **kwargs)
