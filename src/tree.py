class Node:
    def __init__(self, parent=None, class_name='no name'):
        self.parent = parent
        self.class_name = class_name
        self.children = []
        self.slots = {}


class Tree:
    def __init__(self):
        self.tree_names = []
        self.classes_with_slots = []
        self.root = None

    # FIX find all nodes!
    def find_node(self, current, target):
        if current is None:
            return None
        if current.class_name == target:
            return current
        for child in current.children:
            result = self.find_node(child, target)
            if result is not None:
                return result

    def visit(self, current, level=0, slot=None, get_classes=False):
        if current is None:
            return
        if get_classes:
            if slot in current.slots.keys():
                self.classes_with_slots.append(current.class_name)
        if slot is not None and not get_classes:
            current.slots[slot] = ''
        else:
            self.tree_names.append((level, current.class_name))
        print(f'{"  " * level} {current.class_name} : {current.slots}')
        for child in current.children:
            self.visit(child, level + 1, slot, get_classes)

    def add_node(self, parent_name: str, children: list):
        parent = self.find_node(self.root, parent_name)
        if parent is None:
            parent = Node(class_name=parent_name)
            self.root = parent
            print(parent.class_name)
        if len(children) > 1:
            for node in children:
                parent.children.append(Node(parent, class_name=node))
