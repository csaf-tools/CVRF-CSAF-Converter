import logging
import re
import sys

from typing import Tuple
from src.common.common import SectionHandler
from utils import get_utc_timestamp
from operator import itemgetter


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

        revision_history, version = self._process_revision_history(root_element)
        self.json['revision_history'] = revision_history
        self.json['version'] = version

        # Generator is set by this Converter
        self.json['generator'] = {}
        self.json['generator']['date'] = get_utc_timestamp()
        self.json['generator']['engine'] = {}
        self.json['generator']['engine']['name'] = self.cvrf2csaf_name
        self.json['generator']['engine']['version'] = self.cvrf2csaf_version

    def _process_optional_elements(self, root_element):
        if hasattr(root_element.Identification, 'Alias'):
            aliases = []
            for alias in root_element.Identification.Alias:
                aliases.append(alias.text)

            self.json['aliases'] = aliases

    @staticmethod
    def check_for_version_t(revision_history):
        """
        Checks whether all version numbers in /document/tracking/revision_history match semantic versioning.
        semantic version is defined in version_t definition
        see: https://docs.oasis-open.org/csaf/csaf/v2.0/csd01/csaf-v2.0-csd01.html#3111-version-type and
        section 9.1.5 Conformance Clause 5: CVRF CSAF converter
        """

        pattern = (
            r'^((0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)'
            r'(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?)$'
        )
        return all(re.match(pattern, revision['number']) for revision in revision_history)

    @staticmethod
    def _as_int_tuple(text: str) -> Tuple[int]:
        """ Converts string of dotted numbers into tuple of ints """
        try:
            return tuple(int(part) for part in text.split('.'))
        except ValueError:
            return (sys.maxsize, )

    def _process_revision_history(self, root_element):
        # preprocess the data
        revision_history = []
        for revision in root_element.RevisionHistory.Revision:
            # number_cvrf: keep original value in this variable for matching later
            # number: this value might be overwritten later if some version numbers doesn't match semantic versioning
            revision_history.append(
                {
                    'date': revision.Date.text,
                    'number': revision.Number.text,
                    'summary': revision.Description.text,
                    # Extra vars
                    'number_cvrf': revision.Number.text,
                    'version_as_int_tuple': self._as_int_tuple(revision.Number.text),
                }
            )

        # handle corresponding part of Conformance Clause 5: CVRF CSAF converter
        # that is: some version numbers in revision_history don't match semantic versioning
        if not self.check_for_version_t(revision_history):
            logging.info('Some version numbers in /document/tracking/revision_history does not match semantic versioning. Reindexing to integers.')

            revision_history = sorted(revision_history, key=itemgetter('version_as_int_tuple'))

            for rev_number, revision in enumerate(revision_history, start=1):
                revision['number'] = rev_number  # Changing the type from str to int

        # match document version to corresponding one in revision history
        # TODO: maybe throw exception if more than one revision matches? Is it checked somewhere else? see: http://docs.oasis-open.org/csaf/csaf-cvrf/v1.2/cs01/csaf-cvrf-v1.2-cs01.html#_Toc493508877
        version = next(rev for rev in revision_history if rev['number_cvrf'] == root_element.Version.text)['number']

        # cleanup extra vars
        for revision in revision_history:
            revision.pop('number_cvrf')
            revision.pop('version_as_int_tuple')

        return revision_history, version


