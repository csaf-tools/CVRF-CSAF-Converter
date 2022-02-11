import logging
from ..common.common import SectionHandler


class References(SectionHandler):
    def __init__(self, config):
        super().__init__()
        self.force_default_category = config.get('force_insert_default_reference_category')

    def _process_mandatory_elements(self, root_element):

        references = []

        for reference in root_element.Reference:
            ref_csaf = {'summary': reference.Description.text,
                        'url': reference.URL.text}

            if reference.attrib.get('Type'):
                ref_csaf['category'] = reference.attrib['Type'].lower()
            elif self.force_default_category:
                ref_csaf['category'] = 'external'
                logging.info('"Type" attribute not present in "Reference" element, using default value "external". '
                             'This can be controlled by "force_insert_default_reference_category" option.')

            references.append(ref_csaf)

        self.csaf = references

    def _process_optional_elements(self, root_element):
        pass
