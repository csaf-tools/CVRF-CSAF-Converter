import logging
from ..common.common import SectionHandler


class DocumentCategory(SectionHandler):
    def __init__(self):
        super().__init__()

    def _process_mandatory_elements(self, root_element):
        self.csaf = root_element.text

    def _process_optional_elements(self, root_element):
        # Not used
        pass
