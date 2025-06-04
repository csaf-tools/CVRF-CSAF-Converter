""" Module containing Acknowledgments class """
import logging
from ..common.common import SectionHandler


# pylint: disable=too-few-public-methods
class Acknowledgments(SectionHandler):
    """ Responsible for converting the Acknowledgments sections:
      - /cvrf:cvrfdoc/cvrf:Acknowledgments
      - /cvrf:cvrfdoc/vuln:Vulnerability[i+1]/vuln:Acknowledgments
    """
    # pylint: disable=useless-super-delegation
    def __init__(self):
        super().__init__()

    def _process_mandatory_elements(self, root_element):

        if hasattr(root_element, 'Acknowledgment'):
            # at least one entry in list of Acknowledgments
            pass  # No field is mandatory due to CVRF.xsd; version 1.2

    def _process_optional_elements(self, root_element):
        self.csaf = []

        for ack in root_element.Acknowledgment:
            # empty Acknowledgment slips CVRF input validation
            if not any([hasattr(ack, 'Name'),
                        hasattr(ack, 'Organization'),
                        hasattr(ack, 'Description'),
                        hasattr(ack, 'URL')]):
                logging.warning('Skipping empty Acknowledgment entry, input line: %s',
                                ack.sourceline)
                continue

            ack_elem = {}

            if hasattr(ack, 'Organization'):
                if len(ack.Organization) > 1:
                    # If more than one cvrf:Organization instance is given,
                    # the CVRF CSAF converter converts the first one into the organization.
                    # In addition, the converter outputs a warning that information might be lost
                    # during conversion of document or vulnerability acknowledgment.
                    logging.warning('CSAF 2.0 allows only one organization inside Acknowledgments. '
                                    'Taking the first occurrence, ignoring: %s.',
                                    ack.Organization[1:])

                ack_elem['organization'] = ack.Organization[0].text

            if hasattr(ack, 'Description'):
                # Single Description elem is asserted on the input
                ack_elem['summary'] = ack.Description[0].text

            # Names and URLs can have more entries
            if hasattr(ack, 'Name'):
                ack_elem['names'] = [x.text for x in ack.Name]

            if hasattr(ack, 'URL'):
                ack_elem['urls'] = [x.text for x in ack.URL]

            self.csaf.append(ack_elem)
