from setuptools import setup

with open('README.md', 'r', encoding='utf8') as f:
    long_description = f.read()

setup(
    name='dict2anki',
    version='0.2.8',
    author='Binbin Qian',
    author_email='qianbinbin@hotmail.com',
    url='https://github.com/qianbinbin/dict2anki',
    description='dict2anki is a tool converting words to Anki cards.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=['dict2anki', 'dict2anki.extractors'],
    entry_points={
        'console_scripts': [
            'dict2anki = dict2anki.__main__:main'
        ]
    },
    python_requires='>=3.5',
)
