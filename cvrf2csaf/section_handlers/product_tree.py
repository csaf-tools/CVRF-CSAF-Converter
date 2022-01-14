import logging
from ..common.common import SectionHandler


class ProductTree(SectionHandler):
    """ Responsible for converting the ProductTree section """

    def _process_mandatory_elements(self, root_element):
        """ There are no mandatory elements in the ProductTree section """
        pass

    def _handle_full_product_names(self, root_element):
        if not hasattr(root_element, 'FullProductName'):
            return

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

    def _handle_relationships(self, root_element):
        if not hasattr(root_element, 'Relationship'):
            return

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


    def _handle_product_groups(self, root_element):
        if not hasattr(root_element, 'ProductGroups'):
            return

        product_groups = []
        for product_group in root_element.ProductGroups.Group:
            product_ids = [x.text for x in product_group.ProductID]
            pg_to_add = {
                'group_id': product_group.attrib['GroupID'],
                'product_ids': product_ids,
            }

            if hasattr(product_group, 'Description'):
                pg_to_add['summary'] = product_group.Description.text

            product_groups.append(pg_to_add)

        self.csaf['product_groups'] = product_groups

    def _handle_branches(self, root_element):
        pass

    def _process_optional_elements(self, root_element):
        self._handle_full_product_names(root_element)
        self._handle_relationships(root_element)
        self._handle_product_groups(root_element)
