import logging
import re
import sys

from typing import Tuple
from src.common.common import SectionHandler
from utils import get_utc_timestamp
from operator import itemgetter
from contextlib import suppress


class DocumentTracking(SectionHandler):
    def __init__(self, cvrf2csaf_name, cvrf2csaf_version):
        super().__init__()
        self.cvrf2csaf_name = cvrf2csaf_name
        self.cvrf2csaf_version = cvrf2csaf_version

    def _process_mandatory_elements(self, root_element):
        self.csaf['id'] = root_element.Identification.ID.text
        self.csaf['current_release_date'] = root_element.CurrentReleaseDate.text
        self.csaf['initial_release_date'] = root_element.InitialReleaseDate.text
        self.csaf['status'] = root_element.Status.text

        revision_history, version = self._process_revision_history(root_element)
        self.csaf['revision_history'] = revision_history
        self.csaf['version'] = version

        # Generator is set by this Converter
        self.csaf['generator'] = {}
        self.csaf['generator']['date'] = get_utc_timestamp()
        self.csaf['generator']['engine'] = {}
        self.csaf['generator']['engine']['name'] = self.cvrf2csaf_name
        self.csaf['generator']['engine']['version'] = self.cvrf2csaf_version

    def _process_optional_elements(self, root_element):
        if hasattr(root_element.Identification, 'Alias'):
            aliases = []
            for alias in root_element.Identification.Alias:
                aliases.append(alias.text)

            self.csaf['aliases'] = aliases

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

    def _add_current_revision_to_history(self, root_element, revision_history) -> None:
        """
        If the current version is missing in Revision history, and the Current revision is X.Y.Z, and the last item
        in history is X.(Y-1).Z, add the current version to the history

        Throws ValueError when didn't match these conditions
        """
        try:
            current_minor_version = self._as_int_tuple(root_element.Version.text)[1]

            latest_history_revision = revision_history[-1]['number']
            latest_history_minor_version = self._as_int_tuple(latest_history_revision)[1]
        except (IndexError, AttributeError):
            raise ValueError('Missing minor version number in the current or latest history Version')

        if current_minor_version - latest_history_minor_version == 1:
            revision_history.append(
                {
                    'date': root_element.CurrentReleaseDate.text,
                    'number': root_element.Version.text,
                    'summary': "Added by CVRF-CSAF-Converter",
                    # Extra vars
                    'number_cvrf': root_element.Version.text,
                    'version_as_int_tuple': self._as_int_tuple(root_element.Version.text),
                }
            )

        else:
            raise ValueError('Can not handle such version difference between The current and the history"s last version')


    def _reindex_history_to_integers(self, root_element, revision_history):
        logging.info('Some version numbers in /document/tracking/revision_history do not match semantic versioning. '
                     'Reindexing to integers.')

        revision_history_sorted = sorted(revision_history, key=itemgetter('version_as_int_tuple'))

        for rev_number, revision in enumerate(revision_history_sorted, start=1):
            revision['number'] = rev_number  # Changing the type from str to int

        # after reindexing, match document version to corresponding one in revision history
        version = next(rev for rev in revision_history_sorted if rev['number_cvrf'] == root_element.Version.text)['number']

        return revision_history_sorted, version

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

        # Do we miss the current version in the revision history?
        if not [rev for rev in revision_history if rev['number'] == root_element.Version.text]:
            try:
                self._add_current_revision_to_history(root_element, revision_history)
                logging.warning(f'/document/tracking/version value was not found in /document/tracking/revision_history. Adding the current revision to the history')
            except ValueError as e:
                # TODO: What to do here? If the current version is not semver OR the difference between versions is > 0.1.0
                logging.critical(f'/document/tracking/version value was not found in /document/tracking/revision_history. Converter doesn"t know how to proceed. Reason: {e}')
                exit(1)

        # handle corresponding part of Conformance Clause 5: CVRF CSAF converter
        # that is: some version numbers in revision_history don't match semantic versioning
        if not self.check_for_version_t(revision_history):
            # TODO: X.Y is not considered a valid semantic versioning, shall we assume X.Y.0 here?
            revision_history, version = self._reindex_history_to_integers(root_element, revision_history)
        else:
            # Just copy over the version
            version = root_element.Version.text

        # cleanup extra vars
        for revision in revision_history:
            revision.pop('number_cvrf')
            revision.pop('version_as_int_tuple')

        return revision_history, version


