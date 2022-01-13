
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

        self.csaf['names'] = names
        self.csaf['organization'] = organization
        self.csaf['summary'] = summary
        self.csaf['urls'] = urls
