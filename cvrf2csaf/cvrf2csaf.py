import logging
import argparse
import os
import json
from lxml import etree
from lxml import objectify

from .common.utils import get_config_from_file, store_json, critical_exit

from .section_handlers.document_acknowlegments import Acknowledgments
from .section_handlers.document_aggregate_severity import AggregateSeverity
from .section_handlers.document_category import DocumentCategory
from .section_handlers.document_csaf_version import DocumentCsafVersion
from .section_handlers.document_distribution import DocumentDistribution
from .section_handlers.document_lang import DocumentLang
from .section_handlers.document_notes import DocumentNotes
from .section_handlers.document_publisher import DocumentPublisher
from .section_handlers.document_references import DocumentReferences
from .section_handlers.document_source_lang import DocumentSourceLang
from .section_handlers.document_title import DocumentTitle
from .section_handlers.document_tracking import DocumentTracking
from .section_handlers.product_tree import ProductTree
from .section_handlers.vulnerability import Vulnerabilities

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(module)s - %(levelname)s - %(message)s')


class DocumentHandler:
    """
    Main Handler of the conversion:
    1. Reads/Parses/Validates CVRF XML input
    2. Iterates over each first-level XML section
    3. Each first-level XML section has its class and its methods are responsible for converting the content
    4. Collecting the output of each mapper class, which consists of the CSAF2.0 JSON equivalent
    5. Combining it to the final JSON and writing the result to a file
    """

    SCHEMA_FILE = 'schemata/cvrf/1.2/cvrf.xsd'
    CATALOG_FILE = 'schemata/catalog_1_2.xml'

    def __init__(self, config):

        self.document_acknowledgments = Acknowledgments()
        self.document_aggregate_severity = AggregateSeverity()
        self.document_category = DocumentCategory()
        self.document_csaf_version = DocumentCsafVersion()
        self.document_distribution = DocumentDistribution()
        self.document_lang = DocumentLang()
        self.document_notes = DocumentNotes(config=config)
        self.document_publisher = DocumentPublisher(config['publisher_name'],
                                                    config['publisher_namespace'])
        self.document_references = DocumentReferences()
        self.document_source_lang = DocumentSourceLang()
        self.document_title = DocumentTitle()
        self.document_tracking = DocumentTracking(config,
                                                  config['cvrf2csaf_name'],
                                                  config['cvrf2csaf_version'],
                                                  config['force_update_revision_history'])
        self.product_tree = ProductTree()
        self.vulnerabilities = Vulnerabilities()

        # ToDo: Lang and SourceLang are missing here.
        self.sections_handlers = {
            'Acknowledgements': self.document_acknowledgments,
            'AggregateSeverity': self.document_aggregate_severity,
            'DocumentType': self.document_category,
            'DocumentDistribution': self.document_distribution,
            'DocumentNotes': self.document_notes,
            'DocumentPublisher': self.document_publisher,
            'DocumentReferences': self.document_references,
            'DocumentTitle': self.document_title,
            'DocumentTracking': self.document_tracking,
            'ProductTree': self.product_tree,
            'Vulnerability': self.vulnerabilities,
        }

    def _parse(self, root):
        for elem in root.iterchildren():
            # get tag name without it's namespace, don't use elem.tag here
            tag = etree.QName(elem).localname
            tag_handler = self.sections_handlers.get(tag)

            if tag_handler:
                tag_handler.create_csaf(root_element=elem)
            else:
                logging.warning(f'Not handled input tag {tag}. No parser available.')

    def _compose_final_csaf(self) -> dict:
        # Merges first level leaves into final CSAF document.
        # [mapping table](https://github.com/tschmidtb51/csaf/blob/csaf-2.0-what-is-new-table/notes/whats-new-csaf-v2.0-cn01.md#e4-mapped-elements)

        final_csaf = {'document': {}}
        final_csaf['document']['acknowledgments'] = self.document_acknowledgments.csaf
        final_csaf['document']['aggregate_severity'] = self.document_aggregate_severity.csaf
        final_csaf['document']['category'] = self.document_category.csaf
        final_csaf['document']['distribution'] = self.document_distribution.csaf
        final_csaf['document']['lang'] = self.document_lang.csaf
        final_csaf['document']['notes'] = self.document_notes.csaf
        final_csaf['document']['publisher'] = self.document_publisher.csaf
        final_csaf['document']['source_lang'] = self.document_source_lang.csaf
        final_csaf['document']['references'] = self.document_references.csaf
        final_csaf['document']['title'] = self.document_title.csaf
        final_csaf['document']['tracking'] = self.document_tracking.csaf
        final_csaf['document']['references'] = self.document_references.csaf
        final_csaf['product_tree'] = self.product_tree.csaf
        final_csaf['vulnerabilities'] = self.vulnerabilities.csaf
        return final_csaf

    @classmethod
    def _validate_and_open_file(cls, file_path):
        """Read CVRF XML from $path"""
        with open(cls.SCHEMA_FILE) as f:
            os.environ.update(XML_CATALOG_FILES=cls.CATALOG_FILE)
            schema = etree.XMLSchema(file=f)

        parser = objectify.makeparser(schema=schema)

        try:
            xml_objectified = objectify.parse(file_path, parser).getroot()
            return xml_objectified
        except etree.ParseError as e:
            critical_exit(f'Input document not valid: {e}.')

    def convert_file(self, path) -> dict:
        """Wrapper to read/parse CVRF and parse it to CSAF JSON structure"""
        root = DocumentHandler._validate_and_open_file(path)

        self._parse(root)

        return self._compose_final_csaf()


def main():
    # General args
    parser = argparse.ArgumentParser(description='Converts CVRF XML input into CSAF 2.0 JSON output.')
    parser.add_argument('--input-file', dest='input_file', type=str, required=True,
                        help="CVRF XML input file to parse", metavar='PATH')
    parser.add_argument('--output-file', dest='output_file', type=str, required=True,
                        help="CVRF JSON output file to write to.", metavar='PATH')
    parser.add_argument('--print', dest='print', action='store_true', default=False,
                        help="Additionally prints JSON output on command line.")
    parser.add_argument('--force', action='store_true', dest='force',
                        help="If used, the converter produces output that is invalid "
                             "(use case: convert to JSON, fix the errors manual, e.g. in Secvisogram.")



    # Document Publisher args
    parser.add_argument('--publisher-name', dest='publisher_name', type=str, help="Name of the publisher.")
    parser.add_argument('--publisher-namespace', dest='publisher_namespace', type=str,
                        help="Namespace of the publisher.")

    # Document Tracking args
    parser.add_argument('--force-update-revision-history', action='store_const', const='cmd-arg-entered',
                        help="If the current version is not present in the revision history AND the difference "
                             "between the current version and the most recent revision is more than one version, "
                             "the current version is added to the revision history. Also warning is produced. By default, "
                             "the current version is added only if the difference is one version.")

    args = {k: v for k, v in vars(parser.parse_args()).items() if v is not None}

    config = get_config_from_file()

    # Update & rewrite config file values with the ones from command line arguments
    config.update(args)

    # Boolean optional argument need special treatment
    if config['force_update_revision_history'] == 'cmd-arg-entered':
        config['force_update_revision_history'] = True

    if not os.path.isfile(config.get('input_file')):
        critical_exit(f'Input file not found, check the path: {config.get("input_file")}')

    # DocumentHandler is iterating over each XML element within convert_file and return CSAF 2.0 JSON
    h = DocumentHandler(config)
    final_csaf = h.convert_file(path=config.get('input_file'))

    # Output / Store results
    if final_csaf:
        store_json(js=final_csaf, fpath=config.get('output_file'))
        if config.get('print', False):
            print(json.dumps(final_csaf, indent=1))


if __name__ == '__main__':
    main()
