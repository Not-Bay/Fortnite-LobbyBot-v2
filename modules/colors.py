# -*- coding: utf-8 -*-
import colorama
from colorama import Fore, Style


def init():
    colorama.init()


def colored(text: str, color: str) -> str:
    return f'{getattr(Fore,color)}{text}{Style.RESET_ALL}'


def blue(text: str) -> str:
    return colored(text, 'BLUE')


def cyan(text: str) -> str:
    return colored(text, 'CYAN')


def green(text: str) -> str:
    return colored(text, 'GREEN')


def magenta(text: str) -> str:
    return colored(text, 'MAGENTA')


def red(text: str) -> str:
    return colored(text, 'RED')


def yellow(text: str) -> str:
    return colored(text, 'YELLOW')
