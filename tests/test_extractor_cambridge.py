from unittest import TestCase

from dict2anki.extractors.cambridge import *
from dict2anki.utils import Log, get_tag

TAG = get_tag(__name__)

Log.level = Log.DEBUG


class TestCambridge(TestCase):
    def test_CambridgeExtractor(self):
        extractor = CambridgeExtractor()
        self.assertEqual('cater for sb sth', extractor.get_card('cater to')[0])
        extractor.generate_front_template()
        extractor.generate_back_template()
        extractor.generate_styling()
        words = (
            'shiiiit',
            'adhere to sth',
            'fulfill',
            'account',
            'list',
            'in terms of',
            'reflect on',
            'abbreviate',
            'chat')
        extractor.generate_cards(*words)
