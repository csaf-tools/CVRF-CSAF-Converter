import logging
import re
import sys
from operator import itemgetter
from typing import Tuple
from ..common.common import SectionHandler
from ..common.utils import get_utc_timestamp



class ProductTree(SectionHandler):
    """ Responsible for converting the ProductTree section """

    def _process_mandatory_elements(self, root_element):
        """ There are no mandatory elements in the ProductTree section """
        pass

    def _process_optional_elements(self, root_element):
        if hasattr(root_element, 'FullProductName'):
            full_product_names = []
            for full_product_name in root_element.FullProductName:
                full_product_names.append({
                    'product_id': full_product_name.attrib['ProductID'],
                    'name': full_product_name.text,
                    'product_identification_helper': {'cpe': full_product_name.attrib['CPE']},
                })

            self.csaf['full_product_names'] = full_product_names

        # if hasattr(root_element, 'Relationship'):
        #     relationships = []
        #     for relationship in root_element.Relationship:
        #         relationships.append({
        #             # optional CPE attribute in CVRF is omitted (not present in CSAF specification)
        #             # 'product_id': full_product_name.attrib['ProductID'],
        #             # 'name': full_product_name.text,
        #         })
        #
        #     self.csaf['relationships'] = relationships