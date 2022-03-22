# pylint: disable=too-few-public-methods
from ..common.common import SectionHandler


class DocumentPublisher(SectionHandler):
    type_category_mapping = {
        'Vendor': 'vendor',
        'Coordinator': 'coordinator',
        'User': 'user',
        'Discoverer': 'discoverer',
        'Other': 'other',
    }

    def __init__(self, config):
        super().__init__()
        self.name = config.get('publisher_name')
        self.namespace = config.get('publisher_namespace')

    def _process_mandatory_elements(self, root_element):
        self.csaf['name'] = self.name
        self.csaf['namespace'] = self.namespace
        self.csaf['category'] = self.type_category_mapping[root_element.attrib['Type']]

    def _process_optional_elements(self, root_element):
        # optional values
        if hasattr(root_element, 'ContactDetails'):
            self.csaf['contact_details'] = root_element.ContactDetails.text
        if hasattr(root_element, 'IssuingAuthority'):
            self.csaf['issuing_authority'] = root_element.IssuingAuthority.text
