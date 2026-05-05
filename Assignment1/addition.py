import csv
import random
import time
from pathlib import Path

import implement
from implement import BPTree


STORAGE = []
DEBUG_MODE = 0
RANDOM_SEED = 42
SEARCH_COUNT = 10000
DELETE_COUNT = 2000
RANGE_LOW = 202000000
RANGE_HIGH = 202099999
RUN_COUNT = 10


class Layered_BPNode:
    def __init__(self, is_leaf=1):
        self.is_leaf = is_leaf
        self.keys = []
        self.children = []
        self.rids = []
        self.next = None


class Layered_BPTree:
    def __init__(self, di, dl):
        if di < 3 or dl < 3:
            raise ValueError("orders di and dl must be at least 3")
        self.di = di
        self.dl = dl
        self.min_keys_inner = (di - 1) // 2
        self.min_keys_leaf = dl // 2
        self.max_keys_inner = di - 1
        self.max_keys_leaf = dl - 1
        self.root = Layered_BPNode(is_leaf=1)
        self.node_count = 0
        self.key_count = 0
        self.split_count = 0
        self.utilization = 0.0

    def STATUS(self):
        self.node_count = 0
        self.key_count = 0
        capacity = self._travel(self.root)
        self.utilization = (self.key_count / capacity * 100) if capacity else 0.0
        if implement.DEBUG:
            print(
                f"[STATUS()]: nodes={self.node_count}, keys={self.key_count}, "
                f"util={self.utilization:.2f}%"
            )
        return self.node_count, self.utilization

    def _travel(self, node):
        if node is None:
            return 0
        self.node_count += 1
        self.key_count += len(node.keys)
        capacity = self.max_keys_leaf if node.is_leaf else self.max_keys_inner
        if node.is_leaf:
            return capacity
        for child in node.children:
            capacity += self._travel(child)
        return capacity

    def search(self, key):
        node = self.root
        while not node.is_leaf:
            i = 0
            while i < len(node.keys) and key >= node.keys[i]:
                i += 1
            node = node.children[i]
        rid = None
        if key in node.keys:
            rid = node.rids[node.keys.index(key)]
        if implement.DEBUG:
            print(f"[search()]: key={key}, rid={rid}")
        return rid

    def range_query(self, low, high):
        if low > high:
            return []
        result = []
        node = self.root
        while not node.is_leaf:
            i = 0
            while i < len(node.keys) and low >= node.keys[i]:
                i += 1
            node = node.children[i]
        while node is not None:
            for i, key in enumerate(node.keys):
                if key > high:
                    if implement.DEBUG:
                        print(f"[range_query()]: low={low}, high={high}, count={len(result)}")
                    return result
                if key >= low:
                    result.append(node.rids[i])
            node = node.next
        if implement.DEBUG:
            print(f"[range_query()]: low={low}, high={high}, count={len(result)}")
        return result

    def insert(self, key, rid):
        self._insert(self.root, key, rid)
        if len(self.root.keys) > self.max_keys_for(self.root):
            old_root = self.root
            new_root = Layered_BPNode(is_leaf=0)
            new_root.children.append(old_root)
            self.root = new_root
            self._split(new_root, 0, old_root)
        if implement.DEBUG:
            print(
                f"[insert()]: key={key}, rid={rid}, root_keys={len(self.root.keys)}, "
                f"splits={self.split_count}"
            )

    def delete(self, key):
        self._delete(self.root, key)
        if not self.root.is_leaf and len(self.root.keys) == 0:
            self.root = self.root.children[0]
        if implement.DEBUG:
            print(f"[delete()]: key={key}, root_keys={len(self.root.keys)}")

    def max_keys_for(self, node):
        return self.max_keys_leaf if node.is_leaf else self.max_keys_inner

    def min_keys_for(self, node):
        return self.min_keys_leaf if node.is_leaf else self.min_keys_inner

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
        if len(node.children[i].keys) > self.max_keys_for(node.children[i]):
            self._split(node, i, node.children[i])

    def _split(self, parent, index, child):
        if child.is_leaf:
            mid = (self.dl + 1) // 2
            new_node = Layered_BPNode(is_leaf=1)
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
            new_node = Layered_BPNode(is_leaf=0)
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
        if len(child.keys) < self.min_keys_for(child):
            self._recover(node, i)

    def _recover(self, parent, index):
        child = parent.children[index]
        if child.is_leaf:
            self._recover_leaf(parent, index, child)
            return
        self._recover_inner(parent, index, child)

    def _recover_leaf(self, parent, index, child):
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


class Student:
    def __init__(self, sid, name, gender, gpa, height, weight):
        self.sid = int(sid)
        self.name = name
        self.gender = gender
        self.gpa = float(gpa)
        self.height = float(height)
        self.weight = float(weight)


def load_students(csv_path):
    STORAGE.clear()
    with open(csv_path, "r", encoding="utf-8", newline="") as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            STORAGE.append(Student(*row))


def elapsed_ms(start, end):
    return (end - start) * 1000


def summarize_records(rids):
    male = []
    for rid in rids:
        student = STORAGE[rid]
        if student.gender == "Male":
            male.append(student)
    avg_gpa = sum(student.gpa for student in male) / len(male) if male else 0.0
    avg_height = sum(student.height for student in male) / len(male) if male else 0.0
    return len(male), avg_gpa, avg_height


def TEST(tree):
    report = {}
    random.seed(RANDOM_SEED)

    start = time.perf_counter()
    for rid, student in enumerate(STORAGE):
        tree.insert(student.sid, rid)
    end = time.perf_counter()
    node_count, utilization = tree.STATUS()

    report["insert_ms"] = elapsed_ms(start, end)
    report["split_count"] = tree.split_count
    report["node_count"] = node_count
    report["utilization"] = utilization

    all_keys = [student.sid for student in STORAGE]
    search_keys = random.sample(all_keys, min(SEARCH_COUNT, len(all_keys)))

    start = time.perf_counter()
    found = 0
    for key in search_keys:
        if tree.search(key) is not None:
            found += 1
    end = time.perf_counter()
    report["search_ms"] = elapsed_ms(start, end)
    report["search_found"] = found

    start = time.perf_counter()
    rids = tree.range_query(RANGE_LOW, RANGE_HIGH)
    end = time.perf_counter()
    male_count, avg_gpa, avg_height = summarize_records(rids)
    report["range_ms"] = elapsed_ms(start, end)
    report["range_count"] = len(rids)
    report["male_count"] = male_count
    report["male_avg_gpa"] = avg_gpa
    report["male_avg_height"] = avg_height

    delete_keys = search_keys[:min(DELETE_COUNT, len(search_keys))]
    start = time.perf_counter()
    deleted = 0
    for key in delete_keys:
        if tree.search(key) is not None:
            tree.delete(key)
            deleted += 1
    end = time.perf_counter()
    node_count, utilization = tree.STATUS()

    report["delete_ms"] = elapsed_ms(start, end)
    report["delete_count"] = deleted
    report["node_count_after_delete"] = node_count
    report["utilization_after_delete"] = utilization

    return report


def print_report(name, report):
    print(f"[{name}]")
    print(f"insert total: {report['insert_ms']:.6f} ms")
    print(f"search total: {report['search_ms']:.6f} ms, found={report['search_found']}")
    print(f"range total: {report['range_ms']:.6f} ms, key=[{RANGE_LOW}, {RANGE_HIGH}], count={report['range_count']}")
    print(f"delete total: {report['delete_ms']:.6f} ms, deleted={report['delete_count']}")
    print(f"splits: {report['split_count']}")
    print(f"nodes: {report['node_count']}")
    print(f"util: {report['utilization']:.6f}%")
    print(
        "record(male): "
        f"count={report['male_count']}, "
        f"avg_gpa={report['male_avg_gpa']:.6f}, "
        f"avg_height={report['male_avg_height']:.6f}"
    )
    print()


def average_reports(reports):
    averaged = {}
    keys = reports[0].keys()
    for key in keys:
        values = [report[key] for report in reports]
        averaged[key] = sum(values) / len(values)
    return averaged


def main():
    implement.DEBUG = DEBUG_MODE

    csv_path = Path(__file__).with_name("student.csv")
    load_students(csv_path)
    print(f"Loaded {len(STORAGE)} records")
    print()

    #Comparison between B+-tree orders and two asymmetric layered B+-tree.
    tree_cases = [
        ("B+-tree, d=10", lambda: BPTree(d=10)),
        ("B+-tree, d=20", lambda: BPTree(d=20)),
        ("B+-tree, d=30", lambda: BPTree(d=30)),
        ("Layered_B+-tree, di=10, dl=30", lambda: Layered_BPTree(di=10, dl=30)),
        ("Layered_B+-tree, di=30, dl=10", lambda: Layered_BPTree(di=30, dl=10)),
    ]

    print(f"Repeat count per tree: {RUN_COUNT}")
    print()

    for name, tree_factory in tree_cases:
        reports = []
        for _ in range(RUN_COUNT): #Repeat cases for accuracy of experiment.
            report = TEST(tree_factory())
            reports.append(report)
        print_report(f"{name} | average of {RUN_COUNT} runs", average_reports(reports))


if __name__ == "__main__":
    main()
