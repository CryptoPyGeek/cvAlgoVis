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
  highlight_available: boolean;
  message: string;
};

export async function fetchSnippet(algorithmId: string): Promise<SnippetPayload> {
  try {
    const res = await fetch(`${API_BASE}/code-snippet?algorithm_id=${algorithmId}`);
    if (!res.ok) {
      const reason =
        res.status === 404
          ? `算法 ${algorithmId} 无代码片段（404）`
          : `后端 /code-snippet 返回 ${res.status}`;
      return {
        snippet: "# snippet unavailable",
        highlighted_html: "",
        pygments_css: "",
        highlight_available: false,
        message: `高亮已降级：${reason}`
      };
    }
    const payload = await res.json();
    return {
      snippet: payload.snippet as string,
      highlighted_html: payload.highlighted_html as string,
      pygments_css: payload.pygments_css as string,
      highlight_available: Boolean(payload.pygments_css),
      message: "高亮已启用（Pygments）"
    };
  } catch {
    return {
      snippet: "# snippet unavailable",
      highlighted_html: "",
      pygments_css: "",
      highlight_available: false,
      message: "高亮已降级：后端未连接，无法访问 /code-snippet"
    };
  }
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
