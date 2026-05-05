import csv
import random
import time
from pathlib import Path

import implement
from implement import BTree, BSTree, BPTree


STORAGE = []
DEBUG_MODE = 0 #Set 1 to debug logs for small sample
ORDER_VALUES = [3, 5, 10]
RANDOM_SEED = 42
SEARCH_COUNT = 10000
DELETE_COUNT = 2000
RANGE_LOW = 202000000
RANGE_HIGH = 202099999
RUN_COUNT = 5


class Student:
    def __init__(self, sid, name, gender, gpa, height, weight):
        #Store CSV values with usable numeric types
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
        #Keep array index as RID
        for row in reader:
            STORAGE.append(Student(*row))


def elapsed_ms(start, end):
    return (end - start) * 1000


def summarize_records(rids):
    male = []
    #Use RID results to read real records
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

    #Measure complete index construction
    start = time.perf_counter()
    for rid, student in enumerate(STORAGE):
        tree.insert(student.sid, rid)
    end = time.perf_counter()
    node_count, utilization = tree.STATUS()

    report["insert_ms"] = elapsed_ms(start, end)
    report["split_count"] = tree.split_count
    report["node_count"] = node_count
    report["utilization"] = utilization

    #Keep lookup keys reproducible
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

    #Measure fixed range workload
    start = time.perf_counter()
    rids = tree.range_query(RANGE_LOW, RANGE_HIGH)
    end = time.perf_counter()
    male_count, avg_gpa, avg_height = summarize_records(rids)
    report["range_ms"] = elapsed_ms(start, end)
    report["range_count"] = len(rids)
    report["male_count"] = male_count
    report["male_avg_gpa"] = avg_gpa
    report["male_avg_height"] = avg_height

    #Delete only from the tree index
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


def print_report(name, d, report):
    print(f"[{name}, d={d}]")
    print(f"insert total: {report['insert_ms']:.6f} ms")
    print(f"search total: {report['search_ms']:.6f} ms, found={report['search_found']}")
    print(f"range total: {report['range_ms']:.6f} ms, key=[{RANGE_LOW}, {RANGE_HIGH}], count={report['range_count']}")
    print(f"delete total: {report['delete_ms']:.6f} ms, deleted={report['delete_count']}")
    print(f"splits: {report['split_count']}")
    print(f"nodes: {report['node_count']}")
    print(f"util: {report['utilization']:.6f}%")
    print(f"record(male): count={report['male_count']}, avg_gpa={report['male_avg_gpa']:.6f}, avg_height={report['male_avg_height']:.6f}")
    print()


def average_reports(reports):
    averaged = {}
    keys = reports[0].keys()
    for key in keys:
        values = [report[key] for report in reports]
        averaged[key] = sum(values) / len(values)
    return averaged


def main():
    #Apply debug setting before experiments
    implement.DEBUG = DEBUG_MODE

    csv_path = Path(__file__).with_name("student.csv")
    load_students(csv_path)
    print(f"Loaded {len(STORAGE)} records")
    print()

    tree_classes = [
        ("B-tree", lambda d: BTree(d=d)),
        ("B*-tree", lambda d: BSTree(d=d)),
        ("B+-tree", lambda d: BPTree(d=d)),
    ]

    print(f"Repeat count per tree: {RUN_COUNT}")
    print()

    #Test each order and tree case
    for d in ORDER_VALUES:
        for name, tree_factory in tree_classes:
            reports = []
            for _ in range(RUN_COUNT):
                report = TEST(tree_factory(d))
                reports.append(report)
            print_report(f"{name} | average of {RUN_COUNT} runs", d, average_reports(reports))


if __name__ == "__main__":
    main()
