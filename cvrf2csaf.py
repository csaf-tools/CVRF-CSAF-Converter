from lxml import etree
import logging
import argparse
import yaml
import json

from utils import str2bool, get_config_from_file, store_json

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

    def __init__(self, config):
        self.publisher = DocumentPublisherHandler(config['publisher_name'], config['publisher_namespace'])

    def _parse(self, root):
        for elem in root.iterchildren():
            # get tag name without it's namespace, don't use elem.tag here
            tag = etree.QName(elem).localname
            if tag == 'DocumentPublisher':
                self.publisher.parse(elem)
            elif tag == 'ToDo':
                # ToDo: Going through it tag by tag for further parsing
                pass
            else:
                logging.warning(f'Not handled input tag {tag}. No parser available.')

    def _create_json(self):
        js = {'document': {}}
        js_publisher = self.publisher.create_json()
        js['document']['publisher'] = js_publisher
        return js

    @staticmethod
    def _open_file(path):
        """Read CVRF XML from $path"""
        root = None
        try:
            tree = etree.parse(path)
            root = tree.getroot()
        except Exception as e:
            logging.error(f"Failed to open file {path}, {e}.")
        return root

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
        return self._create_json()


class DocumentPublisherHandler:

    def __init__(self, name, namespace):
        self.name = name
        self.namespace = namespace

    def parse(self, element):
        self.Type = element.attrib.get('Type', None)
        self.VendorID = element.attrib.get('VendorID', None)
        self.ContactDetails = element.findtext('{*}ContactDetails')
        self.IssuingAuthority = element.findtext('{*}IssuingAuthority')

    def create_json(self):
        js = {}

        # mandatory values
        js['name'] = self.name
        js['namespace'] = self.namespace
        js['category'] = self.Type

        # ToDo: Complete structure

        # optional values
        if self.ContactDetails:
            js['contact_details'] = self.ContactDetails
        if self.IssuingAuthority:
            js['issuing_authority'] = self.IssuingAuthority
        return js


# Load CLI args
parser = argparse.ArgumentParser(description='Converts CVRF XML input into CSAF 2.0 JSON output.')
parser.add_argument('--input-file', dest='input_file', type=str, help="CVRF XML input file to parse", default='./sample_input/sample.xml')
parser.add_argument('--out-file', dest='out_file', type=str, help="CVRF JSON output file to write to.", default='./output/sample.json')
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




