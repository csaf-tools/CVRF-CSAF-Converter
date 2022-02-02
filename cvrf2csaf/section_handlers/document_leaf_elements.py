import logging
from ..common.common import SectionHandler


class DocumentLeafElements(SectionHandler):
    """
    A handler for the document leaf elements which do not have any further children elements
    handling CSAF path: /document
    """
    def __init__(self, config):
        super().__init__(config)

    def _process_mandatory_elements(self, root_element):
        # This element is new in CSAF, not present in CVRF
        self.csaf['csaf_version'] = self.config.get('csaf_version')

        self.csaf['category'] = root_element.DocumentType.text
        self.csaf['title'] = root_element.DocumentTitle.text

    def _process_optional_elements(self, root_element):
        if hasattr(root_element, 'DocumentDistribution'):
            self.csaf['distribution'] = {
                'text': root_element.DocumentDistribution.text
            }

        if hasattr(root_element, 'AggregateSeverity'):
            self.csaf['aggregate_severity'] = {
                'text': root_element.AggregateSeverity.text
            }
            if root_element.AggregateSeverity.attrib.get('Namespace'):
                self.csaf['aggregate_severity']['namespace'] = root_element.AggregateSeverity.attrib['Namespace']
