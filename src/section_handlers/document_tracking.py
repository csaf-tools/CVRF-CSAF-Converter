import logging
import re

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

        revision_history, version = DocumentTracking._proces_revision_history(root_element)
        self.json['revision_history'] = revision_history
        self.json['version'] = version

        # Generator is set by this Converter
        self.json['generator'] = {}
        self.json['generator']['date'] = get_utc_timestamp()
        self.json['generator']['engine'] = {}
        self.json['generator']['engine']['name'] = self.cvrf2csaf_name
        self.json['generator']['engine']['version'] = self.cvrf2csaf_version

    """
    Checks whether all version numbers in /document/tracking/revision_history match semantic versioning.
    semantic version is defined in version_t definition
    see: https://docs.oasis-open.org/csaf/csaf/v2.0/csd01/csaf-v2.0-csd01.html#3111-version-type and
    section 9.1.5 Conformance Clause 5: CVRF CSAF converter
    """
    @staticmethod
    def check_for_version_t(revision_history):
        pattern = '^((0|[1-9]\\d*)\\.(0|[1-9]\\d*)\\.(0|[1-9]\\d*)(?:-((?:0|[1-9]\\d*|\\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\\.(?:0|[1-9]\\d*|\\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\\+([0-9a-zA-Z-]+(?:\\.[0-9a-zA-Z-]+)*))?)$'
        return all([re.match(pattern, revision['number']) for revision in revision_history])

    @staticmethod
    def _proces_revision_history(root_element):
        # preprocess the data
        revision_history = []
        for revision in root_element.RevisionHistory.Revision:
            revision_attrs = {}
            revision_attrs['date'] = revision.Date.text
            # keep original value in this variable for matching later
            revision_attrs['number_cvrf'] = revision.Number.text
            # this value might be overwritten later if it doesn't match semantic versioning
            revision_attrs['number'] = revision.Number.text
            revision_attrs['summary'] = revision.Description.text

            revision_history.append(revision_attrs)

        # handle corresponding part of Conformance Clause 5: CVRF CSAF converter
        # that is: some of the version number in revision_history don't match semantic versioning
        if not DocumentTracking.check_for_version_t(revision_history):
            logging.info('Some of the version number /document/tracking/revision_history does not match semantic versioning. Reindexing to integers.')
            revision_history = sorted(revision_history, key=lambda x: list(map(int, x['number'].split('.'))))
            i = 1
            for revision in revision_history:
                revision['number'] = i
                i += 1

        # match document version to corresponding one in revision history
        # TODO: maybe throw exception if more than one revision matches? Is it checked somewhere else? see: http://docs.oasis-open.org/csaf/csaf-cvrf/v1.2/cs01/csaf-cvrf-v1.2-cs01.html#_Toc493508877
        current_revision = list(filter(lambda revision: revision['number_cvrf'] == root_element.Version.text, revision_history))[0]
        version = current_revision['number']

        # cleanup extra vars
        for revision in revision_history:
            revision.pop('number_cvrf')

        return revision_history, version

    def _process_optional_elements(self, root_element):
        if hasattr(root_element.Identification, 'Alias'):
            aliases = []
            for alias in root_element.Identification.Alias:
                aliases.append(alias.text)

            self.json['aliases'] = aliases
