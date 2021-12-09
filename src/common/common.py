
class SectionHandler:
    def __init__(self):
        self.json = {}

    # Subclasses must implement
    def _process_mandatory_elements(self, root_element):
        raise NotImplemented

    # Subclasses must implement
    def _process_optional_elements(self, root_element):
        raise NotImplemented

    def create_json(self, root_element):
        self._process_mandatory_elements(root_element)
        self._process_optional_elements(root_element)

