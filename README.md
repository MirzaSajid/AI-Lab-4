# Lab 4 - Informed Search: Heuristics & A*

**Student:** Sajid Hussain (BSAIM-046) | **Course:** CAI601400 - Artificial Intelligence | **Lab:** 4 (CLO2)

A* search on the campus graph S, A, B, C, G (edges = travel-time units, S = start,
G = destination): manual g/h/f calculations, heuristic audit (admissibility and
consistency), A* vs a zero-heuristic UCS control, and a single-value overestimate
experiment. Heuristic values are **abstract time estimates** from the lab manual, not
measured campus distances.

Conventions: ties in the queue are broken by the supplied code's tuple order (f, then
g, then node label); a node counts as **expanded** only when its successors are
examined; goal processing is logged but **not** counted; stale queue entries are
skipped and reported separately.

## Setup
Python 3.8+ (tested on 3.12). Standard library only. No virtual environment needed.

```bash
python --version
```

## Run
```bash
python lab4_astar_audit.py    # Task 1: supplied A*, audit, manual g/h/f trace
python lab4_compare.py        # Task 2: A* vs UCS control, same graph and counting rules
python lab4_overestimate.py   # Task 3: h(C) 2 -> 10 (and h(B) 4 -> 10)
python lab4_tests.py          # edge cases + 500 random graphs (exit code 0 = all pass)
```
Keep all `lab4_*.py` files in the same folder: the other scripts import
`lab4_astar_audit.py`.

## Files
| File | Purpose |
|---|---|
| `lab4_astar_audit.py` | Supplied `astar()`, traced version, heuristic audit, manual trace |
| `lab4_compare.py` | A* (supplied h) vs UCS (h = 0) with traces and counts |
| `lab4_overestimate.py` | Single-value overestimate experiments |
| `lab4_tests.py` | Start==goal, unreachable, stale entry, 500 random graphs |
| `outputs/*.txt` | Captured outputs of the four scripts |
| `Lab4_Report.docx` | Full report: calculations, audit, comparison, failure analysis, reflection |

## Reproducing the outputs
```bash
python lab4_astar_audit.py  > outputs/audit_output.txt
python lab4_compare.py      > outputs/compare_output.txt
python lab4_overestimate.py > outputs/overestimate_output.txt
python lab4_tests.py        > outputs/tests_output.txt
```

## Sources
`astar()` in `lab4_astar_audit.py` is the supplied reference function from the Lab 4
manual (Section 4.2). All other code is my own. Textbook and paper sources are listed in
the References section of `Lab4_Report.docx`. The random-graph test uses synthetic data
generated from a fixed seed. No credentials, private data or virtual environments are
included.
