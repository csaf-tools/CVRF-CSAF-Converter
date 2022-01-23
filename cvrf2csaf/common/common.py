import logging
from .utils import critical_exit


class SectionHandler:
    """
    A class encapsulating arbitrary XML element in the tree.
    After conversion, it holds the JSON structure of its whole subtree.

    Attributes:
        csaf     The CSAF interpretation of the data, to be converted to JSON in the final composition step
    """

    def __init__(self, config=None):
        self.csaf = {}
        self.config = config

    def _process_mandatory_elements(self, root_element):
        raise NotImplementedError('Subclasses must implement.')

    def _process_optional_elements(self, root_element):
        raise NotImplementedError('Subclasses must implement.')

    def create_csaf(self, root_element):
        try:
            self._process_mandatory_elements(root_element)
        except Exception as e:
            logging.error(f'Something went wrong when processing mandatory elements for {root_element.tag}. Reason: {e}')

        try:
            self._process_optional_elements(root_element)
        except Exception as e:
            logging.error(f'Something went wrong when processing optional elements for {root_element.tag}. Reason: {e}')

    def _critical_exit(self, msg, status_code=1):
        """ A wrapper around generic critical_exit function, just adding the class name to the message """
        critical_exit(f'{self.__class__.__name__}: {msg}', status_code)
