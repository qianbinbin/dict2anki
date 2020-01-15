import re
from unittest import TestCase

from dict2anki import htmls
from dict2anki.utils import Log, get_tag

TAG = get_tag(__name__)

Log.level = Log.DEBUG


class TestHtml(TestCase):
    HTML = '''<html>
    <head>
        <title>Example page</title>
    </head>
    <body>
        <p>Moved to <a href="http://example.org/">example.org</a>
        or <a href="http://example.com/">example.com</a>.</p>
    </body>
</html>'''

    def test_find_positions(self):
        for i, j in htmls.find_positions(self.HTML, 'a', 'href="http://example.org/"'):
            Log.d(TAG, 'i={}, j={}'.format(i, j))

    def test_findall(self):
        for e in htmls.findall(self.HTML, 'a'):
            Log.d(TAG, e)

    def test_find(self):
        self.assertEqual('<a href="http://example.org/">example.org</a>', htmls.find(self.HTML, 'a'))

    def test_sub(self):
        def rm_tag(s):
            return re.sub(r'<[\s\S]*?>([\s\S]*)<[\s\S]*>', r'\g<1>', s)

        Log.d(TAG, htmls.sub(self.HTML, rm_tag, 'a', 'href="http://example.com/"'))

    def test_removeall(self):
        Log.d(TAG, htmls.removeall(self.HTML, 'a'))
