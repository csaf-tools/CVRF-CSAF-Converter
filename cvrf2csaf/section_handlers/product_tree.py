import logging
from ..common.common import SectionHandler


class ProductTree(SectionHandler):
    def __init__(self):
        super().__init__()

    def _process_mandatory_elements(self, root_element):
        logging.warning(f'Not implemented input {self.__class__}. No parser written.')

    def _process_optional_elements(self, root_element):
        pass
