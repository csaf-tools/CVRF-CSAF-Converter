""" Module containing DocumentTracking class """
import logging
import re
import sys
from operator import itemgetter
from typing import Tuple
from ..common.common import SectionHandler
from ..common.utils import get_utc_timestamp


# pylint: disable=too-few-public-methods
class DocumentTracking(SectionHandler):
    """ Responsible for converting the DocumentTracking section:
      - /cvrf:cvrfdoc/cvrf:DocumentTracking
    """
    tracking_status_mapping = {
        'Final': 'final',
        'Draft': 'draft',
        'Interim': 'interim',
    }

    def __init__(self, config, pkg_version):
        super().__init__()
        self.cvrf2csaf_name = config.get('cvrf2csaf_name')
        self.cvrf2csaf_version = pkg_version
        self.fix_insert_current_version_into_revision_history \
            = config.get('fix_insert_current_version_into_revision_history')

    def _process_mandatory_elements(self, root_element):
        self.csaf['id'] = self._remove_id_whitespace(root_element.Identification.ID.text)
        self.csaf['current_release_date'] = get_utc_timestamp(root_element.CurrentReleaseDate.text)
        self.csaf['initial_release_date'] = get_utc_timestamp(root_element.InitialReleaseDate.text)
        self.csaf['status'] = self.tracking_status_mapping[root_element.Status.text]

        revision_history, version = self._handle_revision_history_and_version(root_element)
        self.csaf['revision_history'] = revision_history
        self.csaf['version'] = version

        # Generator is set by this Converter
        self.csaf['generator'] = {}
        self.csaf['generator']['date'] = get_utc_timestamp(time_stamp='now')
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
    def _remove_id_whitespace(id_string: str) -> str:
        """
        Removes leading/trailing whitespace and linebreaks from the ID string and 
        outputs a warning if the ID string was changed.
        """
        id_string_clean = id_string.strip().replace("\r", "").replace("\n", "")
        if id_string_clean != id_string:
            logging.warning(
                'The ID string contained leading/trailing whitespace or linebreaks. '
                'These were removed.'
            )
        return id_string_clean

    @staticmethod
    def check_for_version_t(revision_history):
        """
        Checks whether all version numbers in /document/tracking/revision_history match
        semantic versioning. Semantic version is defined in version_t definition.
        see: https://docs.oasis-open.org/csaf/csaf/v2.0/csaf-v2.0.html#3111-version-type
        and section 9.1.5 Conformance Clause 5: CVRF CSAF converter
        """

        pattern = (
            r'^((0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)'
            r'(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)'
            r'(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))'
            r'?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?)$'
        )
        return all(re.match(pattern, revision['number']) for revision in revision_history)

    @staticmethod
    def _as_int_tuple(text: str) -> Tuple[int]:
        """ Converts string of dotted numbers into tuple of ints """
        try:
            return tuple(int(part) for part in text.split('.'))
        except ValueError:
            return (sys.maxsize,)

    def _add_current_revision_to_history(self, root_element, revision_history) -> None:
        """
        If the current version is missing in Revision history and
        --fix-insert-current-version-into-revision-history is True,
        the current version is added to the history.
        """

        revision_history.append(
            {
                'date': get_utc_timestamp(root_element.CurrentReleaseDate.text),
                'number': root_element.Version.text,
                'summary': f'Added by {self.cvrf2csaf_name} as the value was missing in the '
                           f'original CVRF.',
                # Extra vars
                'number_cvrf': root_element.Version.text,
                'version_as_int_tuple': self._as_int_tuple(root_element.Version.text),
            }
        )

    @staticmethod
    def _reindex_versions_to_integers(root_element, revision_history):
        logging.warning(
            'Some version numbers in revision_history do not match semantic versioning. '
            'Reindexing to integers.')

        revision_history_sorted = sorted(revision_history, key=itemgetter('version_as_int_tuple'))

        for rev_number, revision in enumerate(revision_history_sorted, start=1):
            revision['number'] = str(rev_number)
            # add property legacy_version with the original version number
            # for each reindexed version
            revision['legacy_version'] = revision['number_cvrf']

        # after reindexing, match document version to corresponding one in revision history
        version = next(rev for rev in revision_history_sorted if
                       rev['number_cvrf'] == root_element.Version.text)['number']

        return revision_history_sorted, version

    def _handle_revision_history_and_version(self, root_element):
        # preprocess the data
        revision_history = []
        for revision in root_element.RevisionHistory.Revision:
            # number_cvrf: keep original value in this variable for matching later
            # number: this value might be overwritten later if some version numbers doesn't match
            # semantic versioning
            revision_history.append(
                {
                    'date': get_utc_timestamp(revision.Date.text),
                    'number': revision.Number.text,
                    'summary': revision.Description.text,
                    # Extra vars
                    'number_cvrf': revision.Number.text,
                    'version_as_int_tuple': self._as_int_tuple(revision.Number.text),
                }
            )

        # Just copy over the version
        version = root_element.Version.text

        missing_latest_version_in_history = False
        # Do we miss the current version in the revision history?
        if not [rev for rev in revision_history if rev['number'] == version]:
            if self.fix_insert_current_version_into_revision_history:
                logging.warning('Trying to fix the revision history by adding the current version. '
                                'This may lead to inconsistent history. This happens because '
                                '--fix-insert-current-version-into-revision-history is used. ')
                self._add_current_revision_to_history(root_element, revision_history)
            else:
                logging.error('Current version is missing in revision history. This can be fixed by'
                              ' using --fix-insert-current-version-into-revision-history.')
                missing_latest_version_in_history = True
                self.error_occurred = True

        # handle corresponding part of Conformance Clause 5: CVRF CSAF converter
        # that is: some version numbers in revision_history don't match semantic versioning
        if not self.check_for_version_t(revision_history):
            if not missing_latest_version_in_history:
                revision_history, version = self._reindex_versions_to_integers(root_element,
                                                                               revision_history)
            else:
                logging.error('Can not reindex revision history to integers because of missing'
                              ' the current version. This can be fixed with'
                              ' --fix-insert-current-version-into-revision-history')
                self.error_occurred = True

        # cleanup extra vars
        for revision in revision_history:
            revision.pop('number_cvrf')
            revision.pop('version_as_int_tuple')

        return revision_history, version
