#!/usr/bin/env python3

import argparse
import gzip
import logging
import re
import socket
import sys
from io import BytesIO
from typing import List, Tuple, Optional
from urllib import request, error

QUERY = 'https://dictionary.cambridge.org/zhs/' \
        '%E8%AF%8D%E5%85%B8/%E8%8B%B1%E8%AF%AD-%E6%B1%89%E8%AF%AD-%E7%AE%80%E4%BD%93/{}'

STYLE = 'https://dictionary.cambridge.org/zhs/common.css'

HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'utf-8,*;q=0.5',
    'Accept-Encoding': 'gzip',
    'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-TW;q=0.6',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/76.0.3809.132 Safari/537.36',
}

output_file_name = 'anki.txt'

style_file_name = 'style.css'

skipped = []


def urlopen_with_retry(req: request.Request, retry: int = 5):
    for i in range(retry):
        try:
            return request.urlopen(req)
        except Exception as e:
            if isinstance(e, socket.timeout):
                logging.warning('request attempt {} timeout'.format(str(i + 1)))
            else:
                logging.warning('can\'t open url: {}'.format(req.full_url))
                logging.warning(e)
            if i + 1 == retry:
                raise e


def get_source(url: str) -> str:
    logging.debug('url: {}'.format(url))

    req = request.Request(url, headers=HEADERS)
    response = urlopen_with_retry(req)
    data = response.read()
    content_encoding = response.getheader('Content-Encoding')
    logging.debug('Content-Encoding: {}'.format(content_encoding))
    if content_encoding == 'gzip':
        data = gzip.GzipFile(fileobj=BytesIO(data)).read()

    charset = 'UTF-8'
    match = re.search(r'charset=([\w-]+)', response.getheader('Content-Type'))
    if match:
        charset = match.group(1)
    return data.decode(charset, 'ignore')


class ExtractError(Exception):
    pass


def extract_fields(source: str) -> Optional[Tuple[str, str]]:
    try:
        match = re.search(r'(<div class="di-body">[\s\S]*?/div>)<small class', source)
        # body = re.sub(r'>\s+<', r'><', match.group(1))
        body = match.group(1)
        body = body.replace('\n', '')
        match = re.search(r'(<div class="di-title">[\s\S]*?/div>)<div class="posgram', body)
        title = match.group(1)

        # remove titles
        body = re.sub(r'<div class="di-title"[\s\S]*?/div>\s*?<div class="posgram', r'<div class="posgram', body)
        # remove audios
        body = re.sub(r'<span class="daud"[\s\S]*?</span>', r'', body)
        # remove amp-access
        body = re.sub(r'<a amp-access[\s\S]*?</a>', r'', body)
        # remove links
        body = re.sub(r'<a class="query"[\s\S]*?>([\s\S]*?)</a>', r'\g<1>', body)
        body = re.sub(r'<a href=[\s\S]*?>([\s\S]*?)</a>', r'\g<1>', body)
        # remove share
        body = re.sub(r'<div class="pr x lbb lb-cm">([\s\S]*?)</div>\s*?<div class="pos-header dpos-h">',
                      r'<div class="pr x lbb lb-cm"></div><div class="pos-header dpos-h">', body)
        # remove more examples
        body = re.sub(r'<amp-accordion[\s\S]*?</amp-accordion>', r'', body)
        body = re.sub(r'<div class="daccord"[\s\S]*?</div>', r'', body)
        # remove see also
        body = re.sub(r'<div class="xref see_also[\s\S]*?<div[\s\S]*?<div[\s\S]*?</div>[\s\S]*?</div>[\s\S]*?</div>',
                      r'',
                      body)
        # remove js
        body = re.sub(r'<script[\s\S]*?</script>', r'', body)
        return title, body
    except Exception as e:
        raise ExtractError(e)


def append_to_output(fp, columns: Tuple[str, ...]):
    logging.debug('tell: {}'.format(fp.tell()))
    if fp.tell():
        fp.write('\n')
    fp.write('\t'.join(columns))


def get_style_file():
    logging.debug('downloading style file')
    style = get_source(STYLE)
    with open(style_file_name, 'w', encoding='utf8') as fp:
        fp.write(style)
    logging.info('saved style file: {}'.format(style_file_name))


def convert(words: List[str]):
    visited = set()
    with open(output_file_name, 'a', encoding='utf8') as fp:
        for word in words:
            w = word.strip()
            if not w or w in visited:
                logging.info('skipping duplicate: "{}"'.format(w))
                continue
            visited.add(w)

            logging.debug('querying "{}"'.format(w))
            try:
                source = get_source(QUERY.format(w))
                fields = extract_fields(source)
                append_to_output(fp, fields)
                logging.info('added: "{}"'.format(w))
            except Exception as e:
                if isinstance(e, ExtractError):
                    logging.warning('can\'t parse dictionary data of "{}"'.format(w))
                else:
                    logging.error(e)
                logging.warning('skipped: "{}"'.format(w))
                skipped.append(w)


def main():
    parser = argparse.ArgumentParser(
        prog='dict2anki',
        usage='dict2anki [OPTION]...',
        description='A tool converting words to txt file for Anki to import.',
        add_help=False,
    )
    parser.add_argument(
        '-h', '--help', action='store_true',
        help='Print this help message and exit.'
    )
    parser.add_argument(
        '-i', '--input-file', metavar='FILE', type=argparse.FileType('r'),
        help='Read words from FILE, split by lines.'
    )
    parser.add_argument(
        '-s', '--style-file', metavar='FILE', help='Set style file.'
    )
    parser.add_argument(
        '-o', '--output-file', metavar='FILE', help='Set output file.'
    )
    parser.add_argument(
        '-d', '--debug', action='store_true',
        help='Show debug info.'
    )
    args = parser.parse_args()
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.INFO)

    if not args.input_file:
        logging.error('no input file specified')
        parser.print_help()
        sys.exit(2)

    global style_file_name
    if args.style_file:
        style_file_name = args.style_file
    global output_file_name
    if args.output_file:
        output_file_name = args.output_file

    socket.setdefaulttimeout(20)

    get_style_file()

    logging.debug('loading words from {}'.format(args.input_file.name))
    words = args.input_file.read().splitlines()
    args.input_file.close()
    convert(words)
    logging.info('saved anki file: {}'.format(output_file_name))
    if skipped:
        logging.error('skipped {} words:'.format(len(skipped)))
        logging.error('\n'.join(skipped))


if __name__ == '__main__':
    main()
