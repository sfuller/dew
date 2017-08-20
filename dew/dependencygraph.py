from typing import List


class DependencyGraphNode(object):
    def __init__(self):
        self.name = ""
        self.children = []


class DependencyGraph(object):
    def __init__(self):
        self.root = DependencyGraphNode()
        self.nodes = {}

    def add_dependency(self, name: str, parent_name: str or None):
        node = self.nodes.get(name)
        if node is None:
            node = DependencyGraphNode()
            node.name = name
            self.nodes[name] = node

        parent_node = self.root
        if parent_name:
            parent_node = self.nodes[parent_name]

        parent_node.children.append(node)

    def resolve(self) -> List[str]:
        # The dependency names in order
        deps = []

        stack = [self.root]

        while len(stack) > 0:
            node = stack.pop()
            has_child_to_resolve = False
            for child in node.children:
                if child.name not in deps:
                    has_child_to_resolve = True
                    stack.append(node)
                    stack.append(child)
                    break

            if not has_child_to_resolve:
                if node.name:
                    deps.append(node.name)

        return deps











