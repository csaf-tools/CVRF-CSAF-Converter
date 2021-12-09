
from src.common.common import SectionHandler


class DocumentTracking(SectionHandler):

    def _process_mandatory_elements(self, root_element):
        self.json['id'] = root_element.Identification.ID.text
        self.json['current_release_date'] = root_element.CurrentReleaseDate.text
        self.json['initial_release_date'] = root_element.InitialReleaseDate.text
        self.json['status'] = root_element.Status.text
        self.json['version'] = root_element.Version.text
        self.json['revision_history'] = []

        for revision in root_element.RevisionHistory.Revision:
            revision_attrs = {}
            revision_attrs['date'] = revision.Date.text
            revision_attrs['number'] = revision.Number.text
            revision_attrs['summary'] = revision.Description.text

            self.json['revision_history'].append(revision_attrs)

    def _process_optional_elements(self, root_element):
        if hasattr(root_element.Identification, 'Alias'):
            aliases = []
            for alias in root_element.Identification.Alias:
                aliases.append(alias.text)

            self.json['aliases'] = aliases

        if hasattr(root_element, 'Generator'):
            # TODO: not sure how to proceed here, since in 1.2, Engine is optional, in 2.0, Engine is required
            pass






# ------------------- LEAF elements/attributes ------------------------

