import logging
from ..common.common import SectionHandler


class ProductTree(SectionHandler):
    """ Responsible for converting the ProductTree section """

    def _process_mandatory_elements(self, root_element):
        """ There are no mandatory elements in the ProductTree section """
        pass

    def _process_optional_elements(self, root_element):
        if hasattr(root_element, 'FullProductName'):
            full_product_names = []
            for full_product_name in root_element.FullProductName:
                fpn_to_add = {
                    'product_id': full_product_name.attrib['ProductID'],
                    'name': full_product_name.text,
                }
                if full_product_name.attrib.get('CPE'):
                    fpn_to_add['product_identification_helper'] = {'cpe': full_product_name.attrib['CPE']}

                full_product_names.append(fpn_to_add)

            self.csaf['full_product_names'] = full_product_names

        if hasattr(root_element, 'Relationship'):
            relationships = []
            for relationship in root_element.Relationship:
                first_prod_name = relationship.FullProductName[0]

                if len(relationship.FullProductName) > 1:
                    # To be compliant with 9.1.5 Conformance Clause 5: CVRF CSAF converter
                    # https://docs.oasis-open.org/csaf/csaf/v2.0/csaf-v2.0.html
                    logging.warning(f'Input line {relationship.sourceline}: Relationship contains more '
                                    'FullProductNames. Taking only the first one, since CSAF expects '
                                    'only 1 value here')

                rel_to_add = {
                    'category': relationship.attrib['RelationType'],
                    'product_reference': relationship.attrib['ProductReference'],
                    'relates_to_product_reference': relationship.attrib['RelatesToProductReference'],
                    'full_product_name': {
                        'product_id': first_prod_name.attrib['ProductID'],
                        'name': first_prod_name.text,
                    }
                }

                if first_prod_name.attrib.get('CPE'):
                    rel_to_add['full_product_name']['product_identification_helper'] = {'cpe': first_prod_name.attrib['CPE']}

                relationships.append(rel_to_add)

                self.csaf['relationships'] = relationships
