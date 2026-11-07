"""Lab 4 - edge cases and evidence over many random graphs.

Part 1  start == goal, unreachable goal, stale-entry demonstration, and the
        zero-heuristic control.
Part 2  evidence beyond one example: on 500 random weighted graphs (fixed
        seed), A* with admissible heuristics always returns the optimal cost,
        while overestimating heuristics sometimes do not. A single unchanged
        run therefore proves nothing about a heuristic.
All graphs here are synthetic. Exit code 0 if every check passes, else 1.
Run: python lab4_tests.py   (needs lab4_astar_audit.py in the same folder)
"""
import random
import sys

from lab4_astar_audit import (GRAPH, H, INF, arrow, astar_trace, path_cost,
                              true_remaining_costs)

results = []


def check(name, condition):
    results.append(bool(condition))
    print(f"{'PASS' if condition else 'FAIL'} | {name}")


def random_graph(rng, n_nodes):
    nodes = [f"n{i}" for i in range(n_nodes)]
    graph = {n: [] for n in nodes}
    for u in nodes:
        for v in nodes:
            if u != v and rng.random() < 0.35:
                graph[u].append((v, rng.randint(1, 9)))
    return nodes, graph


def main():
    # ---------------------------------------------------------------- Part 1
    print("== Part 1: edge cases ==")
    r = astar_trace(GRAPH, H, "S", "S")
    check("start == goal: path [S], cost 0, no expansions",
          r["path"] == ["S"] and r["cost"] == 0 and r["expansions"] == 0)

    g2 = dict(GRAPH, Z=[])
    h2 = dict(H, Z=0)
    r = astar_trace(g2, h2, "S", "Z")
    print("info | unreachable goal Z: expansions =", r["expansions"],
          "| stale =", r["stale"])
    check("unreachable goal: A* reports no path after exhausting the frontier",
          not r["found"] and r["path"] is None)

    stale_graph = {"S": [("X", 5), ("Y", 1)], "Y": [("X", 1)],
                   "X": [("G", 10)], "G": []}
    zero = {n: 0 for n in stale_graph}
    r = astar_trace(stale_graph, zero, "S", "G")
    print("info | stale demo trace:", [(e["kind"], e["node"], e["g"]) for e in r["events"]])
    check("stale entry: X is first queued at g=5, then improved to g=2",
          r["stale"] == 1 and r["cost"] == 12 and r["path"] == ["S", "Y", "X", "G"])
    check("stale entry is skipped, not counted as an expansion (3 expansions)",
          r["expansions"] == 3)

    zero_main = {n: 0 for n in H}
    u = astar_trace(GRAPH, zero_main, "S", "G")
    a = astar_trace(GRAPH, H, "S", "G")
    check("h = 0 (UCS control) returns the same optimal cost as A*", u["cost"] == a["cost"] == 6)
    check("A* expands fewer nodes than the UCS control here (3 < 4)",
          a["expansions"] < u["expansions"])

    # ---------------------------------------------------------------- Part 2
    print()
    print("== Part 2: 500 random graphs (seed 4, 6-8 nodes, weights 1-9) ==")
    rng = random.Random(4)
    solvable = 0
    admissible_bad = 0          # admissible heuristics that returned a wrong cost
    over_checked = over_suboptimal = 0
    expansions_zero = expansions_exact = 0
    for _ in range(500):
        nodes, graph = random_graph(rng, rng.randint(6, 8))
        start, goal = nodes[0], nodes[-1]
        star = true_remaining_costs(graph, goal)
        if start not in star:
            continue                                 # goal unreachable: skip
        solvable += 1
        optimum = star[start]
        reach = [n for n in nodes if n in star]
        # heuristics must be defined for every node; use 0 for dead-end nodes
        h_zero = {n: 0 for n in nodes}
        h_half = {n: star.get(n, 0) // 2 for n in nodes}      # admissible
        h_exact = {n: star.get(n, 0) for n in nodes}          # perfect
        h_over = {n: (star[n] + rng.randint(1, 8) if n in star and n != goal else 0)
                  for n in nodes}                             # overestimates
        for hh in (h_zero, h_half, h_exact):
            res = astar_trace(graph, hh, start, goal)
            if res["cost"] != optimum or path_cost(res["path"], graph) != optimum:
                admissible_bad += 1
        expansions_zero += astar_trace(graph, h_zero, start, goal)["expansions"]
        expansions_exact += astar_trace(graph, h_exact, start, goal)["expansions"]
        res = astar_trace(graph, h_over, start, goal)
        over_checked += 1
        if res["cost"] != optimum:
            over_suboptimal += 1

    print(f"graphs with a route from start to goal : {solvable}")
    print(f"admissible runs (h=0, h=h*//2, h=h*) with a wrong cost : {admissible_bad}")
    print(f"overestimating runs checked            : {over_checked}")
    print(f"overestimating runs with a suboptimal cost : {over_suboptimal}")
    print(f"total expansions, h = 0     : {expansions_zero}")
    print(f"total expansions, h = h*    : {expansions_exact}")
    check("admissible heuristics were optimal on every solvable graph", admissible_bad == 0)
    check("overestimating heuristics returned a suboptimal cost on some graphs",
          over_suboptimal > 0)
    check("overestimating heuristics were still optimal on some graphs "
          "(an unchanged run proves nothing)", over_suboptimal < over_checked)
    check("a perfect heuristic expands no more nodes than h = 0 in total",
          expansions_exact <= expansions_zero)

    passed = sum(results)
    print()
    print(f"{passed}/{len(results)} checks passed")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
