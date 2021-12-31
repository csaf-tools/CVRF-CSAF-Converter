import logging


class SectionHandler:
    """
    A class encapsulating arbitrary XML element in the tree.
    After conversion, it holds the JSON structure of its whole subtree.
    """

    def __init__(self):
        self.json = {}

    def _process_mandatory_elements(self, root_element):
        raise NotImplementedError('Subclasses must implement.')

    def _process_optional_elements(self, root_element):
        raise NotImplementedError('Subclasses must implement.')

    def create_json(self, root_element):
        try:
            self._process_mandatory_elements(root_element)
        except Exception as e:
            logging.error(f'Something went wrong when processing mandatory elements for {root_element.tag}. Reason: {e}')

        try:
            self._process_optional_elements(root_element)
        except Exception as e:
            logging.error(f'Something went wrong when processing optional elements for {root_element.tag}. Reason: {e}')
