
class SectionHandler:
    """
    A class encapsulating arbitrary XML element in the tree.
    After conversion, it holds the JSON structure of its whole subtree.
    """
    def __init__(self):
        self.json = {}

    # Subclasses must implement
    def _process_mandatory_elements(self, root_element):
        raise NotImplemented

    # Subclasses must implement
    def _process_optional_elements(self, root_element):
        raise NotImplemented

    def create_json(self, root_element):
        try:
            self._process_mandatory_elements(root_element)
        except Exception as e:
            # TODO: logger
            print(f'Something went wrong when processing mandatory elements for {root_element}. Reason: {e}')

        try:
            self._process_optional_elements(root_element)
        except Exception as e:
            # TODO: logger
            print(f'Something went wrong when processing optional elements for {root_element}. Reason: {e}')


