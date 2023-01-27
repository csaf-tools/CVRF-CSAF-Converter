""" Module containing DocumentHandler class taking care of conversion.
    Program's top-level logic is done in main() function.
"""
# pylint: disable=c-extension-no-member
import logging
import argparse
import json
import os
import re
import turvallisuusneuvonta as mandatory_tests

from lxml import etree
from lxml import objectify
from jsonschema import Draft202012Validator, ValidationError, SchemaError, \
    draft202012_format_checker
from pkg_resources import get_distribution, Requirement, resource_filename

from .common.utils import get_config_from_file, store_json, critical_exit, create_file_name

from .section_handlers.document_leaf_elements import DocumentLeafElements
from .section_handlers.acknowledgments import Acknowledgments
from .section_handlers.notes import Notes
from .section_handlers.document_publisher import DocumentPublisher
from .section_handlers.references import References
from .section_handlers.document_tracking import DocumentTracking
from .section_handlers.product_tree import ProductTree
from .section_handlers.vulnerability import Vulnerability
from .common.common import SectionHandler

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(module)s - %(levelname)s - %(message)s')


# pylint: disable=too-many-instance-attributes
class DocumentHandler:
    """
    Main Handler of the conversion:
    1. Reads/Parses/Validates CVRF XML input
    2. Iterates over each first-level XML section
    3. Each first-level XML section has its class and its methods are responsible for
       converting the content
    4. Collecting the output of each mapper class, which consists of the CSAF2.0 JSON equivalent
    5. Combining it to the final JSON and writing the result to a file
    """

    TOLERATED_ERRORS_SUBSTR = [
        "}ScoreSetV3': This element is not expected. Expected is one of"
        " ( {http://docs.oasis-open.org/csaf/ns/csaf-cvrf/v1.2/vuln}ScoreSetV2,"
        " {http://docs.oasis-open.org/csaf/ns/csaf-cvrf/v1.2/vuln}ScoreSetV3 ).",
        "}ScoreSetV3': This element is not expected. Expected is "
        "( {http://docs.oasis-open.org/csaf/ns/csaf-cvrf/v1.2/vuln}ScoreSetV3 ).",
        r"is not accepted by the pattern '[c][pP][eE]:/[AHOaho]?(:[A-Za-z0-9\._\-~%]*){0,6}'."]

    PACKAGE_NAME = 'cvrf2csaf'

    SCHEMA_FILE = resource_filename(Requirement.parse(PACKAGE_NAME),
                                    f'{PACKAGE_NAME}/schemata/cvrf/1.2/cvrf.xsd')
    CATALOG_FILE = resource_filename(Requirement.parse(PACKAGE_NAME),
                                     f'{PACKAGE_NAME}/schemata/catalog_1_2.xml')

    # Content copied from
    # https://github.com/secvisogram/secvisogram/blob/main/app/lib/app/shared/Core/csaf_2.0_strict.json
    CSAF_SCHEMA_FILE = resource_filename(Requirement.parse(PACKAGE_NAME),
                                         f'{PACKAGE_NAME}'
                                         f'/schemata/csaf/2.0/csaf_json_schema_strict.json')

    def __init__(self, config, pkg_version):
        self.document_leaf_elements = DocumentLeafElements(config)
        self.document_acknowledgments = Acknowledgments()
        self.document_notes = Notes()
        self.document_publisher = DocumentPublisher(config)
        self.document_references = References(config)
        self.document_tracking = DocumentTracking(config, pkg_version)
        self.product_tree = ProductTree()
        self.vulnerability = Vulnerability(config)

        self.sections_handlers = {
            'Acknowledgments': self.document_acknowledgments,
            'DocumentNotes': self.document_notes,
            'DocumentPublisher': self.document_publisher,
            'DocumentReferences': self.document_references,
            'DocumentTracking': self.document_tracking,
            'ProductTree': self.product_tree,
            'Vulnerability': self.vulnerability,
        }

    def _update_cvssv3_version_from_schema(self, root_element):
        """ Tries to update CVSS 3.x version from schema."""
        cvss_3_regex = r'.*cvss-v(3\.[01]).*'

        potential_cvss3 = None

        # iterate over  namespaces
        for name_space in root_element.nsmap.values():
            match = re.match(cvss_3_regex, name_space)
            if match:
                cvss_version_matched = match.groups()[0]
                # no potential cvss version found yet -> store it
                if not potential_cvss3:
                    potential_cvss3 = cvss_version_matched
                # already have some version, but it's the same as currently matched -> ok, continue
                elif potential_cvss3 == cvss_version_matched:
                    continue
                # else we have two different potential cvss versions -> skip this step comletely
                else:
                    return

        if potential_cvss3:
            logging.info('Default CVSS v3.x version set to %s based on document XML schemas.',
                         potential_cvss3)
            self.vulnerability.default_cvss_version = potential_cvss3

    def _parse(self, root):
        self._update_cvssv3_version_from_schema(root)

        # Document leaf elements are handled on the root itself
        self.document_leaf_elements.create_csaf(root)

        # For children of the root element with a deeper structure,
        # dedicated section handlers are used
        for elem in root.iterchildren():
            # get tag name without its namespace, don't use elem.tag here
            tag = etree.QName(elem).localname
            tag_handler = self.sections_handlers.get(tag)

            if tag_handler:
                tag_handler.create_csaf(root_element=elem)

    def _compose_final_csaf(self) -> dict:
        # Merges first level leaves into final CSAF document.
        # [mapping table](https://github.com/tschmidtb51/csaf/blob/csaf-2.0-what-is-new-table
        # /notes/whats-new-csaf-v2.0-cn01.md#e4-mapped-elements)

        final_csaf = {'document': {}}
        final_csaf['document'] = self.document_leaf_elements.csaf

        section_mappings = (
            (final_csaf['document'], 'publisher', self.document_publisher.csaf),
            (final_csaf['document'], 'tracking', self.document_tracking.csaf),
            (final_csaf['document'], 'notes', self.document_notes.csaf),
            (final_csaf['document'], 'references', self.document_references.csaf),
            (final_csaf['document'], 'acknowledgments', self.document_acknowledgments.csaf),
            (final_csaf, 'product_tree', self.product_tree.csaf),
            (final_csaf, 'vulnerabilities', self.vulnerability.csaf),
        )

        for root, section, csaf_content in section_mappings:
            if csaf_content:
                root[section] = csaf_content

        return final_csaf

    @classmethod
    def _tolerate_errors(cls, error_list):
        tolerated_errors = [error for error in error_list if any(
            error_substr in error.message for error_substr in
            DocumentHandler.TOLERATED_ERRORS_SUBSTR)]
        if len(tolerated_errors) > 0:
            logging.warning('Tolerating errors: %s.', tolerated_errors)
        return set(tolerated_errors) == set(error_list)

    @classmethod
    def _validate_input_against_schema(cls, xml_objectified):
        with open(cls.SCHEMA_FILE, encoding='utf-8') as f:
            os.environ.update(XML_CATALOG_FILES=cls.CATALOG_FILE)
            schema = etree.XMLSchema(file=f)

        try:
            schema.assertValid(xml_objectified)
            logging.info('Input XSD validation OK.')
            return True
        except etree.DocumentInvalid:
            errors = list(schema.error_log)

        if not DocumentHandler._tolerate_errors(errors):
            logging.error('Errors during input validation occurred, reason(s): %s.', errors)
            return False

        return True

    @classmethod
    def _open_and_validate_file(cls, file_path):
        try:
            parser = objectify.makeparser(resolve_entities=False, no_network=True)
            xml_objectified = objectify.parse(file_path, parser)
        except (OSError, etree.LxmlError) as e:
            critical_exit(f'Failed to open input file {file_path}: {e}.')

        if not DocumentHandler._validate_input_against_schema(xml_objectified):
            critical_exit('Input document not valid.')

        return xml_objectified.getroot()

    def convert_file(self, path) -> dict:
        """Wrapper to read/parse CVRF and parse it to CSAF JSON structure"""
        root = DocumentHandler._open_and_validate_file(path)

        self._parse(root)

        return self._compose_final_csaf()

    def validate_output_against_schema(self, final_csaf) -> bool:
        """
        Validates the CSAF output against the CSAF JSON schema
        return: True if valid, False if invalid
        """
        with open(self.CSAF_SCHEMA_FILE, encoding='utf-8') as f:
            csaf_schema_content = json.loads(f.read())

        try:
            Draft202012Validator.check_schema(csaf_schema_content)
            validator = Draft202012Validator(csaf_schema_content,
                                             format_checker=draft202012_format_checker)
            validator.validate(final_csaf)
        except SchemaError as e:
            logging.error(
                'CSAF schema validation error. Provided CSAF schema is invalid. Message: %s',
                e.message)
            return False
        except ValidationError as e:
            logging.error('CSAF schema validation error. Path: %s. Message: %s.', e.json_path,
                          e.message)
            return False
        else:
            logging.info('CSAF schema validation OK.')
            return True

    @staticmethod
    def validate_mandatory_tests(final_csaf):
        """
        Validates output against mandatory tests:
        https://docs.oasis-open.org/csaf/csaf/v2.0/cs02/csaf-v2.0-cs02.html#61-mandatory-tests
        """
        # pylint: disable=fixme
        # TODO: After the turvallisuusneuvonta package is complete and part of the csaf package,
        #  replace the implementation
        # For now we fetch the tests like this to see which failed
        passed = True
        for m_test_str in mandatory_tests.__all__:
            # Skip translator function since translator value cannot appear on the input
            # Skip is_valid which calls all the tests (but doesnt produce any output)
            if m_test_str in ['is_valid', 'is_valid_translator']:
                continue
            m_test_call = getattr(mandatory_tests, m_test_str)
            if not m_test_call(final_csaf):
                passed = False
                logging.error('Mandatory test %s failed.', m_test_str)

        return passed


# pylint: disable=missing-function-docstring
def main():
    # General args
    parser = argparse.ArgumentParser(
        description='Converts CVRF 1.2 XML input into CSAF 2.0 JSON output.')
    parser.add_argument('-v', '--version', action='version',
                        version=str(get_distribution('cvrf2csaf').version))
    parser.add_argument('--input-file', dest='input_file', type=str, required=True,
                        help="CVRF XML input file to parse", metavar='PATH')
    parser.add_argument('--output-dir', dest='output_dir', type=str, default='./', metavar='PATH',
                        help="CSAF output dir to write to."
                             " Filename is derived from /document/tracking/id.")
    parser.add_argument('--print', dest='print', action='store_true', default=False,
                        help="Additionally prints CSAF JSON output on stdout.")
    parser.add_argument('--force', action='store_const', const='cmd-arg-entered',
                        help="If used, the converter produces output even if it is invalid "
                             "(errors occured during conversion). "
                             "Target use case: best-effort conversion to JSON, "
                             "fix the errors manually, e.g. in Secvisogram.")

    # Document Publisher args
    parser.add_argument('--publisher-name', dest='publisher_name', type=str,
                        help="Name of the publisher.")
    parser.add_argument('--publisher-namespace', dest='publisher_namespace', type=str,
                        help="Namespace of the publisher. Must be a valid URI")

    # Document Tracking args
    parser.add_argument('--fix-insert-current-version-into-revision-history', action='store_const',
                        const='cmd-arg-entered',
                        help="If the current version is not present in the revision history "
                             "the current version is added to the revision history."
                             " Also warning is produced. By default, an error is produced.")

    # Document References args
    parser.add_argument('--force-insert-default-reference-category', action='store_const',
                        const='cmd-arg-entered',
                        help='When "Type" attribute not present in "Reference" element, '
                             'then force using default value "external".')

    # Vulnerabilities args
    parser.add_argument('--remove-CVSS-values-without-vector', action='store_const',
                        const='cmd-arg-entered',
                        help="If vector is not present in CVSS ScoreSet, the convertor removes"
                             " the whole ScoreSet instead of producing an error.")

    parser.add_argument('--default-CVSS3-version', dest='default_CVSS3_version',
                        help="Default version used for CVSS version 3, when the version cannot be"
                             " derived from other sources. Default value is '3.0'.")

    args = {k: v for k, v in vars(parser.parse_args()).items() if v is not None}

    config = get_config_from_file()

    # Update & rewrite config file values with the ones from command line arguments
    config.update(args)

    # Boolean optional arguments that are also present in config need special treatment
    if config['fix_insert_current_version_into_revision_history'] == 'cmd-arg-entered':
        config['fix_insert_current_version_into_revision_history'] = True
    if config['force_insert_default_reference_category'] == 'cmd-arg-entered':
        config['force_insert_default_reference_category'] = True
    if config['remove_CVSS_values_without_vector'] == 'cmd-arg-entered':
        config['remove_CVSS_values_without_vector'] = True
    if config['force'] == 'cmd-arg-entered':
        config['force'] = True

    if not os.path.isfile(config.get('input_file')):
        critical_exit(f'Input file not found, check the path: {config.get("input_file")}')

    # Get the version of the installed package
    pkg_version = get_distribution('cvrf2csaf').version

    # DocumentHandler is iterating over each XML element within convert_file and
    # return CSAF 2.0 JSON
    handler = DocumentHandler(config, pkg_version)
    final_csaf = handler.convert_file(path=config.get('input_file'))

    valid_output = True
    if not handler.validate_output_against_schema(final_csaf) \
            or not handler.validate_mandatory_tests(final_csaf) \
            or SectionHandler.error_occurred:
        valid_output = False

        if not config.get('force', False):
            critical_exit("Some error occurred during conversion, can't produce output."
                          " To override this, use --force.")
        else:
            logging.warning('Some errors occurred during conversion,'
                            ' but producing output as --force option is used.')

    # Output / Store results
    file_name = create_file_name(final_csaf['document'].get('tracking', {}).get('id', None),
                                 valid_output)
    file_path = str(os.path.join(config.get('output_dir'), file_name))
    store_json(json_dict=final_csaf, fpath=file_path)
    if config.get('print', False):
        print(json.dumps(final_csaf, indent=2))


if __name__ == '__main__':
    main()
