import type { CatalogResponse, ProcessResponse } from "../types";

const API_BASE = "http://localhost:8000";

export async function fetchCatalog(): Promise<CatalogResponse> {
  const res = await fetch(`${API_BASE}/catalog`);
  if (!res.ok) throw new Error("加载 catalog 失败");
  return res.json();
}

export type SnippetPayload = {
  snippet: string;
  highlighted_html: string;
  pygments_css: string;
};

export async function fetchSnippet(algorithmId: string): Promise<SnippetPayload> {
  const res = await fetch(`${API_BASE}/code-snippet?algorithm_id=${algorithmId}`);
  if (!res.ok) {
    return {
      snippet: "# snippet unavailable",
      highlighted_html: "<pre># snippet unavailable</pre>",
      pygments_css: ""
    };
  }
  const payload = await res.json();
  return {
    snippet: payload.snippet as string,
    highlighted_html: payload.highlighted_html as string,
    pygments_css: payload.pygments_css as string
  };
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
