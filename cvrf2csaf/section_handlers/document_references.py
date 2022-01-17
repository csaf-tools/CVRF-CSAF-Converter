import logging
from ..common.common import SectionHandler


class DocumentReferences(SectionHandler):
    def __init__(self):
        super().__init__()

    def _process_mandatory_elements(self, root_element):

        references = []
        if hasattr(root_element, 'Reference'):
            for ref in root_element.Reference:
                ref_csaf = dict()
                if 'Type' not in ref.attrib or len(ref.attrib['Type']) < 2:
                    ref_csaf['category'] = 'external' # default behaviour
                else:
                    ref_csaf['category'] = str(ref.attrib['Type'])

                if ref_csaf['category'] not in ['external', 'self']:
                    logging.warn(f'DocumentReferences->category {ref_csaf["category"]} must be external or self!')

                if hasattr(ref, 'Description'):
                    ref_csaf['summary'] = ref.Description.text
                if hasattr(ref, 'URL'):
                    ref_csaf['url'] = ref.URL.text
                references.append(ref_csaf)

        self.csaf = references

    def _process_optional_elements(self, root_element):
        pass
