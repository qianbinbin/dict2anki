import os
from abc import ABCMeta, abstractmethod
from typing import Tuple, List

from dict2anki.utils import valid_path, Log, get_tag

__all__ = [
    'WordNotFoundError', 'ExtractError', 'CardExtractor',
]

TAG = get_tag(__name__)

DEFAULT_OUT_PATH = os.path.join(os.curdir, TAG)
DEFAULT_MEDIA_FOLDER = 'collection.media'
DEFAULT_FRONT_TEMPLATE_FILE = 'front_template.txt'
DEFAULT_BACK_TEMPLATE_FILE = 'back_template.txt'
DEFAULT_STYLING_FILE = 'styling.txt'
DEFAULT_CARDS_FILE = 'cards.txt'

DEFAULT_FRONT_TEMPLATE = '''{{正面}}'''

DEFAULT_BACK_TEMPLATE = '''{{FrontSide}}
<hr id=answer>
{{背面}}'''

DEFAULT_STYLING = '''.card {
 font-family: arial;
 font-size: 20px;
 text-align: left;
 color: black;
 background-color: white;
}
'''


class WordNotFoundError(Exception):
    pass


class ExtractError(Exception):
    pass


class CardExtractor(metaclass=ABCMeta):

    def __init__(self, out_path: str = DEFAULT_OUT_PATH, media_folder: str = DEFAULT_MEDIA_FOLDER,
                 front: str = DEFAULT_FRONT_TEMPLATE_FILE, back: str = DEFAULT_BACK_TEMPLATE_FILE,
                 styling: str = DEFAULT_STYLING_FILE, cards: str = DEFAULT_CARDS_FILE):
        self.out_path = out_path
        self.media_path = os.path.join(out_path, media_folder)
        self.front_template_file = os.path.join(out_path, front)
        self.back_template_file = os.path.join(out_path, back)
        self.styling_file = os.path.join(out_path, styling)
        self.cards_file = os.path.join(out_path, cards)
        self._front_template = DEFAULT_FRONT_TEMPLATE
        self._back_template = DEFAULT_BACK_TEMPLATE
        self._styling = DEFAULT_STYLING

    def generate_front_template(self):
        Log.i(TAG, 'generating front template')
        ftf = valid_path(self.front_template_file)
        with open(ftf, 'w', encoding='utf8') as fp:
            fp.write(self._front_template)
        Log.i(TAG, 'generated front template to: {}'.format(ftf))

    def generate_back_template(self):
        Log.i(TAG, 'generating back template')
        btf = valid_path(self.back_template_file)
        with open(btf, 'w', encoding='utf8') as fp:
            fp.write(self._back_template)
        Log.i(TAG, 'generated back template to: {}'.format(btf))

    def generate_styling(self):
        Log.i(TAG, 'generating styling')
        sf = valid_path(self.styling_file)
        with open(sf, 'w', encoding='utf8') as fp:
            fp.write(self._styling)
        Log.i(TAG, 'generated styling to: {}'.format(sf))

    def generate_cards(self, *words: str):
        Log.i(TAG, 'trying to generate {} cards'.format(len(words)))
        visited = set()
        skipped = []
        cf = valid_path(self.cards_file)
        with open(cf, 'a', encoding='utf8') as fp:
            for word in words:
                if word in visited:
                    Log.i(TAG, 'skipping duplicate: "{}"'.format(word))
                    continue
                try:
                    actual, fields = self.get_card(word)
                except Exception as e:
                    Log.e(TAG, e)
                    skipped.append(word)
                    Log.w(TAG, 'skipped: "{}"'.format(word))
                else:
                    if fp.tell():
                        fp.write('\n')
                    fp.write('\t'.join(fields))
                    visited.add(word)
                    visited.add(actual)
        if skipped:
            Log.w(TAG, 'skipped {} words:\n'.format(len(skipped)) + '\n'.join(skipped))
        Log.i(TAG, 'generated {} cards to: {}'.format(len(words) - len(skipped), cf))

    @abstractmethod
    def get_card(self, word: str) -> Tuple[str, List[str]]:
        pass
