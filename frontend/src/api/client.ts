import type { CatalogResponse, ProcessResponse } from "../types";

const API_BASE = "http://localhost:8000";

export async function fetchCatalog(): Promise<CatalogResponse> {
  const res = await fetch(`${API_BASE}/catalog`);
  if (!res.ok) throw new Error("加载 catalog 失败");
  return res.json();
}

export async function fetchSnippet(algorithmId: string): Promise<string> {
  const res = await fetch(`${API_BASE}/code-snippet?algorithm_id=${algorithmId}`);
  if (!res.ok) return "# snippet unavailable";
  const payload = await res.json();
  return payload.snippet as string;
}

export async function processImage(payload: {
  library_id: string;
  algorithm_id: string;
  params: Record<string, number>;
  image: string;
}): Promise<ProcessResponse> {
  const res = await fetch(`${API_BASE}/process`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || "处理失败");
  }
  return res.json();
}
