import argparse
import os
import socket
import sys

from .extractors import EXTRACTORS, DEFAULT_EXTRACTOR
from .utils import get_tag, Log

TAG = get_tag(__name__)

extractor = None

output_path = None

words = []

DEFAULT_TIME_OUT = 20


def parse_args():
    parser = argparse.ArgumentParser(
        prog='dict2anki',
        usage='dict2anki [OPTION]...',
        description='A tool converting words to cards for Anki to import.',
        add_help=False,
    )
    parser.add_argument(
        '-h', '--help', action='store_true',
        help='Print this help message and exit.'
    )
    parser.add_argument(
        '-i', '--input-file', metavar='FILE', type=argparse.FileType('r'),
        help='Read words from FILE, split by lines. Lines starting with "#" will be ignored.'
    )
    parser.add_argument(
        '-o', '--output-path', metavar='PATH', help='Set output path.'
    )
    parser.add_argument(
        '-e', '--extractor', metavar='DICT',
        help='Available extractors: {}.'.format(list(EXTRACTORS.keys()))
    )
    parser.add_argument(
        '-d', '--debug', action='store_true',
        help='Show debug info.'
    )
    args = parser.parse_args()

    if args.debug:
        Log.level = Log.DEBUG
    if not args.input_file:
        Log.e(TAG, 'no input file specified')
        parser.print_help()
        sys.exit(2)

    if args.extractor and args.extractor not in EXTRACTORS:
        Log.e(TAG, 'unknown extractor: {}'.format(args.extractor))
        parser.print_help()
        sys.exit(2)
    global extractor
    if args.extractor:
        extractor = args.extractor
    else:
        Log.i(TAG, 'no extractor specified, using default: {}'.format(DEFAULT_EXTRACTOR))
        extractor = DEFAULT_EXTRACTOR

    global output_path
    output_path = os.path.join(args.output_path if args.output_path else os.curdir, extractor)

    global words
    Log.d(TAG, 'loading words from {}'.format(args.input_file.name))
    for word in args.input_file.read().splitlines():
        word = word.strip()
        if word and not word.startswith('#'):
            words.append(word)
    args.input_file.close()
    Log.d(TAG, '{} words loaded'.format(len(words)))


def main():
    parse_args()

    socket.setdefaulttimeout(DEFAULT_TIME_OUT)

    global extractor
    e = EXTRACTORS[extractor](output_path)
    e.generate_front_template()
    e.generate_back_template()
    e.generate_styling()
    e.generate_cards(*words)
