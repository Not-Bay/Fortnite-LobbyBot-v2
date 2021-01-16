# -*- coding: utf-8 -*-
from collections import UserString
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .bot import Bot


class LocalizedText(UserString):
    def __init__(self, bot: 'Bot', key: str, default: str,
                 *args: tuple, add: Optional[list] = None, **kwargs: dict) -> None:
        self.bot = bot
        self.key = key
        self.default = default
        self.add = add or [self]
        self.args = args
        self.kwargs = kwargs
        text = self.get_text()
        super().__init__(text)

    def text(self) -> str:
        return self.bot.get_dict_key_default(
            self.bot.localize,
            self.key,
            self.default or str(self.key)
        ).format(*self.args, **self.kwargs)

    def get_text(self) -> str:
        return ''.join([
            ((a.text() if a is self else a.get_text())
             if isinstance(a, self.__class__) else
             a)
            for a in self.add
        ])

    def __str__(self):
        self.data = self.get_text()
        return super().__str__()
    def __repr__(self):
        self.data = self.get_text()
        return super().__repr__()
    def __int__(self):
        self.data = self.get_text()
        return super().__int__()
    def __float__(self):
        self.data = self.get_text()
        return super().__float__()
    def __complex__(self):
        self.data = self.get_text()
        return super().__complex__
    def __hash__(self):
        self.data = self.get_text()
        return super().__hash__()
    def __getnewargs__(self):
        self.data = self.get_text()
        return super().__getnewargs__()
    def __eq__(self, string):
        self.data = self.get_text()
        return super().__eq__(string)
    def __lt__(self, string):
        self.data = self.get_text()
        return super().__lt__(string)
    def __le__(self, string):
        self.data = self.get_text()
        return super().__le__(string)
    def __gt__(self, string):
        self.data = self.get_text()
        return super().__gt__(string)
    def __ge__(self, string):
        self.data = self.get_text()
        return super().__ge__(string)
    def __contains__(self, char):
        self.data = self.get_text()
        return super().__contains__(char)
    def __len__(self):
        self.data = self.get_text()
        return super().__len__()
    def __getitem__(self, index):
        self.data = self.get_text()
        return self.data[index]
    def __add__(self, other):
        return self.__class__(
            self.bot,
            self.key,
            self.default,
            *self.args,
            add=[*self.add, other],
            **self.kwargs
        )
    def __radd__(self, other):
        return self.__class__(
            self.bot,
            self.key,
            self.default,
            *self.args,
            add=[other, *self.add],
            **self.kwargs
        )
    def __mul__(self):
        self.data = self.get_text()
        return super().__mul__()
    __rmul__ = __mul__
    def __mod__(self):
        self.data = self.get_text()
        return super().__mod__()
    def __rmod__(self):
        self.data = self.get_text()
        return super().__rmod__()
