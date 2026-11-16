// Hash routes (#/study/quant, #/m/m01.2/los.01.d) work on any static host, including
// a GitHub Pages sub-path, with no server rewrites.

import { useEffect, useState } from "../lib.js";

export function parse(hash) {
  const parts = hash.replace(/^#\/?/, "").split("/").filter(Boolean).map(decodeURIComponent);
  return { name: parts[0] ?? "home", args: parts.slice(1) };
}

export function useRoute() {
  const [route, setRoute] = useState(() => parse(location.hash));
  useEffect(() => {
    const onChange = () => setRoute(parse(location.hash));
    addEventListener("hashchange", onChange);
    return () => removeEventListener("hashchange", onChange);
  }, []);
  return route;
}

export const href = (...parts) => "#/" + parts.map(encodeURIComponent).join("/");
