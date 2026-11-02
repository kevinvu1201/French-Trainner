// Concept-graph queries. An edge {from, to, type: "requires"} means `from` builds on `to`.

/** All modules `moduleId` depends on through "requires" edges, with their depth. */
export function prerequisites(graph, moduleId) {
  const depth = new Map();
  const queue = [[moduleId, 0]];
  while (queue.length) {
    const [id, d] = queue.shift();
    for (const e of graph.edges) {
      if (e.from === id && e.type === "requires" && e.to !== moduleId && !depth.has(e.to)) {
        depth.set(e.to, d + 1);
        queue.push([e.to, d + 1]);
      }
    }
  }
  return depth;
}

/** Average LOS mastery per module, from the knowledge model (null if the module has no LOS). */
export function moduleMastery(model, manifest) {
  const out = new Map();
  for (const t of manifest.topics) {
    for (const r of t.readings) {
      for (const m of r.modules) {
        const list = m.los.map((l) => model.los.get(l)).filter(Boolean);
        out.set(m.id, list.length ? {
          mean: list.reduce((s, l) => s + l.mean, 0) / list.length,
          practised: list.some((l) => l.n > 0),
        } : null);
      }
    }
  }
  return out;
}

/**
 * The root gap behind a module: its weakest prerequisite (lowest mastery; deeper wins a tie,
 * because a gap further down the chain undermines everything above it).
 */
export function rootGap(graph, model, manifest, moduleId) {
  const pre = prerequisites(graph, moduleId);
  if (!pre.size) return null;
  const mastery = moduleMastery(model, manifest);
  let best = null;
  for (const [id, depth] of pre) {
    const m = mastery.get(id);
    if (!m) continue;
    if (!best || m.mean < best.mean - 1e-9 || (Math.abs(m.mean - best.mean) < 1e-9 && depth > best.depth)) {
      best = { module: id, mean: m.mean, practised: m.practised, depth };
    }
  }
  return best;
}
