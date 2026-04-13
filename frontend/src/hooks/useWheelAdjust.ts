export function wheelAdjust(
  current: number,
  step: number,
  min: number,
  max: number,
  deltaY: number
) {
  const direction = deltaY > 0 ? -1 : 1;
  const next = current + direction * step;
  return Math.min(max, Math.max(min, Number(next.toFixed(4))));
}
