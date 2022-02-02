import logging
from ..common.common import SectionHandler


class DocumentReferences(SectionHandler):
    def __init__(self):
        super().__init__()

    def _process_mandatory_elements(self, root_element):

        references = []

        for reference in root_element.Reference:
            ref_csaf = {'summary': reference.Description.text,
                        'url': reference.URL.text}

            if reference.attrib.get('Type'):
                ref_csaf['category'] = reference.attrib['Type'].lower()
            else:  # TODO: is this really needed here? `category` fields is not mandatory in CSAF
                ref_csaf['category'] = 'external'  # default behaviour

            references.append(ref_csaf)

        self.csaf = references

    def _process_optional_elements(self, root_element):
        pass
