import logging
from ..common.common import SectionHandler


class AggregateSeverity(SectionHandler):
    def __init__(self):
        super().__init__()

    def _process_mandatory_and_optional(self, root_element):

        logging.warning(f'Not implemented input {self.__class__}. No parser written.')
        # 39 -> To be tested! No example in input for now.
        csaf_dict = dict(
            namespace=root_element.get('Namespace'),
            text=root_element.text,
        )
        self.csaf = csaf_dict

    def _process_mandatory_elements(self, root_element):
        self._process_mandatory_and_optional(root_element=root_element)

    def _process_optional_elements(self, root_element):
        pass
