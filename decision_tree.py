from queue import Queue

class tree_node:
    __slots__ = ("decision", "child_nodes")

    def __init__(self, decision):
        self.decision = decision
        self.child_nodes = {}


class recursive_decision_tree:
    __slots__ = ("_root")

    def __init__(self, root=None):
        self._root = root

    def size(self):
        if not self._root:
            return 0

        def recursion(node):
            all_child_nodes = 0

            if node.child_nodes:
                all_child_nodes = len(node.child_nodes)

                def nodes_traversal(nodes, pos, current):
                    all_child_nodes = recursion(current)

                    if pos + 1 < len(nodes):
                        all_child_nodes += nodes_traversal(
                            nodes, pos + 1, nodes[pos + 1])

                    return all_child_nodes

                child_nodes_list = list(node.child_nodes.values())

                all_child_nodes += nodes_traversal(
                    child_nodes_list, 0, child_nodes_list[0])

            return all_child_nodes

        return 1 + recursion(self._root)

    def traversal(self, obj_status):
        if not self._root:
            return None

        def recursion(node):
            if not node.child_nodes:
                return node.decision

            child_key = node.decision(obj_status)

            if child_key not in node.child_nodes:
                return None

            return recursion(node.child_nodes[child_key])

        return recursion(self._root)

    def get(self, depth_level, obj_status):
        if not self._root:
            return None

        def recursion(node, current_depth):
            if current_depth >= depth_level:
                return node

            if not node.child_nodes:
                return None

            child_key = node.decision(obj_status)

            if child_key not in node.child_nodes:
                return None

            return recursion(node.child_nodes[child_key], current_depth + 1)

        return recursion(self._root, 0)

    def add(self, depth_level, obj_status, key, decision):
        if not self._root:
            if depth_level > 0:
                return None, False

            self._root = tree_node(decision)

            return self._root, True

        if depth_level == 0:
            return self._root, False

        def recursion(node, current_depth):
            if current_depth + 1 == depth_level:
                if key not in node.child_nodes:
                    node.child_nodes[key] = tree_node(decision)
                    inserted = True
                else:
                    inserted = False

                return node.child_nodes[key], inserted

            if not node.child_nodes:
                return None, False

            child_key = node.decision(obj_status)

            if child_key not in node.child_nodes:
                return None, False

            return recursion(node.child_nodes[child_key], current_depth + 1)

        return recursion(self._root, 0)


class iterative_decision_tree:
    __slots__ = ("_root")

    def __init__(self, root=None):
        self._root = root

    def size(self):
        if not self._root:
            return 0

        size = 1
        stack = Queue()
        node = self._root

        while True:
            if node.child_nodes:
                size += len(node.child_nodes)

                for child_node in reversed(list(node.child_nodes.values())):
                    stack.put_nowait(child_node)

            if stack.empty():
                return size

            node = stack.get_nowait()

    def traversal(self, obj_status):
        if not self._root:
            return None

        node = self._root

        while True:
            if not node.child_nodes:
                return node.decision

            child_key = node.decision(obj_status)

            if child_key not in node.child_nodes:
                return None

            node = node.child_nodes[child_key]

    def get(self, depth_level, obj_status):
        if not self._root:
            return None

        current_depth = 0
        node = self._root

        while True:
            if current_depth >= depth_level:
                return node

            if not node.child_nodes:
                return None

            child_key = node.decision(obj_status)

            if child_key not in node.child_nodes:
                return None

            node = node.child_nodes[child_key]
            current_depth += 1

    def add(self, depth_level, obj_status, key, decision):
        if not self._root:
            if depth_level > 0:
                return None, False

            self._root = tree_node(decision)

            return self._root, True

        if depth_level == 0:
            return self._root, False

        current_depth = 0
        node = self._root

        while True:
            if current_depth + 1 == depth_level:
                if key not in node.child_nodes:
                    node.child_nodes[key] = tree_node(decision)
                    inserted = True
                else:
                    inserted = False

                return node.child_nodes[key], inserted

            if not node.child_nodes:
                return None, False

            child_key = node.decision(obj_status)

            if child_key not in node.child_nodes:
                return None, False

            node = node.child_nodes[child_key]
            current_depth += 1
