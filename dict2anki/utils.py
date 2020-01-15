import os
import re
import sys

__all__ = [
    'Log',
    'get_tag', 'valid_path',
]


def get_tag(name: str) -> str:
    return name.rsplit('.', 1)[-1]


TAG = get_tag(__name__)


class Log:
    DEBUG = 1
    INFO = 2
    WARN = 3
    ERROR = 4

    level = INFO

    _TERM = os.getenv('TERM', '')
    _ANSI_TERMINAL = _TERM.startswith('xterm') or _TERM in ('eterm-color', 'linux', 'screen', 'vt100',)

    # https://en.wikipedia.org/wiki/ANSI_escape_code
    _RESET = '0'
    _BOLD = '1'
    _FAINT = '2'
    _ITALIC = '3'
    _UNDERLINE = '4'
    _BLINK = '5'
    _REVERSE = '7'
    _RED = '31'
    _GREEN = '32'
    _YELLOW = '33'
    _BLUE = '34'
    _RED_BG = '41'
    _GREEN_BG = '42'
    _YELLOW_BG = '43'
    _BLUE_BG = '44'

    @staticmethod
    def _sgr_text(msg, *attributes) -> str:
        return '\33[{}m{}\33[{}m'.format(';'.join([color for color in attributes]), msg, Log._RESET)

    @staticmethod
    def _pure_text(msg, *attributes) -> str:
        return str(msg)

    _text = _sgr_text if _ANSI_TERMINAL else _pure_text

    @staticmethod
    def _print(msg, *attributes):
        sys.stderr.write(Log._text('{}\n'.format(msg), *attributes))

    _MSG = '{:<10}: {}'

    @staticmethod
    def d(tag, msg):
        if Log.level <= Log.DEBUG:
            Log._print('D/' + Log._MSG.format(tag, msg))

    @staticmethod
    def i(tag, msg):
        if Log.level <= Log.INFO:
            Log._print('I/' + Log._MSG.format(tag, msg), Log._GREEN)

    @staticmethod
    def w(tag, msg):
        if Log.level <= Log.WARN:
            Log._print('W/' + Log._MSG.format(tag, msg), Log._YELLOW)

    @staticmethod
    def e(tag, msg):
        if Log.level <= Log.ERROR:
            Log._print('E/' + Log._MSG.format(tag, msg), Log._RED)


def valid_path(path: str, force: bool = True) -> str:
    Log.d(TAG, 'valid path, path={}, force={}'.format(path, force))
    dir_name, base_name = os.path.split(path)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name, exist_ok=True)
    base_name = re.sub(r'[/:*?"<>|]', '_', base_name)
    path = os.path.join(dir_name, base_name)
    if force:
        return path
    while os.path.exists(path):
        name, ext = os.path.splitext(base_name)
        # '.txt' -> ('.txt', '')
        # which doesn't make sense
        if not ext:
            name, ext = ext, name
        m = re.search(r'_\(([1-9]\d*)\)$', name)
        if not m:
            name += '_(1)'
        else:
            name = re.sub(r'\(([1-9]\d*)\)$', '(' + str(int(m.group(1)) + 1) + ')', name)
        base_name = name + ext
        path = os.path.join(dir_name, base_name)
    Log.d(TAG, 'valid path, path={}'.format(path))
    return path
