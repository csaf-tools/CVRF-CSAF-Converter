""" Module containing DocumentLeafElements class """
import logging

from ..common.common import SectionHandler


# pylint: disable=too-few-public-methods
class DocumentLeafElements(SectionHandler):
    """
    A handler for the document leaf elements which do not have any further children elements
    handling CSAF path: /document
    """

    def __init__(self, config):
        super().__init__()
        self.csaf_version = config.get('csaf_version')

    def _process_mandatory_elements(self, root_element):
        # This element is new in CSAF, not present in CVRF
        self.csaf['csaf_version'] = self.csaf_version

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
                self.csaf['aggregate_severity']['namespace'] = \
                    root_element.AggregateSeverity.attrib['Namespace']

        self._process_xml_lang(root_element)

    def _process_xml_lang(self, root_element):
        langs = list(set(root_element.xpath("//@xml:lang")))
        if len(langs) == 1:
            self.csaf['lang'] = langs[0]
            return

        if len(langs) > 1:
            reason = (f'multiple languages specified in XML: {", ".join(langs)}.'
                      ' A document with multiple languages might have been produced')
        else:
            reason = "no language specified in XML"
        logging.warning("could not determine value for 'lang': %s", reason)
