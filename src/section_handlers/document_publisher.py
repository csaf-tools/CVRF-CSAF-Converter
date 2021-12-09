
from src.common.common import SectionHandler


class DocumentPublisher(SectionHandler):
    def __init__(self, name, namespace):
        super().__init__()
        self.name = name
        self.namespace = namespace

    def _process_mandatory_elements(self, root_element):
        self.json['name'] = self.name
        self.json['namespace'] = self.namespace
        self.json['category'] = root_element.attrib['Type']

    def _process_optional_elements(self, root_element):
        # optional values
        if hasattr(root_element, 'ContactDetails'):
            self.json['contact_details'] = root_element.ContactDetails.text
        if hasattr(root_element, 'IssuingAuthority'):
            self.json['issuing_authority'] = root_element.IssuingAuthority.text

