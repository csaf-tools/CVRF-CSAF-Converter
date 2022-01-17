import logging
from ..common.common import SectionHandler


class Acknowledgments(SectionHandler):
    def __init__(self):
        super().__init__()

    def _process_mandatory_elements(self, root_element):

        if hasattr(root_element, 'Acknowledgment'):
            # at least one entry in list of Acknowledgments
            pass # No field is mandatory due to CVRF.xsd; version 1.2


    def _process_optional_elements(self, root_element):
        # optional values
        names = []
        organization = []
        summary = []
        urls = []
        for ack in root_element.Acknowledgment:
            names.append(ack.Name.text)
            if hasattr(ack, 'Organization'):
                organization.append(ack.Organization.text)
            if hasattr(ack, 'Summary'):
                summary.append(ack.Summary.text)
            if hasattr(ack, 'Url'):
                urls.append(ack.Url.text)

        if len(organization)>=1:
            # If more than one cvrf:Organization instance is given,
            # the CVRF CSAF converter converts the first one into the organization.
            # In addition the converter outputs a warning that information might be lost during conversion of document or vulnerability acknowledgment.
            self.csaf['organization'] = organization[0]
            if len(organization) > 1:
                logging.warn(f'Due to CSAF 2.0 standard, only the first organization can be acknowledged. '
                             f'{len(organization)-1} are not mentioned in the output.')
        if len(names) > 0:
            self.csaf['names'] = names
        if len(summary) > 0:
            self.csaf['summary'] = summary
        if len(urls) > 0:
            self.csaf['urls'] = urls
