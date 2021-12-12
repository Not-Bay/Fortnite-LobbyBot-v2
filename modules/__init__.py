# -*- coding: utf-8 -*-
"""
MIT License

Copyright (c) 2020-2021 gomashio1596

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import io

from .auto_updater import __version__
from .bot import *
from .colors import init, red

init()


class MyStream(io.StringIO):
    def __init__(self, original: io.IOBase, func: Optional[Callable] = None) -> None:
        self.original = original
        self.func = func if func is not None else (lambda x: x)
        super().__init__()

    def write(self, s: str) -> int:
        s = self.func(s)
        print(s, end='', file=self.original)
        return super().write(s)

    def read(self, size: Optional[int] = -1) -> str:
        self.seek(0)
        return super().read(size)


sys.stdout = MyStream(sys.stdout)
sys.stderr = MyStream(sys.stderr, red)
