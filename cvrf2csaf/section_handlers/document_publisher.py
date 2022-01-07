
from ..common.common import SectionHandler


class DocumentPublisher(SectionHandler):
    def __init__(self, name, namespace):
        super().__init__()
        self.name = name
        self.namespace = namespace

    def _process_mandatory_elements(self, root_element):
        self.csaf['name'] = self.name
        self.csaf['namespace'] = self.namespace
        self.csaf['category'] = root_element.attrib['Type']

    def _process_optional_elements(self, root_element):
        # optional values
        if hasattr(root_element, 'ContactDetails'):
            self.csaf['contact_details'] = root_element.ContactDetails.text
        if hasattr(root_element, 'IssuingAuthority'):
            self.csaf['issuing_authority'] = root_element.IssuingAuthority.text

