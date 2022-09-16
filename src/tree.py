import graphviz as gv


class Node:
    def __init__(self, parent=None, class_name='no name', is_instance=False):
        self.is_instance = is_instance
        self.parent = parent
        self.class_name = class_name
        self.children = []
        self.slots = {}


class Tree:
    convert = {
        'int': (lambda x: int(x)),
        'float': (lambda x: float(x)),
        'string': (lambda x: str(x))
    }

    def __init__(self):
        self.tree_names = []
        self.classes_with_slots = []
        self.query_result = []
        self.ancestors = []
        self.root = None
        self.image = gv.Digraph()
        self.image.format = 'png'
        self.image_nodes = []

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

    def visit(self, current, level=0, slot=None, get_classes=False, query=False, mode=None, value=None):
        if current is None:
            return
        if query:
            if current.is_instance:
                print(current.slots)
                for k, v in current.slots.items():
                    if isinstance(current.slots[k], tuple):
                        current.slots[k] = Tree.convert.get(v[1])(v[0])
                if mode == 'больше':
                    if current.slots[slot] > value:
                        self.query_result.append(current)
                if mode == 'меньше':
                    if current.slots[slot] < value:
                        self.query_result.append(current)
                if mode == 'равен':
                    if current.slots[slot] == value:
                        self.query_result.append(current)
        if get_classes:
            if slot[0] in current.slots.keys() and not current.is_instance:
                self.classes_with_slots.append(current.class_name)
        if slot is not None and not get_classes and not query:
            current.slots[slot[0]] = slot[1]
        elif slot is None and not current.is_instance:
            self.tree_names.append((level, current.class_name))
        print(f'{"  " * level} {current.class_name} : {current.slots}')
        for child in current.children:
            self.visit(child, level + 1, slot, get_classes, query, mode, value)

    def add_node(self, parent_name: str, children: list):
        parent = self.find_node(self.root, parent_name)
        if parent is None:
            parent = Node(class_name=parent_name)
            self.root = parent
            print(parent.class_name)
        if len(children) > 1:
            for node in children:
                parent.children.append(Node(parent, class_name=node))

    def find_ancestors(self, current):
        if current is None:
            return
        if not current.is_instance:
            self.ancestors.append(current.class_name)
        self.find_ancestors(current.parent)

    def build_graph(self, current):
        if current is None:
            return
        if current.class_name not in self.image_nodes:
            self.image.node(current.class_name, current.class_name)
            self.image_nodes.append(current.class_name)
        for child in current.children:
            if child.class_name not in self.image_nodes:
                self.image.node(child.class_name, child.class_name)
                self.image_nodes.append(child.class_name)
            self.image.edge(current.class_name, child.class_name)
            self.build_graph(child)
