import typing

class SectionHandler:
    def parse(self, root_element):
        # Get everything from the subsections (recursively)
        for class_attr in self.__dict__.values():
            if isinstance(class_attr, SectionHandler) or isinstance(class_attr, LeafElement): # or isinstance(class_attr, LeafAttribute):
                child_element = root_element.find('{*}' + f'{class_attr.__class__.__name__}')
                class_attr.parse(child_element)

            if isinstance(class_attr, list):
                list_type = class_attr.pop()
                for elem in root_element:
                    x = list_type()
                    x.parse(elem)
                    class_attr.append(x)


class LeafAttribute:
    def parse(self, root_element):
        pass



class LeafElement:
    min_occurs = None
    max_occurs = None
    type = None
    extension = None

    def parse(self, root_element):
        self.text = None

        # TODO: Validate min_occurs
        if root_element is None:
            return

        self.text = root_element.text

        # print('x')
        # TODO: occurence, type, extension validation
        # if len(self.element) < self.min_occurs:
        #     pass

