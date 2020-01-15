import hashlib
import urllib.parse
from unittest import TestCase

from dict2anki.net import *
from dict2anki.utils import Log, get_tag

TAG = get_tag(__name__)

Log.level = Log.DEBUG

URL_CAMBRIDGE_QUERY = 'https://dictionary.cambridge.org/zhs/%E6%90%9C%E7%B4%A2/direct/?datasetsearch=english-chinese' \
                      '-simplified&q={}'

URL_DEBIAN_CD_PATH = 'https://cdimage.debian.org/debian-cd/current/amd64/iso-cd/{}'


class TestNet(TestCase):
    def test_urlopen_with_retry(self):
        url = URL_CAMBRIDGE_QUERY.format(urllib.parse.quote('cater to'))
        with urlopen_with_retry(url, fake_headers()) as response:
            Log.d(TAG, 'headers={}'.format(response.headers))
            Log.d(TAG, 'status={}, url={}'.format(response.status, response.url))

    def test_url_get_content(self):
        Log.d(TAG, url_get_content(URL_DEBIAN_CD_PATH.format('MD5SUMS'), fake_headers()))

    def test_url_save_guess_file(self):
        md5, file = url_get_content(URL_DEBIAN_CD_PATH.format('MD5SUMS'), fake_headers()).splitlines()[0].split()
        Log.d(TAG, 'md5={}, file={}'.format(md5, file))
        self.assertEqual(file, url_save_guess_file(URL_DEBIAN_CD_PATH.format(file))[0])

    def test_url_save(self):
        md5, file = url_get_content(
            URL_DEBIAN_CD_PATH.format('MD5SUMS'),
            fake_headers()
        ).splitlines()[0].split()
        Log.d(TAG, 'md5={}, file={}'.format(md5, file))
        file_actual, size = url_save(
            URL_DEBIAN_CD_PATH.format(file),
            reporthook=lambda a, b: Log.d(TAG, '{:>5}% downloaded'.format(round(a * 100 / b, 1)))
        )
        Log.d(TAG, 'file size: {} MiB'.format(round(size / 1024 / 1024, 1)))
        md5_actual = hashlib.md5()
        with open(file_actual, 'rb') as f:
            buffer = f.read(512 * 1024)
            while buffer:
                md5_actual.update(buffer)
                buffer = f.read(512 * 1024)
        self.assertEqual(md5, md5_actual.hexdigest())
