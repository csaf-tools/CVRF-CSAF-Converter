import logging
from ..common.common import SectionHandler


class ProductTree(SectionHandler):
    """ Responsible for converting the ProductTree section """
    
    def __init__(self):
        super().__init__()

    def _process_mandatory_elements(self, root_element):
        """ There are no mandatory elements in the ProductTree section """
        pass

    def _process_optional_elements(self, root_element):
        self._handle_full_product_names(root_element)
        self._handle_relationships(root_element)
        self._handle_product_groups(root_element)

        branches = self._handle_branches_recursive(root_element)
        if branches is not None:
            self.csaf['branches'] = branches

    @staticmethod
    def _construct_full_product_name(fpn_elem) -> dict:
        fpn = {
            'product_id': fpn_elem.attrib['ProductID'],
            'name': fpn_elem.text
        }

        if fpn_elem.attrib.get('CPE'):
            fpn['product_identification_helper'] = {'cpe': fpn_elem.attrib['CPE']}

        return fpn

    def _handle_full_product_names(self, root_element):
        if not hasattr(root_element, 'FullProductName'):
            return

        full_product_names = []
        for fpn_elem in root_element.FullProductName:
            full_product_names.append(self._construct_full_product_name(fpn_elem))

        self.csaf['full_product_names'] = full_product_names

    def _handle_relationships(self, root_element):
        if not hasattr(root_element, 'Relationship'):
            return

        relationships = []
        for rel_elem in root_element.Relationship:
            first_prod_name = rel_elem.FullProductName[0]

            if len(rel_elem.FullProductName) > 1:
                # To be compliant with 9.1.5 Conformance Clause 5: CVRF CSAF converter
                # https://docs.oasis-open.org/csaf/csaf/v2.0/csaf-v2.0.html
                logging.warning(f'Input line {rel_elem.sourceline}: Relationship contains more '
                                'FullProductNames. Taking only the first one, since CSAF expects '
                                'only 1 value here')

            rel_to_add = {
                'category': rel_elem.attrib['RelationType'],
                'product_reference': rel_elem.attrib['ProductReference'],
                'relates_to_product_reference': rel_elem.attrib['RelatesToProductReference'],
                'full_product_name': self._construct_full_product_name(first_prod_name)
            }

            relationships.append(rel_to_add)

        self.csaf['relationships'] = relationships

    def _handle_product_groups(self, root_element):
        if not hasattr(root_element, 'ProductGroups'):
            return

        product_groups = []
        for pg_elem in root_element.ProductGroups.Group:
            product_ids = [x.text for x in pg_elem.ProductID]
            pg_to_add = {
                'group_id': pg_elem.attrib['GroupID'],
                'product_ids': product_ids,
            }

            if hasattr(pg_elem, 'Description'):
                pg_to_add['summary'] = pg_elem.Description.text

            product_groups.append(pg_to_add)

        self.csaf['product_groups'] = product_groups

    def _handle_branches_recursive(self, root_element):
        """ Recursive method for handling the branches, branch can have either list of another branches,
        or a single FullProductName inside
        """
        if not hasattr(root_element, 'Branch') and not hasattr(root_element, 'FullProductName'):
            # The ProductTree section doesn't contain Branches at all
            return None

        if hasattr(root_element, 'FullProductName'):
            # root_element is the leaf branch

            leaf_branch = {
                'name': root_element.attrib['Name'],
                'category': root_element.attrib['Type'],
                'product': self._construct_full_product_name(root_element.FullProductName)
            }

            return leaf_branch

        if hasattr(root_element, 'Branch'):
            branches = []
            for branch_elem in root_element.Branch:
                if hasattr(branch_elem, 'FullProductName'):
                    branches.append(self._handle_branches_recursive(branch_elem))
                else:
                    branches.append({
                        'name': branch_elem.attrib['Name'],
                        'category': branch_elem.attrib['Type'],
                        'branches': self._handle_branches_recursive(branch_elem)
                    })

            return branches
