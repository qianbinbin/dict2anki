import mimetypes
import os
import re
import socket
import urllib
import urllib.parse
import zlib
from http.client import HTTPResponse
from typing import Union, Tuple, Optional, Dict
from urllib.request import Request, urlopen

from .utils import valid_path, get_tag, Log

__all__ = [
    'fake_headers', 'urlopen_with_retry', 'url_get_content', 'url_save', 'url_save_guess_file',
]

TAG = get_tag(__name__)


def fake_headers() -> Dict[str, str]:
    return {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Charset': 'utf-8,*;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'utf-8, *;q=0.5',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/76.0.3809.132 Safari/537.36',
    }


def urlopen_with_retry(url: Union[str, Request],
                       headers: Dict[str, str] = None,
                       retry: int = 5,
                       **kwargs) -> HTTPResponse:
    Log.d(TAG, 'urlopen: url={}, headers={}, retry={}, kwargs={}'.format(url, headers, retry, kwargs))
    if isinstance(url, str):
        url = Request(url)
    if headers:
        url.headers = headers
    for i in range(1, retry + 1):
        try:
            return urlopen(url, **kwargs)
        except socket.timeout as e:
            Log.i(TAG, 'urlopen attempt {} timeout'.format(i))
            if i == retry:
                raise e
        except Exception as e:
            Log.w(TAG, 'urlopen error: {}'.format(e))
            if i == retry:
                raise e


def url_get_content(url: Union[str, Request, HTTPResponse],
                    headers: Dict[str, str] = None,
                    retry: int = 5,
                    **kwargs) -> Union[bytes, str]:
    Log.d(TAG, 'get content, url={}, headers={}, retry={}, kwargs={}'.format(url, headers, retry, kwargs))
    response = url if isinstance(url, HTTPResponse) else urlopen_with_retry(url, headers, retry, **kwargs)
    data = response.read()

    content_encoding = response.headers['Content-Encoding']
    if content_encoding == 'gzip':
        data = zlib.decompress(data, zlib.MAX_WBITS | 16)
    elif content_encoding == 'deflate':
        try:
            data = zlib.decompress(data)
        except zlib.error:
            Log.w(TAG, 'cannot decompress, treat as deflate data')
            data = zlib.decompress(data, -zlib.MAX_WBITS)
    elif content_encoding:
        raise NotImplementedError('unknown encoding: {}'.format(content_encoding))

    charset = None
    content_type = response.headers['Content-Type']
    if content_type:
        m = re.search(r'charset=([\w-]+)', content_type)
        if m:
            charset = m.group(1)
            Log.d(TAG, 'charset={}'.format(charset))
    return data.decode(charset) if charset else data.decode('utf-8', 'ignore')


def url_save_guess_file(url: Union[str, Request],
                        headers: Dict[str, str] = None,
                        retry: int = 5,
                        **kwargs) -> Tuple[str, Optional[int]]:
    Log.d(TAG, 'guess file, url={}, headers={}, retry={}, kwargs={}'.format(url, headers, retry, kwargs))
    name, size = None, None
    with urlopen_with_retry(url, headers, retry, **kwargs) as response:
        if response.headers['Content-Disposition']:
            m = re.search(r'filename="(.+)"', response.headers['Content-Disposition'])
            if m:
                name = m.group(1)
        if not name:
            name = urllib.parse.unquote(os.path.basename(urllib.parse.urlparse(response.geturl()).path))
            if not name:
                name = 'file'
                ext = mimetypes.guess_extension(response.headers['Content-Type'].rsplit(';', 1)[0])
                if ext:
                    name += ext
        if response.headers['Content-Length']:
            size = int(response.headers['Content-Length'])
    Log.d(TAG, 'guess file, name={}, size={}'.format(name, size))
    return name, size


def url_save(url: Union[str, Request],
             headers: Dict[str, str] = None,
             filename: str = None,
             force: bool = False,
             reporthook=None,
             **kwargs) -> Tuple[str, int]:
    Log.d(TAG, 'url save, url={}, headers={}, filename={}, force={}, reporthook={}, kwargs={}'.format(
        url, headers, filename, force, reporthook, kwargs))
    if isinstance(url, str):
        url = Request(url)
    if headers:
        url.headers = headers
    else:
        headers = url.headers

    name, total_size = url_save_guess_file(url, **kwargs)
    if total_size is None:
        total_size = float('inf')
    if filename is None:
        filename = os.path.join(os.curdir, name)
    filename = valid_path(filename, force)

    mode = 'wb'
    part_file = filename + '.part' if total_size != float('inf') else filename
    part_size = 0
    if os.path.exists(part_file):
        part_size = os.path.getsize(part_file)
        if 0 < part_size < total_size:
            Log.i(TAG, '\'.part\' file already exists: {}, trying to append'.format(part_file))
            mode = 'ab'
        else:
            part_size = 0

    if part_size < total_size:
        if part_size:
            headers['Range'] = 'bytes={}-'.format(part_size)
        response = urlopen_with_retry(url, **kwargs)
        remaining_size = float('inf')
        if response.headers['Content-Range']:
            m = re.search(r'(\d+)-(\d+)/(\d+)$', response.headers['Content-Range'])
            remaining_size = int(m.group(3)) - int(m.group(1))
        elif response.headers['Content-Length']:
            remaining_size = int(response.headers['Content-Length'])
        if part_size + remaining_size != total_size:
            Log.i(TAG, '\'.part\' file inconsistent with server, retrieving')
            part_size = 0
            mode = 'wb'

        with open(part_file, mode) as f:
            bs = 512 * 1024
            while part_size < total_size:
                buffer = None
                try:
                    buffer = response.read(bs)
                except socket.timeout:
                    Log.i(TAG, 'timeout during downloading, retrying')
                if buffer:
                    f.write(buffer)
                    part_size += len(buffer)
                    if reporthook:
                        reporthook(part_size, total_size)
                else:
                    if part_size >= total_size or total_size == float('inf'):
                        break
                    headers['Range'] = 'bytes={}-'.format(part_size)
                    response = urlopen_with_retry(url, **kwargs)
    assert part_size == os.path.getsize(part_file)
    if part_file != filename:
        if os.access(filename, os.W_OK):
            os.remove(filename)
        os.rename(part_file, filename)
    Log.d(TAG, 'url save completed, file={}, size={}'.format(filename, part_size))
    return filename, part_size
