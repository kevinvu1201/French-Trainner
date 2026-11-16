// Inline Markdown subset used by the content: **bold**, _italic_, <sup>, <sub>,
// \( inline \) and \[ display \] LaTeX, and [[fig.x]] figure tokens.
// Everything is HTML-escaped first, so source text can never inject markup.
// ($ is not a math delimiter: the curriculum is full of dollar amounts.)

const ESC = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" };
const escape = (s) => s.replace(/[&<>"]/g, (c) => ESC[c]);

export const FIG_TOKEN = /\[\[(fig\.[0-9a-f]{10})\]\]/g;

export function inline(md) {
  // Math is parked in placeholders so the emphasis rules can't touch "x_1" or "**".
  const math = [];
  const park = (display) => (_, tex) =>
    `\u0000${math.push(`<span class="tex"${display ? ' data-display="1"' : ""} data-tex="${tex}"></span>`) - 1}\u0000`;
  let s = escape(md ?? "");
  s = s.replace(/\\\[([\s\S]+?)\\\]/g, park(true));
  s = s.replace(/\\\(([\s\S]+?)\\\)/g, park(false));
  s = s.replace(/&lt;(sup|sub)&gt;([\s\S]*?)&lt;\/\1&gt;/g, "<$1>$2</$1>");
  s = s.replace(/\*\*(?=\S)([\s\S]*?\S)\*\*/g, "<strong>$1</strong>");
  s = s.replace(/(^|[^\w*])_(?=\S)([^_]*?\S)_(?!\w)/g, "$1<em>$2</em>");
  return s.replace(/\u0000(\d+)\u0000/g, (_, i) => math[i]);
}

/** Split text around figure tokens: ["text", {fig: "fig.x"}, "text", ...]. */
export function splitFigures(md) {
  const parts = [];
  let last = 0;
  for (const m of (md ?? "").matchAll(FIG_TOKEN)) {
    if (m.index > last) parts.push(md.slice(last, m.index));
    parts.push({ fig: m[1] });
    last = m.index + m[0].length;
  }
  if (last < (md ?? "").length) parts.push(md.slice(last));
  return parts;
}
