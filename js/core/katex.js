// KaTeX (~75 KB gz) is loaded only when a page actually contains math.

let loading;

function loadKatex() {
  loading ??= new Promise((resolve, reject) => {
    const css = document.createElement("link");
    css.rel = "stylesheet";
    css.href = "vendor/katex/katex.min.css";
    document.head.append(css);
    const script = document.createElement("script");
    script.src = "vendor/katex/katex.min.js";
    script.onload = () => resolve(window.katex);
    script.onerror = () => { loading = undefined; reject(new Error("KaTeX failed to load")); };
    document.head.append(script);
  });
  return loading;
}

export async function renderMath(root) {
  const nodes = root?.querySelectorAll(".tex:not([data-done])");
  if (!nodes?.length) return;
  const katex = await loadKatex();
  for (const el of nodes) {
    katex.render(el.dataset.tex, el, { displayMode: el.dataset.display === "1", throwOnError: false });
    el.dataset.done = "1";
  }
}
