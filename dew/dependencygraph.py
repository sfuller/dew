from typing import Dict, List, Optional


class DependencyGraphNode(object):
    def __init__(self, name: str):
        self.name = name
        self.children: List[DependencyGraphNode] = []
        self.parent: DependencyGraphNode = None


class DependencyGraph(object):
    def __init__(self):
        self.root = DependencyGraphNode('')
        self.nodes: Dict[str, DependencyGraphNode] = {}

    def add_dependency(self, name: str, parent_name: Optional[str]):
        node = self.nodes.get(name)
        if node is None:
            node = DependencyGraphNode(name)
            self.nodes[name] = node

        parent_node = self.root
        if parent_name:
            parent_node = self.nodes[parent_name]

        parent_node.children.append(node)
        node.parent = parent_node

    def resolve(self) -> List[str]:
        # The dependency names in order
        deps: List[str] = []

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
