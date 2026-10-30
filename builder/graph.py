"""Concept graph: modules as nodes, typed edges from the generated layer, layout precomputed.

Edges come from each module's `connections` (requires / applies / contrasts_with / extends).
Only modules that take part in at least one edge are drawn, so the map grows as topics are
generated. Positions are computed here (networkx Kamada–Kawai layout, topics started on a
circle so related modules cluster) and normalised to 0..1; the phone just draws them.
"""

from __future__ import annotations

import math
from typing import Any

import networkx as nx

EDGE_TYPES = ("requires", "applies", "contrasts_with", "extends")


def build_graph(chunks: dict[str, dict[str, Any]], topic_order: list[str]) -> dict[str, Any] | None:
    titles: dict[str, tuple[str, str]] = {}
    for topic, ch in chunks.items():
        for m in ch["modules"]:
            titles[m["id"]] = (m["title"], topic)
    edges = []
    for ch in chunks.values():
        for src, learning in ch["learning"].items():
            for c in learning.get("connections", []):
                if c["to"] in titles and c["to"] != src:
                    edges.append({"from": src, "to": c["to"], "type": c["type"], "note": c["note"]})
    if not edges:
        return None

    g = nx.Graph()
    for e in edges:
        g.add_edge(e["from"], e["to"])
    # Start each topic's nodes around its own point on a circle; springs do the rest.
    anchors = {t: (math.cos(2 * math.pi * i / len(topic_order)), math.sin(2 * math.pi * i / len(topic_order)))
               for i, t in enumerate(topic_order)}
    initial = {}
    for i, node in enumerate(sorted(g.nodes)):
        ax, ay = anchors[titles[node][1]]
        initial[node] = (ax + 0.05 * math.cos(i), ay + 0.05 * math.sin(i))
    # Kamada–Kawai spreads small graphs far better than springs (no central clump); the
    # topic-anchored start keeps related modules near each other.
    pos = nx.kamada_kawai_layout(g, pos=initial)
    xs = [p[0] for p in pos.values()]
    ys = [p[1] for p in pos.values()]
    span = max(max(xs) - min(xs), max(ys) - min(ys)) or 1.0
    nodes = [{"id": n, "title": titles[n][0], "topic": titles[n][1],
              "x": round((pos[n][0] - min(xs)) / span, 4), "y": round((pos[n][1] - min(ys)) / span, 4)}
             for n in sorted(g.nodes)]
    return {"nodes": nodes, "edges": edges}
