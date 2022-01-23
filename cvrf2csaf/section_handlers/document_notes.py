import logging
from ..common.common import SectionHandler


class DocumentNotes(SectionHandler):
    def __init__(self, config):
        super().__init__(config=config)

        self.enum_categories = {
            'description',
            'details',
            'faq',
            'general',
            'legal_disclaimer',
            'other',
            'summary'
        }

    def _process_mandatory_and_optional(self, root_element):
        notes = []

        for elem_note in root_element.Note:

            # mandatory
            new_note = dict(
                text=elem_note.text,
                category=elem_note.get('Type'),
            )

            if new_note['category'].lower() not in self.enum_categories:
                log_msg = f'Invalid document notes category ' \
                          f'{new_note["category"]}. ' \
                          f'Should be one of: {",".join(str(x) for x in sorted(self.enum_categories))}!'
                if self.config.get('force', False):
                    logging.warn(log_msg)
                else:
                    logging.error(log_msg)

            # optional
            if elem_note.get('Audience'):
                new_note['audience'] = elem_note.get('Audience')
            if elem_note.get('Title'):
                new_note['title'] = elem_note.get('Title')

            notes.append(new_note)

        if len(notes) > 0:
            self.csaf['notes'] = notes

    def _process_mandatory_elements(self, root_element):
        return self._process_mandatory_and_optional(root_element=root_element)

    def _process_optional_elements(self, root_element):
        pass # Not used anymore.
