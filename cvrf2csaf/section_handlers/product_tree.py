import logging
from ..common.common import SectionHandler


class ProductTree(SectionHandler):
    """ Responsible for converting the ProductTree section """
    branch_type_mapping = {
        "Vendor": 'vendor',
        "Product Family": 'product_family',
        "Product Name": 'product_name',
        "Product Version": 'product_version',
        "Patch Level": 'patch_level',
        "Service Pack": 'service_pack',
        "Architecture": 'architecture',
        "Language": 'language',
        "Legacy": 'legacy',
        "Specification": 'specification',
        "Host Name": 'host_name',

        # These types do not exist in CSAF, agreed to convert it to product_name
        # https://github.com/csaf-tools/CVRF-CSAF-Converter/pull/54#discussion_r805860658
        "Realm": 'product_name',
        "Resource": 'product_name',
    }

    relation_type_mapping = {
        'Default Component Of': 'default_component_of',
        'Optional Component Of': 'optional_component_of',
        'External Component Of': 'external_component_of',
        'Installed On': 'installed_on',
        'Installed With': 'installed_with',
    }

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
    def _get_full_product_name(fpn_elem) -> dict:
        fpn = {
            'product_id': fpn_elem.attrib['ProductID'],
            'name': fpn_elem.text
        }

        if fpn_elem.attrib.get('CPE'):
            fpn['product_identification_helper'] = {'cpe': fpn_elem.attrib['CPE']}

        return fpn


    @classmethod
    def _get_branch_type(cls, branch_type: str):
        if branch_type in ['Realm', 'Resource']:
            logging.warning(f'Input branch type {branch_type} is no longer supported in CSAF. '
                            'Converting to product_name')

        return cls.branch_type_mapping[branch_type]


    def _handle_full_product_names(self, root_element):
        if not hasattr(root_element, 'FullProductName'):
            return

        full_product_names = []
        for fpn_elem in root_element.FullProductName:
            full_product_names.append(self._get_full_product_name(fpn_elem))

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
                'category': self.relation_type_mapping[rel_elem.attrib['RelationType']],
                'product_reference': rel_elem.attrib['ProductReference'],
                'relates_to_product_reference': rel_elem.attrib['RelatesToProductReference'],
                'full_product_name': self._get_full_product_name(first_prod_name)
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

        if 'Branch' in root_element.tag and hasattr(root_element, 'FullProductName'):
            # Make sure we are inside a Branch (and not in the top ProductTree element, where FullProductName can occur)
            # then root_element is the leaf branch

            leaf_branch = {
                'name': root_element.attrib['Name'],
                'category': self._get_branch_type(root_element.attrib['Type']),
                'product': self._get_full_product_name(root_element.FullProductName)
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
                        'category': self._get_branch_type(branch_elem.attrib['Type']),
                        'branches': self._handle_branches_recursive(branch_elem)
                    })

            return branches
