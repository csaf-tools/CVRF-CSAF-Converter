import logging
import argparse
import yaml
import os
import json

from lxml import etree
from lxml import objectify

from utils import str2bool, get_config_from_file, store_json

from src.section_handlers.document_tracking import DocumentTracking
from src.section_handlers.document_publisher import DocumentPublisher

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class DocumentHandler:
    """
    Main Handler of the conversion:
    1. Reads and Parses CVRF XML input
    2. Recursively iterates over each XML section
    3. For each XML section calling a dedicated mapper class (parse + create_json) 
    4. Collecting the output of each mapper class, which consists of the CSAF2.0 JSON equivalent
    5. Combining it to the final JSON and returning
    """

    SCHEMA_FILE = 'schemata/cvrf/1.2/cvrf.xsd'
    CATALOG_FILE = 'schemata/catalog_1_2.xml'

    def __init__(self, config):
        self.document_publisher = DocumentPublisher(config['publisher_name'], config['publisher_namespace'])
        self.document_tracking = DocumentTracking()

    def _parse(self, root):
        for elem in root.iterchildren():
            # get tag name without it's namespace, don't use elem.tag here
            tag = etree.QName(elem).localname
            if tag == 'DocumentPublisher':
                self.document_publisher.create_json(elem)
            elif tag == 'DocumentTracking':
                self.document_tracking.create_json(elem)
            elif tag == 'ToDo':
                # ToDo: Going through it tag by tag for further parsing
                pass
            else:
                logging.warning(f'Not handled input tag {tag}. No parser available.')

    def _compose_final_json(self):
        js = {'document': {}}
        js['document']['publisher'] = self.document_publisher.json
        js['document']['tracking'] = self.document_tracking.json
        return js

    @classmethod
    def _open_file(cls, file_path):
        """Read CVRF XML from $path"""
        with open(cls.SCHEMA_FILE) as f:
            os.environ.update(XML_CATALOG_FILES=cls.CATALOG_FILE)
            schema = etree.XMLSchema(file=f)
            # xmlschema.assertValid(cvrf_doc)

        parser = objectify.makeparser(schema=schema)

        with open(file_path, 'rb') as f:
            xml_doc = f.read()
            xml_doc = xml_doc.decode('utf-8').encode('ascii')

        xml_objectified = objectify.fromstring(xml_doc, parser)

        return xml_objectified


    def _validate_input_document(self, root):
        """Validate CVRF, where $root is the parsed CVRF XML"""
        valid = True
        try:        
            pass
            # TODO: implement CVRF document validation
        except Exception as exc:
            logging.error(f"Failed to validate input file, {exc}.")
            valid = False
        return valid

    def convert_file(self, path):
        """Wrapper to read/parse CVRF and parse it to CSAF JSON structure"""
        root = DocumentHandler._open_file(path)
        if root is None:
            return None

        if not self._validate_input_document(root):
            logging.error(f"Input file is not valid cvrf document!.")
            return None

        self._parse(root)

        return self._compose_final_json()


# Load CLI args
parser = argparse.ArgumentParser(description='Converts CVRF XML input into CSAF 2.0 JSON output.')
parser.add_argument('--input_file', dest='input_file', type=str, help="CVRF XML input file to parse", default='./sample_input/sample.xml')
parser.add_argument('--out_file', dest='out_file', type=str, help="CVRF JSON output file to write to.", default='./output/sample.json')
parser.add_argument('--print', dest='print', type=str2bool, nargs='?',
                        const=True, default=False,
                        help="1 = Additionally prints JSON output on command line.")

parser.add_argument('--publisher_name', dest='publisher_name', type=str, help="Name of the publisher.")
parser.add_argument('--publisher_namespace', dest='publisher_namespace', type=str, help="Namespace of the publisher.")

args = {k: v for k, v in vars(parser.parse_args()).items() if v is not None}
if __name__ == '__main__':

    config = get_config_from_file()
    config.update(args)

    # DocumentHandler is iterating over each XML element within convert_file and return CSAF 2.0 JSON
    h = DocumentHandler(config)
    js = h.convert_file(path=config.get('input_file'))

    # Output / Store results
    if config.get('print', False):
        print(json.dumps(js, indent=1))

    store_json(js=js, fpath=config.get('out_file'))




