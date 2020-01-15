from typing import Dict, Type

from .cambridge import *
from .extractor import *

EXTRACTORS: Dict[str, Type[CardExtractor]] = {
    'cambridge': CambridgeExtractor,
}

DEFAULT_EXTRACTOR = 'cambridge'
