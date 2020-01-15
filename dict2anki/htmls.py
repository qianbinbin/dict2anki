import re
from typing import Optional, Iterator, Tuple

from .utils import get_tag, Log

__all__ = [
    'find_positions', 'findall', 'find', 'sub', 'removeall',
]

TAG = get_tag(__name__)


def find_positions(html_str: str, tag: str, attrib: str = '', hook=None) -> Iterator[Tuple[int, int]]:
    open_tag = re.compile(r'<{}(?:\s*?|\s[\s\S]*?)>'.format(tag))
    close_tag = re.compile(r'</{}\s*?>'.format(tag))
    all_tag = re.compile(r'</?{}\s*?>|<{}\s[\s\S]*?>'.format(tag, tag))
    # must match with open_tag first
    start_tag = re.compile(r'<{}[\s\S]*?{}[\s\S]*?>'.format(tag, attrib))
    count = 0
    start = -1
    for m in all_tag.finditer(html_str):
        if open_tag.fullmatch(m.group(0)):
            if start != -1:
                count += 1
            elif start_tag.match(m.group(0)):
                count = 1
                start = m.start()
        elif start != -1 and close_tag.fullmatch(m.group(0)):
            count -= 1
            if count == 0:
                Log.d(TAG, 'paired tags found, start={}, end={}'.format(start, m.end()))
                if hook:
                    hook(start, m.end())
                yield start, m.end()
                start = -1


def findall(html_str: str, tag: str, attrib: str = '') -> Iterator[str]:
    for i, j in find_positions(html_str, tag, attrib):
        yield html_str[i:j]


def find(html_str: str, tag: str, attrib: str = '') -> Optional[str]:
    for e in findall(html_str, tag, attrib):
        return e


def sub(html_str: str, replace, tag: str, attrib: str = ''):
    positions = []
    for i, j in find_positions(html_str, tag, attrib):
        positions.append((i, j))
    while positions:
        i, j = positions.pop()
        Log.d(TAG, 'replacing element: {}'.format(html_str[i:j]))
        html_str = html_str[:i] + replace(html_str[i:j]) + html_str[j:]
    return html_str


def removeall(html_str: str, tag: str, attrib: str = '') -> str:
    return sub(html_str, lambda h: '', tag, attrib)
