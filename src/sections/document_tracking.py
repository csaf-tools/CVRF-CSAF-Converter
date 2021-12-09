
from src.common.common import SectionHandler, LeafAttribute, LeafElement
from src.common.extensions import LocalizedString
from src.common.types import DocumentStatusEnumType

from typing import List

# ------------------- Section Handlers --------------------------------


class DocumentTracking(SectionHandler):
    min_occurs = 1
    max_occurs = 1

    # TODO: Stress that SH cant have these
    # type = None
    # extension = None

    def __init__(self):
        self.identification = self.Identification()
        self.status = self.Status()
        self.revision_history = self.RevisionHistory()

    def create_json(self):
        json = {}

        json['id'] = self.identification.id.text
        json['alias'] = self.identification.alias.text

        json['status'] = self.status.text

        json['revision_history'] = []
        for revision in self.revision_history.revisions:
            json['revision_history'].append(revision.date.text)

        return json


    class Status(LeafElement):
        min_occurs = 1
        max_occurs = 1
        type = DocumentStatusEnumType
        extension = None

    class RevisionHistory(SectionHandler):
        min_occurs = 1
        max_occurs = 1

        def __init__(self):
            self.revisions = [self.Revision]


        class Revision(SectionHandler):
            def __init__(self):
                self.number = self.Number()
                self.date = self.Date()
                self.description = self.Description()

            class Number(LeafElement):
                pass

            class Date(LeafElement):
                pass

            class Description(LeafElement):
                pass



    class Identification(SectionHandler):
        def __init__(self):
            self.alias = self.Alias()
            self.id = self.ID()

        class Alias(LeafElement):
            min_occurs = 0
            max_occurs = float('inf')
            type = None
            extension = LocalizedString

        class ID(LeafElement):
            min_occurs = 1
            max_occurs = 1
            type = None
            extension = LocalizedString




# ------------------- LEAF elements/attributes ------------------------

