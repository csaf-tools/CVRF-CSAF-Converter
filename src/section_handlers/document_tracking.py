
from src.common.common import SectionHandler
from utils import get_utc_timestamp


class DocumentTracking(SectionHandler):
    def __init__(self, cvrf2csaf_name, cvrf2csaf_version):
        super().__init__()
        self.cvrf2csaf_name = cvrf2csaf_name
        self.cvrf2csaf_version = cvrf2csaf_version

    def _process_mandatory_elements(self, root_element):
        self.json['id'] = root_element.Identification.ID.text
        self.json['current_release_date'] = root_element.CurrentReleaseDate.text
        self.json['initial_release_date'] = root_element.InitialReleaseDate.text
        self.json['status'] = root_element.Status.text
        # TODO Conformance Clause 5: CVRF CSAF converter
        self.json['version'] = root_element.Version.text

        revison_hisotry = self._proces_revision_history(root_element.RevisionHistory.Revision)
        self.json['revision_history'] = revison_hisotry

        # Generator is set by this Converter
        self.json['generator'] = {}
        self.json['generator']['date'] = get_utc_timestamp()
        self.json['generator']['engine'] = {}
        self.json['generator']['engine']['name'] = self.cvrf2csaf_name
        self.json['generator']['engine']['version'] = self.cvrf2csaf_version


    def _proces_revision_history(self, revisions):
        # TODO Conformance Clause 5: CVRF CSAF converter
        revision_history = []
        for revision in revisions:
            revision_attrs = {}
            revision_attrs['date'] = revision.Date.text
            revision_attrs['number'] = revision.Number.text
            revision_attrs['summary'] = revision.Description.text

            revision_history.append(revision_attrs)

        return revision_history



    def _process_optional_elements(self, root_element):
        if hasattr(root_element.Identification, 'Alias'):
            aliases = []
            for alias in root_element.Identification.Alias:
                aliases.append(alias.text)

            self.json['aliases'] = aliases

