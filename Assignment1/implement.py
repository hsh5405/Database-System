#Control public debug logs
DEBUG = 0


class BNode:
    def __init__(self, is_leaf=1):
        self.is_leaf = is_leaf
        self.keys = []
        self.rids = []
        self.children = []


class BTree:
    def __init__(self, d):
        if d < 3:
            raise ValueError("order d must be at least 3")
        self.d = d
        self.min_keys = (d - 1) // 2
        self.max_keys = d - 1
        self.root = BNode(is_leaf=1)
        self.node_count = 0
        self.key_count = 0
        self.split_count = 0
        self.utilization = 0.0

    def STATUS(self):
        #Refresh structural metrics
        self.node_count = 0
        self.key_count = 0
        self._travel(self.root)
        capacity = self.node_count * self.max_keys
        self.utilization = (self.key_count / capacity * 100) if capacity else 0.0
        if DEBUG:
            print(f"[STATUS()]: nodes={self.node_count}, keys={self.key_count}, util={self.utilization:.2f}%")
        return self.node_count, self.utilization

    def _travel(self, node):
        if node is None:
            return
        self.node_count += 1
        self.key_count += len(node.keys)
        if node.is_leaf:
            return
        for child in node.children:
            self._travel(child)

    def search(self, key):
        rid = self._search(self.root, key)
        if DEBUG:
            print(f"[search()]: key={key}, rid={rid}")
        return rid

    def range_query(self, low, high):
        if low > high:
            return []
        result = []
        self._range(self.root, low, high, result)
        if DEBUG:
            print(f"[range_query()]: low={low}, high={high}, count={len(result)}")
        return result

    def insert(self, key, rid):
        self._insert(self.root, key, rid)
        if len(self.root.keys) > self.max_keys:
            #Grow root after overflow
            old_root = self.root
            new_root = BNode(is_leaf=0)
            new_root.children.append(old_root)
            self.root = new_root
            self._split(new_root, 0, old_root)
        if DEBUG:
            print(f"[insert()]: key={key}, rid={rid}, root_keys={len(self.root.keys)}, splits={self.split_count}")

    def delete(self, key):
        self._delete(self.root, key)
        if not self.root.is_leaf and len(self.root.keys) == 0:
            self.root = self.root.children[0]
        if DEBUG:
            print(f"[delete()]: key={key}, root_keys={len(self.root.keys)}")

    def _search(self, node, key):
        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1
        if i < len(node.keys) and node.keys[i] == key:
            return node.rids[i]
        if node.is_leaf:
            return None
        return self._search(node.children[i], key)

    def _range(self, node, low, high, result):
        i = 0
        while i < len(node.keys) and node.keys[i] < low:
            i += 1
        while i < len(node.keys) and node.keys[i] <= high:
            if not node.is_leaf:
                self._range(node.children[i], low, high, result)
            result.append(node.rids[i])
            i += 1
        if not node.is_leaf:
            self._range(node.children[i], low, high, result)

    def _insert(self, node, key, rid):
        if node.is_leaf:
            i = len(node.keys) - 1
            while i >= 0 and node.keys[i] > key:
                i -= 1
            node.keys.insert(i + 1, key)
            node.rids.insert(i + 1, rid)
            return
        i = len(node.keys) - 1
        while i >= 0 and node.keys[i] > key:
            i -= 1
        child_index = i + 1
        self._insert(node.children[child_index], key, rid)
        if len(node.children[child_index].keys) > self.max_keys:
            self._split(node, child_index, node.children[child_index])

    def _split(self, parent, index, child):
        #Promote middle entry
        mid = len(child.keys) // 2
        new_node = BNode(is_leaf=child.is_leaf)
        sep_key = child.keys[mid]
        sep_rid = child.rids[mid]

        new_node.keys = child.keys[mid + 1:]
        new_node.rids = child.rids[mid + 1:]
        child.keys = child.keys[:mid]
        child.rids = child.rids[:mid]

        if not child.is_leaf:
            new_node.children = child.children[mid + 1:]
            child.children = child.children[:mid + 1]

        parent.keys.insert(index, sep_key)
        parent.rids.insert(index, sep_rid)
        parent.children.insert(index + 1, new_node)
        self.split_count += 1

    def _delete(self, node, key):
        i = 0
        while i < len(node.keys) and node.keys[i] < key:
            i += 1
        if node.is_leaf:
            if i < len(node.keys) and node.keys[i] == key:
                node.keys.pop(i)
                node.rids.pop(i)
            return
        if i < len(node.keys) and node.keys[i] == key:
            #Replace internal key with predecessor
            pred_key, pred_rid = self._predecessor(node.children[i])
            node.keys[i] = pred_key
            node.rids[i] = pred_rid
            self._delete(node.children[i], pred_key)
            if len(node.children[i].keys) < self.min_keys:
                self._recover(node, i)
            return
        self._delete(node.children[i], key)
        if len(node.children[i].keys) < self.min_keys:
            self._recover(node, i)

    def _predecessor(self, node):
        while not node.is_leaf:
            node = node.children[-1]
        return node.keys[-1], node.rids[-1]

    def _recover(self, parent, index):
        child = parent.children[index]
        #Borrow before merging
        if index > 0:
            left = parent.children[index - 1]
            if len(left.keys) > self.min_keys:
                child.keys.insert(0, parent.keys[index - 1])
                child.rids.insert(0, parent.rids[index - 1])
                parent.keys[index - 1] = left.keys.pop()
                parent.rids[index - 1] = left.rids.pop()
                if not left.is_leaf:
                    child.children.insert(0, left.children.pop())
                return
        if index < len(parent.children) - 1:
            right = parent.children[index + 1]
            if len(right.keys) > self.min_keys:
                child.keys.append(parent.keys[index])
                child.rids.append(parent.rids[index])
                parent.keys[index] = right.keys.pop(0)
                parent.rids[index] = right.rids.pop(0)
                if not right.is_leaf:
                    child.children.append(right.children.pop(0))
                return
        if index > 0:
            sep_index = index - 1
            left = parent.children[sep_index]
            left.keys += [parent.keys[sep_index]] + child.keys
            left.rids += [parent.rids[sep_index]] + child.rids
            if not left.is_leaf:
                left.children += child.children
            parent.keys.pop(sep_index)
            parent.rids.pop(sep_index)
            parent.children.pop(index)
            return
        right = parent.children[index + 1]
        child.keys += [parent.keys[index]] + right.keys
        child.rids += [parent.rids[index]] + right.rids
        if not child.is_leaf:
            child.children += right.children
        parent.keys.pop(index)
        parent.rids.pop(index)
        parent.children.pop(index + 1)


class BSNode:
    def __init__(self, is_leaf=1):
        self.is_leaf = is_leaf
        self.keys = []
        self.rids = []
        self.children = []


class BSTree(BTree):
    def __init__(self, d):
        if d < 3:
            raise ValueError("order d must be at least 3")
        self.d = d
        self.min_keys = (d - 1) // 2
        self.max_keys = d - 1
        self.root = BSNode(is_leaf=1)
        self.node_count = 0
        self.key_count = 0
        self.split_count = 0
        self.utilization = 0.0

    def insert(self, key, rid):
        self._insert(self.root, key, rid)
        if len(self.root.keys) > self.max_keys:
            #Use plain split for root overflow
            old_root = self.root
            new_root = BSNode(is_leaf=0)
            new_root.children.append(old_root)
            self.root = new_root
            self._plain_split(new_root, 0, old_root)
        if DEBUG:
            print(f"[insert()]: key={key}, rid={rid}, root_keys={len(self.root.keys)}, splits={self.split_count}")

    def _insert(self, node, key, rid):
        if node.is_leaf:
            i = len(node.keys) - 1
            while i >= 0 and node.keys[i] > key:
                i -= 1
            node.keys.insert(i + 1, key)
            node.rids.insert(i + 1, rid)
            return
        i = len(node.keys) - 1
        while i >= 0 and node.keys[i] > key:
            i -= 1
        child_index = i + 1
        self._insert(node.children[child_index], key, rid)
        if len(node.children[child_index].keys) > self.max_keys:
            self._rearrange(node, child_index)

    def _rearrange(self, parent, index):
        overflow_child = parent.children[index]
        left = parent.children[index - 1] if index > 0 else None
        right = parent.children[index + 1] if index < len(parent.children) - 1 else None

        #Prefer redistribution before adding nodes
        if left is not None and len(left.keys) < self.max_keys:
            self._redistribute(parent, index - 1, left, overflow_child)
            return
        if right is not None and len(right.keys) < self.max_keys:
            self._redistribute(parent, index, overflow_child, right)
            return
        if left is not None:
            self._split_2to3(parent, index - 1, left, overflow_child)
            return
        if right is not None:
            self._split_2to3(parent, index, overflow_child, right)
            return
        self._plain_split(parent, index, overflow_child)

    def _redistribute(self, parent, left_index, left, right):
        all_keys = left.keys + [parent.keys[left_index]] + right.keys
        all_rids = left.rids + [parent.rids[left_index]] + right.rids
        mid = len(all_keys) // 2

        left.keys = all_keys[:mid]
        left.rids = all_rids[:mid]
        parent.keys[left_index] = all_keys[mid]
        parent.rids[left_index] = all_rids[mid]
        right.keys = all_keys[mid + 1:]
        right.rids = all_rids[mid + 1:]

        if not left.is_leaf:
            all_children = left.children + right.children
            left.children = all_children[:mid + 1]
            right.children = all_children[mid + 1:]

    def _split_2to3(self, parent, left_index, left, right):
        #Spread two siblings into three nodes
        all_keys = left.keys + [parent.keys[left_index]] + right.keys
        all_rids = left.rids + [parent.rids[left_index]] + right.rids
        total = len(all_keys)
        s1 = total // 3
        s2 = 2 * total // 3

        mid_node = BSNode(is_leaf=left.is_leaf)
        left.keys = all_keys[:s1]
        left.rids = all_rids[:s1]
        mid_node.keys = all_keys[s1 + 1:s2]
        mid_node.rids = all_rids[s1 + 1:s2]
        right.keys = all_keys[s2 + 1:]
        right.rids = all_rids[s2 + 1:]

        if not left.is_leaf:
            all_children = left.children + right.children
            left.children = all_children[:s1 + 1]
            mid_node.children = all_children[s1 + 1:s2 + 1]
            right.children = all_children[s2 + 1:]

        parent.keys[left_index] = all_keys[s1]
        parent.rids[left_index] = all_rids[s1]
        parent.keys.insert(left_index + 1, all_keys[s2])
        parent.rids.insert(left_index + 1, all_rids[s2])
        parent.children.insert(left_index + 1, mid_node)
        self.split_count += 1

    def _plain_split(self, parent, index, child):
        #Fallback to normal B-tree split
        mid = len(child.keys) // 2
        new_node = BSNode(is_leaf=child.is_leaf)
        sep_key = child.keys[mid]
        sep_rid = child.rids[mid]

        new_node.keys = child.keys[mid + 1:]
        new_node.rids = child.rids[mid + 1:]
        child.keys = child.keys[:mid]
        child.rids = child.rids[:mid]

        if not child.is_leaf:
            new_node.children = child.children[mid + 1:]
            child.children = child.children[:mid + 1]

        parent.keys.insert(index, sep_key)
        parent.rids.insert(index, sep_rid)
        parent.children.insert(index + 1, new_node)
        self.split_count += 1


class BPNode:
    def __init__(self, is_leaf=1):
        self.is_leaf = is_leaf
        self.keys = []
        self.children = []
        self.rids = []
        self.next = None


class BPTree:
    def __init__(self, d):
        if d < 3:
            raise ValueError("order d must be at least 3")
        self.d = d
        self.min_keys_inner = (d - 1) // 2
        self.min_keys_leaf = d // 2
        self.max_keys = d - 1
        self.root = BPNode(is_leaf=1)
        self.node_count = 0
        self.key_count = 0
        self.split_count = 0
        self.utilization = 0.0

    def STATUS(self):
        #Refresh structural metrics
        self.node_count = 0
        self.key_count = 0
        self._travel(self.root)
        capacity = self.node_count * self.max_keys
        self.utilization = (self.key_count / capacity * 100) if capacity else 0.0
        if DEBUG:
            print(f"[STATUS()]: nodes={self.node_count}, keys={self.key_count}, util={self.utilization:.2f}%")
        return self.node_count, self.utilization

    def _travel(self, node):
        if node is None:
            return
        self.node_count += 1
        self.key_count += len(node.keys)
        if node.is_leaf:
            return
        for child in node.children:
            self._travel(child)

    def search(self, key):
        node = self.root
        #Route equal separators to the right child
        while not node.is_leaf:
            i = 0
            while i < len(node.keys) and key >= node.keys[i]:
                i += 1
            node = node.children[i]
        rid = None
        if key in node.keys:
            rid = node.rids[node.keys.index(key)]
        if DEBUG:
            print(f"[search()]: key={key}, rid={rid}")
        return rid

    def range_query(self, low, high):
        if low > high:
            return []
        result = []
        node = self.root
        #Start scan from target leaf
        while not node.is_leaf:
            i = 0
            while i < len(node.keys) and low >= node.keys[i]:
                i += 1
            node = node.children[i]
        while node is not None:
            for i, key in enumerate(node.keys):
                if key > high:
                    if DEBUG:
                        print(f"[range_query()]: low={low}, high={high}, count={len(result)}")
                    return result
                if key >= low:
                    result.append(node.rids[i])
            node = node.next
        if DEBUG:
            print(f"[range_query()]: low={low}, high={high}, count={len(result)}")
        return result

    def insert(self, key, rid):
        self._insert(self.root, key, rid)
        if len(self.root.keys) > self.max_keys:
            #Grow root after overflow
            old_root = self.root
            new_root = BPNode(is_leaf=0)
            new_root.children.append(old_root)
            self.root = new_root
            self._split(new_root, 0, old_root)
        if DEBUG:
            print(f"[insert()]: key={key}, rid={rid}, root_keys={len(self.root.keys)}, splits={self.split_count}")

    def delete(self, key):
        self._delete(self.root, key)
        if not self.root.is_leaf and len(self.root.keys) == 0:
            self.root = self.root.children[0]
        if DEBUG:
            print(f"[delete()]: key={key}, root_keys={len(self.root.keys)}")

    def _insert(self, node, key, rid):
        if node.is_leaf:
            i = len(node.keys) - 1
            while i >= 0 and node.keys[i] > key:
                i -= 1
            node.keys.insert(i + 1, key)
            node.rids.insert(i + 1, rid)
            return
        i = 0
        while i < len(node.keys) and key >= node.keys[i]:
            i += 1
        self._insert(node.children[i], key, rid)
        if len(node.children[i].keys) > self.max_keys:
            self._split(node, i, node.children[i])

    def _split(self, parent, index, child):
        if child.is_leaf:
            #Keep copied separator in leaf
            mid = (self.d + 1) // 2
            new_node = BPNode(is_leaf=1)
            new_node.keys = child.keys[mid:]
            new_node.rids = child.rids[mid:]
            child.keys = child.keys[:mid]
            child.rids = child.rids[:mid]
            new_node.next = child.next
            child.next = new_node
            parent.keys.insert(index, new_node.keys[0])
            parent.children.insert(index + 1, new_node)
        else:
            mid = len(child.keys) // 2
            new_node = BPNode(is_leaf=0)
            push_key = child.keys[mid]
            new_node.keys = child.keys[mid + 1:]
            new_node.children = child.children[mid + 1:]
            child.keys = child.keys[:mid]
            child.children = child.children[:mid + 1]
            parent.keys.insert(index, push_key)
            parent.children.insert(index + 1, new_node)
        self.split_count += 1

    def _delete(self, node, key):
        if node.is_leaf:
            if key in node.keys:
                i = node.keys.index(key)
                node.keys.pop(i)
                node.rids.pop(i)
            return
        i = 0
        while i < len(node.keys) and key >= node.keys[i]:
            i += 1
        self._delete(node.children[i], key)
        child = node.children[i]
        min_keys = self.min_keys_leaf if child.is_leaf else self.min_keys_inner
        if len(child.keys) < min_keys:
            self._recover(node, i)

    def _recover(self, parent, index):
        child = parent.children[index]
        #Choose leaf or internal recovery
        if child.is_leaf:
            self._recover_leaf(parent, index, child)
            return
        self._recover_inner(parent, index, child)

    def _recover_leaf(self, parent, index, child):
        #Repair leaf occupancy and links
        if index > 0:
            left = parent.children[index - 1]
            if len(left.keys) > self.min_keys_leaf:
                child.keys.insert(0, left.keys.pop())
                child.rids.insert(0, left.rids.pop())
                parent.keys[index - 1] = child.keys[0]
                return
        if index < len(parent.children) - 1:
            right = parent.children[index + 1]
            if len(right.keys) > self.min_keys_leaf:
                child.keys.append(right.keys.pop(0))
                child.rids.append(right.rids.pop(0))
                parent.keys[index] = right.keys[0]
                return
        if index < len(parent.children) - 1:
            right = parent.children[index + 1]
            child.keys += right.keys
            child.rids += right.rids
            child.next = right.next
            parent.keys.pop(index)
            parent.children.pop(index + 1)
            return
        left = parent.children[index - 1]
        left.keys += child.keys
        left.rids += child.rids
        left.next = child.next
        parent.keys.pop(index - 1)
        parent.children.pop(index)

    def _recover_inner(self, parent, index, child):
        #Repair internal routing keys
        if index > 0:
            left = parent.children[index - 1]
            if len(left.keys) > self.min_keys_inner:
                child.keys.insert(0, parent.keys[index - 1])
                parent.keys[index - 1] = left.keys.pop()
                child.children.insert(0, left.children.pop())
                return
        if index < len(parent.children) - 1:
            right = parent.children[index + 1]
            if len(right.keys) > self.min_keys_inner:
                child.keys.append(parent.keys[index])
                parent.keys[index] = right.keys.pop(0)
                child.children.append(right.children.pop(0))
                return
        if index < len(parent.children) - 1:
            right = parent.children[index + 1]
            child.keys += [parent.keys.pop(index)] + right.keys
            child.children += right.children
            parent.children.pop(index + 1)
            return
        left = parent.children[index - 1]
        left.keys += [parent.keys.pop(index - 1)] + child.keys
        left.children += child.children
        parent.children.pop(index)
