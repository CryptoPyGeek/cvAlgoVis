import { useEffect, type DependencyList } from "react";

export function useDebouncedEffect(
  effect: () => void,
  deps: DependencyList,
  delay: number
) {
  useEffect(() => {
    const t = window.setTimeout(effect, delay);
    return () => window.clearTimeout(t);
  }, deps);
}
