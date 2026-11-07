"""Lab 4 - Task 2: A* (supplied heuristic) vs UCS (zero-heuristic control).

Same graph, start, goal and tie-breaking in both runs; the ONLY difference is
the heuristic (UCS control: h(n) = 0 for every node, so f = g).
Counting convention: a node is expanded only when its successors are examined;
goal processing is logged but excluded; stale queue entries are skipped and
counted separately.
Run: python lab4_compare.py
"""
from lab4_astar_audit import GRAPH, H, arrow, astar_trace, path_cost


def print_trace(title, result):
    print(title)
    print("step | event | node | g | h | f | frontier after")
    for step, ev in enumerate(result["events"], 1):
        print(step, ev["kind"], ev["node"], ev["g"], ev["h"], ev["f"],
              ev["frontier"], sep=" | ")
    print()


def processed_order(result):
    return ", ".join(e["node"] for e in result["events"])


def expanded_order(result):
    return ", ".join(e["node"] for e in result["events"] if e["kind"] == "expand")


def main():
    zero = {n: 0 for n in H}
    astar_res = astar_trace(GRAPH, H, "S", "G")
    ucs_res = astar_trace(GRAPH, zero, "S", "G")

    print_trace("A* trace (supplied heuristic)", astar_res)
    print_trace("UCS control trace (h = 0 for every node)", ucs_res)

    print("Results")
    print("algorithm | path | reported cost | independent cost | processed-node trace | "
          "expanded nodes | expansions | stale pops")
    for name, r in (("A*", astar_res), ("UCS", ucs_res)):
        print(name, arrow(r["path"]), r["cost"], path_cost(r["path"], GRAPH),
              processed_order(r), expanded_order(r), r["expansions"], r["stale"],
              sep=" | ")
    print()
    print("Independent sums: 1 + 2 + 3 =", path_cost(["S", "A", "C", "G"], GRAPH),
          "(S -> A -> C -> G); 4 + 5 =", path_cost(["S", "B", "G"], GRAPH),
          "(S -> B -> G)")
    print("Same path and same cost in both runs:",
          astar_res["path"] == ucs_res["path"] and astar_res["cost"] == ucs_res["cost"])
    print(f"Expansions saved by the heuristic: "
          f"{ucs_res['expansions'] - astar_res['expansions']}")
    only_ucs = [e["node"] for e in ucs_res["events"] if e["kind"] == "expand"
                and e["node"] not in [x["node"] for x in astar_res["events"]
                                      if x["kind"] == "expand"]]
    print("Nodes expanded by UCS but not by A*:", ", ".join(only_ucs))
    print("Stale entries encountered: A* =", astar_res["stale"],
          "| UCS =", ucs_res["stale"])


if __name__ == "__main__":
    main()
