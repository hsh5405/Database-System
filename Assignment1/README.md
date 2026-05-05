# Assignment1

This repository contains the Python implementation and experiments for CSE321 Project 1, covering B-tree, B*-tree, B+-tree, and an additional layered_B+-tree experiment.

## Author

- Student ID: 20211356
- Name: Han SeungHo

## Environment

- Language: Python
- Tested version: Python 3.12.10
- External dependencies: none
- Required files: `main.py`, `implement.py`, `addition.py`, `student.csv`

## Repository Files

- `main.py`: runs the required experiments for B-tree, B*-tree, and B+-tree.
- `implement.py`: implements `BTree`, `BSTree`, and `BPTree`.
- `addition.py`: runs the additional layered B+-tree experiment.
- `student.csv`: input dataset with 100,000 student records.

## How To Run `main.py`

Open a terminal in this repository directory and run:

```powershell
python main.py
```

This command runs the required experiments for:

- `B-tree`
- `B*-tree`
- `B+-tree`

The program repeats each case and prints the average result for each tree/order combination.

## Example Output `main.py`

```text
Loaded 100000 records

Repeat count per tree: 5

[B-tree | average of 5 runs, d=3]
insert total: 1801.458380 ms
search total: 96.802520 ms, found=10000.0
range total: 18.417940 ms, key=[202000000, 202099999], count=14316.0
delete total: 43.110180 ms, deleted=2000.0
splits: 74357.0
nodes: 74371.0
util: 67.230507%
record(male): count=7214.0, avg_gpa=3.278453, avg_height=174.058082

[B*-tree | average of 5 runs, d=3]
insert total: 2141.103480 ms
search total: 84.844260 ms, found=10000.0
range total: 17.122540 ms, key=[202000000, 202099999], count=14316.0
delete total: 32.725580 ms, deleted=2000.0
splits: 62400.0
nodes: 62412.0
util: 80.112799%
record(male): count=7214.0, avg_gpa=3.278453, avg_height=174.058082

[B+-tree | average of 5 runs, d=3]
insert total: 2712.102580 ms
search total: 98.593180 ms, found=10000.0
range total: 15.521020 ms, key=[202000000, 202099999], count=14316.0
delete total: 32.225180 ms, deleted=2000.0
splits: 116452.0
nodes: 116466.0
util: 71.525595%
record(male): count=7214.0, avg_gpa=3.278453, avg_height=174.058082

[B-tree | average of 5 runs, d=5]
insert total: 1040.563940 ms
search total: 77.526420 ms, found=10000.0
range total: 13.155500 ms, key=[202000000, 202099999], count=14316.0
delete total: 33.808340 ms, deleted=2000.0
splits: 36767.0
nodes: 36776.0
util: 67.979117%
record(male): count=7214.0, avg_gpa=3.278453, avg_height=174.058082

[B*-tree | average of 5 runs, d=5]
insert total: 1337.915760 ms
search total: 71.762620 ms, found=10000.0
range total: 11.077060 ms, key=[202000000, 202099999], count=14316.0
delete total: 25.477140 ms, deleted=2000.0
splits: 30184.0
nodes: 30192.0
util: 82.803392%
record(male): count=7214.0, avg_gpa=3.278453, avg_height=174.058082

[B+-tree | average of 5 runs, d=5]
insert total: 1209.315180 ms
search total: 67.430700 ms, found=10000.0
range total: 9.478740 ms, key=[202000000, 202099999], count=14316.0
delete total: 21.693080 ms, deleted=2000.0
splits: 46799.0
nodes: 46808.0
util: 71.718510%
record(male): count=7214.0, avg_gpa=3.278453, avg_height=174.058082

[B-tree | average of 5 runs, d=10]
insert total: 731.836920 ms
search total: 67.044020 ms, found=10000.0
range total: 9.360580 ms, key=[202000000, 202099999], count=14316.0
delete total: 23.268280 ms, deleted=2000.0
splits: 16381.0
nodes: 16387.0
util: 67.804425%
record(male): count=7214.0, avg_gpa=3.278453, avg_height=174.058082

[B*-tree | average of 5 runs, d=10]
insert total: 1036.465040 ms
search total: 66.504200 ms, found=10000.0
range total: 9.558420 ms, key=[202000000, 202099999], count=14316.0
delete total: 24.451840 ms, deleted=2000.0
splits: 13049.0
nodes: 13055.0
util: 85.110005%
record(male): count=7214.0, avg_gpa=3.278453, avg_height=174.058082

[B+-tree | average of 5 runs, d=10]
insert total: 747.067540 ms
search total: 56.576060 ms, found=10000.0
range total: 6.725720 ms, key=[202000000, 202099999], count=14316.0
delete total: 20.538360 ms, deleted=2000.0
splits: 17939.0
nodes: 17945.0
util: 71.487570%
record(male): count=7214.0, avg_gpa=3.278453, avg_height=174.058082
```

## How To Run `addition.py`

Open a terminal in this repository directory and run:

```powershell
python addition.py
```

This command compares:

- plain `B+-tree` with `d=10`, `d=20`, and `d=30`
- `Layered_B+-tree` with different internal-node order (`di`) and leaf-node order (`dl`)

The program repeats each case and prints the average result for each case.

## Example Output `addition.py`

```text
Loaded 100000 records

Repeat count per tree: 10

[B+-tree, d=10 | average of 10 runs]
insert total: 536.790240 ms
search total: 37.913940 ms, found=10000.0
range total: 4.974550 ms, key=[202000000, 202099999], count=14316.0
delete total: 16.063820 ms, deleted=2000.0
splits: 17939.0
nodes: 17945.0
util: 71.487570%
record(male): count=7214.0, avg_gpa=3.278453, avg_height=174.058082

[B+-tree, d=20 | average of 10 runs]
insert total: 479.256880 ms
search total: 39.286220 ms, found=10000.0
range total: 4.149290 ms, key=[202000000, 202099999], count=14316.0
delete total: 15.211920 ms, deleted=2000.0
splits: 8072.0
nodes: 8077.0
util: 70.059233%
record(male): count=7214.0, avg_gpa=3.278453, avg_height=174.058082

[B+-tree, d=30 | average of 10 runs]
insert total: 516.288090 ms
search total: 42.774400 ms, found=10000.0
range total: 4.126030 ms, key=[202000000, 202099999], count=14316.0
delete total: 16.793480 ms, deleted=2000.0
splits: 5167.0
nodes: 5171.0
util: 69.964457%
record(male): count=7214.0, avg_gpa=3.278453, avg_height=174.058082

[Layered_B+-tree, di=10, dl=30 | average of 10 runs]
insert total: 503.539510 ms
search total: 36.984540 ms, found=10000.0
range total: 4.112550 ms, key=[202000000, 202099999], count=14316.0
delete total: 14.939170 ms, deleted=2000.0
splits: 5725.0
nodes: 5731.0
util: 69.964457%
record(male): count=7214.0, avg_gpa=3.278453, avg_height=174.058082

[Layered_B+-tree, di=30, dl=10 | average of 10 runs]
insert total: 624.172670 ms
search total: 48.412550 ms, found=10000.0
range total: 5.239380 ms, key=[202000000, 202099999], count=14316.0
delete total: 20.694070 ms, deleted=2000.0
splits: 16218.0
nodes: 16223.0
util: 71.566446%
record(male): count=7214.0, avg_gpa=3.278453, avg_height=174.058082
```

## Experiment Settings

The experiments use the following workload:

- Insert all 100,000 student records into an empty tree
- Perform 10,000 random point searches
- Execute one range query on student IDs in `[202000000, 202099999]`
- Delete 2,000 selected keys from the tree
- Report execution time, split count, node count, utilization, and range-query summary statistics

## Notes

- No additional package installation is required.
- The code uses the array index of each loaded student record as the RID.
- If Python is installed correctly and the files are placed in the same directory, the experiments should run as expected with the two commands above.
