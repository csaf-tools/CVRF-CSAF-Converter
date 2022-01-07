import logging
import argparse
import os
import json
from lxml import etree
from lxml import objectify

from .common.utils import get_config_from_file, store_json, critical_exit

from .section_handlers.document_tracking import DocumentTracking
from .section_handlers.document_publisher import DocumentPublisher


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


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
        self.document_publisher = DocumentPublisher(config['publisher_name'],
                                                    config['publisher_namespace'])
        self.document_tracking = DocumentTracking(config['cvrf2csaf_name'],
                                                  config['cvrf2csaf_version'])

    def _parse(self, root):
        for elem in root.iterchildren():
            # get tag name without it's namespace, don't use elem.tag here
            tag = etree.QName(elem).localname
            if tag == 'DocumentPublisher':
                self.document_publisher.create_csaf(elem)
            elif tag == 'DocumentTracking':
                self.document_tracking.create_csaf(elem)
            elif tag == 'ToDo':
                # ToDo: Going through it tag by tag for further parsing
                pass
            else:
                logging.warning(f'Not handled input tag {tag}. No parser available.')

    def _compose_final_csaf(self) -> dict:
        final_csaf = {'document': {}}
        final_csaf['document']['publisher'] = self.document_publisher.csaf
        final_csaf['document']['tracking'] = self.document_tracking.csaf
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
    # Load CLI args
    parser = argparse.ArgumentParser(description='Converts CVRF XML input into CSAF 2.0 JSON output.')
    parser.add_argument('--input-file', dest='input_file', type=str, required=True,
                        help="CVRF XML input file to parse", metavar='PATH')
    parser.add_argument('--output-file', dest='output_file', type=str, required=True,
                        help="CVRF JSON output file to write to.", metavar='PATH')
    parser.add_argument('--print', dest='print', action='store_true', default=False,
                        help="Additionally prints JSON output on command line.")

    parser.add_argument('--publisher-name', dest='publisher_name', type=str, help="Name of the publisher.")
    parser.add_argument('--publisher-namespace', dest='publisher_namespace', type=str,
                        help="Namespace of the publisher.")

    args = {k: v for k, v in vars(parser.parse_args()).items() if v is not None}

    config = get_config_from_file()
    config.update(args)

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
