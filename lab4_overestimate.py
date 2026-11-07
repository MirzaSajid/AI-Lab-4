"""Lab 4 - Task 3: overestimating the heuristic.

ONE heuristic value is changed per experiment; graph, start, goal and
tie-breaking are unchanged. h(C) = 10 is the required reproducible example
(true remaining cost of C is 3). A second experiment, h(B) = 10 (true remaining
cost 5), is also an overestimate but leaves this particular run unchanged: it
shows why one unchanged run does not prove a heuristic safe.
Run: python lab4_overestimate.py
"""
from lab4_astar_audit import (GRAPH, H, arrow, astar_trace, audit_rows,
                              path_cost, true_remaining_costs)
from lab4_compare import print_trace


def main():
    star = true_remaining_costs(GRAPH, "G")
    base = astar_trace(GRAPH, H, "S", "G")
    experiments = [("baseline (supplied h)", None, H, base)]
    for node, new in (("C", 10), ("B", 10)):
        modified = dict(H)
        modified[node] = new
        experiments.append((f"h({node}): {H[node]} -> {new}", node, modified,
                            astar_trace(GRAPH, modified, "S", "G")))

    for label, node, hh, res in experiments[1:]:
        print_trace(f"A* trace with {label}", res)
        adm, cons = audit_rows(GRAPH, hh, "G")
        bad_adm = [n for n, hv, s, ok in adm if not ok]
        bad_cons = [f"{u} -> {v}" for u, v, w, hu, rhs, ok in cons if not ok]
        print(f"Audit: inadmissible nodes = {bad_adm}; inconsistent edges = {bad_cons}")
        print()

    print("Summary of the single-value overestimate experiments")
    print("experiment | original h | modified h | true remaining cost | admissible? | "
          "path | cost | independent cost | expansions | result changed?")
    for label, node, hh, res in experiments:
        if node is None:
            print(label, "-", "-", "-", True, arrow(res["path"]), res["cost"],
                  path_cost(res["path"], GRAPH), res["expansions"], "-", sep=" | ")
            continue
        changed = (res["path"], res["cost"]) != (base["path"], base["cost"])
        print(label, H[node], hh[node], star[node], hh[node] <= star[node],
              arrow(res["path"]), res["cost"], path_cost(res["path"], GRAPH),
              res["expansions"], changed, sep=" | ")
    print()
    print("Optimal cost on this graph:", star["S"])


if __name__ == "__main__":
    main()
