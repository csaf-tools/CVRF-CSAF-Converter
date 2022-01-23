import logging
from ..common.common import SectionHandler


class DocumentCategory(SectionHandler):
    def __init__(self):
        super().__init__()

        self.special_profiles = {
            'Informational Advisory',
            'security-incident-response',
            'Security Advisory',
            'veX'
        }

    def _process_mandatory_elements(self, root_element):


        # No special case
        self.csaf = root_element.text


        # 13 Validate CSAF 2.0 6.1.26 Document Category special case
        # These are Profiles in CSAF 2.0, which come with certain attributs
        # https://docs.oasis-open.org/csaf/csaf/v2.0/csd01/csaf-v2.0-csd01.html#6126-prohibited-document-category-name


        # Apply checks to remove whitespaces, brackets and so on + calculating levenshteinDistance
        def ignore_placeholder_and_case_sensitive(input):
            input = input.lower()
            input = input.strip()
            input = input.replace('_', ' ')
            input = input.replace('-', ' ')
            input = input.replace('.', ' ')
            input = input.replace('/', ' ')
            return input
        def levenshteinDistance(s1, s2):
            orig_s2 = s2
            if len(s1) > len(s2):
                s1, s2 = s2, s1

            distances = range(len(s1) + 1)
            for i2, c2 in enumerate(s2):
                distances_ = [i2 + 1]
                for i1, c1 in enumerate(s1):
                    if c1 == c2:
                        distances_.append(distances[i1])
                    else:
                        distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
                distances = distances_
            return {
                'original_profile': orig_s2,
                'distance': distances[-1]
            }

        # Apply harmonization on input
        profiles = [ignore_placeholder_and_case_sensitive(input=item) for item in self.special_profiles]
        doc_cat = ignore_placeholder_and_case_sensitive(input=self.csaf)

        # Apply harmonization on profiles
        edit_distances = [levenshteinDistance(s1=doc_cat, s2=item) for item in profiles]

        # Check edit distance
        min_edit_distance = min(edit_distances, key=lambda x:x['distance'])['distance']

        # Finally validate harmonization checks
        matching_profile = None

        if min_edit_distance < 3:
            tmp_profile = min(edit_distances, key=lambda x: x['distance'])['original_profile']
            if len(tmp_profile) > 5:
                matching_profile = tmp_profile # editdistance is only useful if original value has certain size. Not given e.g. by VEX
        elif doc_cat in profiles:
            matching_profile = doc_cat # equal

        if matching_profile is not None:
            log_msg = f'CVRF Document type \"{root_element.text}\" -> \"{doc_cat}\" is too close to one of ' \
                      f'the pre-designed Document Categories in CSAF \"{",".join(sorted(self.special_profiles))}\".'
            logging.warn(log_msg)
            self.csaf = matching_profile


    def _process_optional_elements(self, root_element):
        # Not used
        pass
