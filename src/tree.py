class Node:
    def __init__(self, parent=None, **slots):
        self.parent = parent
        self.children = []
        self.slots = slots


class Tree:
    def __init__(self):
        self.tree_names = []
        self.root = None

    # FIX find all nodes!
    def find_node(self, current, target):
        if current is None:
            return None
        if current.slots.get('name') == target:
            return current
        for child in current.children:
            result = self.find_node(child, target)
            if result is not None:
                return result

    def visit(self, current, level=0, **kwargs):
        if current is None:
            return
        self.tree_names.append((level, current.slots.get('name')))
        print(f'{"  " * level}{current.slots.get("name", "no name")}')
        for child in current.children:
            self.visit(child, level + 1)

    def add_node(self, parent_name: str, children: list):
        parent = self.find_node(self.root, parent_name)
        if parent is None:
            parent = Node(name=parent_name)
            self.root = parent
            print(parent.slots.get('name'))
        if len(children) > 1:
            for node in children:
                parent.children.append(Node(parent, name=node))
