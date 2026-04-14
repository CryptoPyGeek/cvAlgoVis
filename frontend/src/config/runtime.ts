function normalizeBase(base?: string): string | undefined {
  if (!base) return undefined;
  return base.replace(/\/+$/, "");
}

export function getApiBase(): string {
  const injected = normalizeBase(window.__APP_CONFIG__?.apiBase);
  if (injected) return injected;

  const envBase = normalizeBase(import.meta.env.VITE_API_BASE);
  if (envBase) return envBase;

  return "http://localhost:8000";
}
