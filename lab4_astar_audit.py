"""Lab 4 - Task 1: A* evaluation, heuristic audit and manual f-value trace.

Campus graph (edges are travel-time units): S = start building, G = destination.
The heuristic values are ABSTRACT TIME ESTIMATES supplied by the lab manual, in
the same units as the edge costs; they are not measured campus distances.

astar() is the supplied reference function (manual Section 4.2), unchanged
apart from layout. astar_trace() uses exactly the same logic but also records,
for every queue entry that is popped, the g/h/f values, the entries generated
and the frontier afterwards.

Tie-breaking (inherited from the supplied code): queue entries are tuples
(f, g, node, path), so ties on f are broken by smaller g, then by node label.
Counting convention: a node is "expanded" only when its successors are
examined. Goal processing is logged but NOT counted as an expansion. Stale
queue entries (g != best[node]) are skipped and counted separately.
Run: python lab4_astar_audit.py
"""
import heapq

INF = float("inf")

GRAPH = {"S": [("A", 1), ("B", 4)], "A": [("C", 2)], "B": [("G", 5)],
         "C": [("G", 3)], "G": []}
H = {"S": 5, "A": 4, "B": 4, "C": 2, "G": 0}


# ---- supplied reference code (manual Section 4.2) -------------------------
def astar(graph, h, start, goal):
    pq = [(h[start], 0, start, [start])]
    best = {start: 0}
    while pq:
        f, g, node, path = heapq.heappop(pq)
        if node == goal:
            return g, path
        if g != best[node]:
            continue
        for nxt, w in graph.get(node, []):
            ng = g + w
            if ng < best.get(nxt, float("inf")):
                best[nxt] = ng
                heapq.heappush(pq, (ng + h[nxt], ng, nxt, path + [nxt]))


# ---- helpers ---------------------------------------------------------------
def fmt_frontier(pq):
    """Frontier as text, in pop order: node(f=..,g=..)."""
    items = sorted(pq)
    return "[" + ", ".join(f"{n}(f={f},g={g})" for f, g, n, _ in items) + "]"


def astar_trace(graph, h, start, goal):
    """Same logic as astar(); returns a result dict with a full event trace."""
    pq = [(h[start], 0, start, [start])]
    best = {start: 0}
    events = []
    expansions = stale = 0
    while pq:
        f, g, node, path = heapq.heappop(pq)
        if node == goal:
            events.append(dict(kind="goal", node=node, g=g, h=h[node], f=f,
                               path=path, generated=[],
                               frontier=fmt_frontier(pq), queue=sorted(pq)))
            return dict(found=True, cost=g, path=path, events=events,
                        expansions=expansions, stale=stale)
        if g != best[node]:
            stale += 1
            events.append(dict(kind="stale", node=node, g=g, h=h[node], f=f,
                               path=path, generated=[],
                               frontier=fmt_frontier(pq), queue=sorted(pq)))
            continue
        expansions += 1
        generated = []
        for nxt, w in graph.get(node, []):
            ng = g + w
            pushed = ng < best.get(nxt, INF)
            if pushed:
                best[nxt] = ng
                heapq.heappush(pq, (ng + h[nxt], ng, nxt, path + [nxt]))
            generated.append((nxt, w, ng, h[nxt], ng + h[nxt], pushed))
        events.append(dict(kind="expand", node=node, g=g, h=h[node], f=f,
                           path=path, generated=generated,
                           frontier=fmt_frontier(pq), queue=sorted(pq)))
    return dict(found=False, cost=None, path=None, events=events,
                expansions=expansions, stale=stale)


def true_remaining_costs(graph, goal):
    """Exact remaining cost h*(n) for every node: Dijkstra on the reversed graph."""
    rev = {}
    for u, edges in graph.items():
        for v, w in edges:
            rev.setdefault(v, []).append((u, w))
    dist = {goal: 0}
    pq = [(0, goal)]
    while pq:
        d, n = heapq.heappop(pq)
        if d > dist[n]:
            continue
        for u, w in rev.get(n, []):
            nd = d + w
            if nd < dist.get(u, INF):
                dist[u] = nd
                heapq.heappush(pq, (nd, u))
    return dist


def path_cost(path, graph):
    """Independent check: sum the edge weights along a path."""
    weight = {(u, v): w for u, edges in graph.items() for v, w in edges}
    return sum(weight[(a, b)] for a, b in zip(path, path[1:]))


def arrow(path):
    return " -> ".join(path) if path else "-"


def audit_rows(graph, h, goal):
    """Admissibility per node and consistency per edge (lists of tuples)."""
    star = true_remaining_costs(graph, goal)
    adm = [(n, h[n], star.get(n, INF), h[n] <= star.get(n, INF)) for n in graph]
    cons = []
    for u, edges in graph.items():
        for v, w in edges:
            cons.append((u, v, w, h[u], w + h[v], h[u] <= w + h[v]))
    return adm, cons


def print_audit(graph, h, goal):
    adm, cons = audit_rows(graph, h, goal)
    print("Admissibility: h(n) <= true remaining cost h*(n)")
    print("node | h(n) | true remaining cost | admissible?")
    for n, hv, star, ok in adm:
        print(n, hv, star, ok, sep=" | ")
    print("All admissible:", all(r[3] for r in adm))
    print()
    print("Consistency: h(u) <= cost(u,v) + h(v) for every directed edge")
    print("edge | cost | h(u) | cost + h(v) | consistent?")
    for u, v, w, hu, rhs, ok in cons:
        print(f"{u} -> {v}", w, hu, f"{w} + {rhs - w} = {rhs}", ok, sep=" | ")
    print("All consistent:", all(r[5] for r in cons))


def print_manual_trace(result, count):
    print(f"First {count} expansions, with every calculation")
    shown = 0
    events = result["events"]
    for i, ev in enumerate(events):
        if ev["kind"] != "expand":
            continue
        shown += 1
        print(f"Expansion {shown}: select {ev['node']}")
        print(f"  g = {ev['g']}, h = {ev['h']}, f = g + h = {ev['g']} + {ev['h']} = {ev['f']}")
        for nxt, w, ng, hn, fn, pushed in ev["generated"]:
            if pushed:
                print(f"  generate {nxt}: g = {ev['g']} + {w} = {ng}, h = {hn}, "
                      f"f = {ng} + {hn} = {fn}")
            else:
                print(f"  generate {nxt}: g = {ev['g']} + {w} = {ng} is not better "
                      f"than the best known cost, so it is not queued")
        print(f"  frontier after: {ev['frontier']}")
        q = ev["queue"]
        nf, ng_, nn, _ = q[0]
        others = ", ".join(f"{n}'s f = {f}" for f, g, n, _ in q[1:])
        why = f"lowest f = {nf}" + (f" (others: {others})" if others else "")
        suffix = " (it is the goal, so A* stops)" if nn == "G" else ""
        print(f"  next selected: {nn} because it has the {why}{suffix}")
        if shown == count:
            break
    print()


def main():
    print("Supplied code (manual Section 4.2)")
    print("astar(g, h, 'S', 'G') ->", astar(GRAPH, H, "S", "G"))
    print()
    print_audit(GRAPH, H, "G")
    print()
    result = astar_trace(GRAPH, H, "S", "G")
    print_manual_trace(result, 3)
    goal_ev = [e for e in result["events"] if e["kind"] == "goal"][0]
    print(f"Goal processing: select {goal_ev['node']} with g = {goal_ev['g']}, "
          f"h = {goal_ev['h']}, f = {goal_ev['g']} + {goal_ev['h']} = {goal_ev['f']}; "
          f"frontier {goal_ev['frontier']}")
    print("Final path:", arrow(result["path"]), "| cost reported by A*:", result["cost"])
    print("Independent edge-weight sum:",
          " + ".join(str(w) for w in [1, 2, 3]), "=", path_cost(result["path"], GRAPH))
    print("Matches supplied astar():",
          (result["cost"], result["path"]) == astar(GRAPH, H, "S", "G"))


if __name__ == "__main__":
    main()
