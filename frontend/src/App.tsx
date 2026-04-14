import { useEffect, useMemo, useState } from "react";

import { fetchCatalog, fetchSnippet, processImage } from "./api/client";
import { AlgorithmSelector } from "./components/AlgorithmSelector";
import { CodePanel } from "./components/CodePanel";
import { ImagePreviewPanel } from "./components/ImagePreviewPanel";
import { LibrarySelector } from "./components/LibrarySelector";
import { ParamControlPanel } from "./components/ParamControlPanel";
import { useDebouncedEffect } from "./hooks/useDebouncedEffect";
import type { CatalogResponse } from "./types";

const SAMPLE_IMAGE = `${import.meta.env.BASE_URL}samples/contact.png`;

export default function App() {
  const [catalog, setCatalog] = useState<CatalogResponse | null>(null);
  const [libraryId, setLibraryId] = useState("opencv");
  const [moduleId, setModuleId] = useState("");
  const [algorithmId, setAlgorithmId] = useState("");
  const [paramValues, setParamValues] = useState<Record<string, number>>({});
  const [sampleDataUrl, setSampleDataUrl] = useState<string>("");
  const [sourceImage, setSourceImage] = useState<string>("");
  const [sourceImageApi, setSourceImageApi] = useState<string>("");
  const [resultImage, setResultImage] = useState<string>("");
  const [snippet, setSnippet] = useState<string>("# loading...");
  const [highlightedSnippet, setHighlightedSnippet] = useState<string>("<pre># loading...</pre>");
  const [pygmentsCss, setPygmentsCss] = useState<string>("");
  const [highlightAvailable, setHighlightAvailable] = useState(false);
  const [highlightMessage, setHighlightMessage] = useState("高亮状态初始化中");
  const [statusText, setStatusText] = useState("状态：Ready");
  const [elapsedMs, setElapsedMs] = useState(0);

  const activeLibrary = useMemo(() => {
    return catalog?.libraries.find((library) => library.id === libraryId);
  }, [catalog, libraryId]);

  const activeModule = useMemo(() => {
    return activeLibrary?.modules.find((module) => module.id === moduleId) ?? activeLibrary?.modules[0];
  }, [activeLibrary, moduleId]);

  const activeAlgorithm = useMemo(() => {
    return activeModule?.algorithms.find((algorithm) => algorithm.id === algorithmId) ?? activeModule?.algorithms[0];
  }, [activeModule, algorithmId]);

  function toDataUrl(blob: Blob): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(String(reader.result));
      reader.onerror = () => reject(new Error("文件读取失败"));
      reader.readAsDataURL(blob);
    });
  }

  function rasterizeToPngDataUrl(src: string): Promise<string> {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => {
        const width = img.naturalWidth || 800;
        const height = img.naturalHeight || 600;
        const canvas = document.createElement("canvas");
        canvas.width = width;
        canvas.height = height;
        const ctx = canvas.getContext("2d");
        if (!ctx) {
          reject(new Error("Canvas 初始化失败"));
          return;
        }
        ctx.drawImage(img, 0, 0, width, height);
        resolve(canvas.toDataURL("image/png"));
      };
      img.onerror = () => reject(new Error("图像栅格化失败"));
      img.src = src;
    });
  }

  async function normalizeImageForApi(src: string): Promise<string> {
    if (src.startsWith("data:image/svg+xml")) {
      return rasterizeToPngDataUrl(src);
    }
    if (src.startsWith("data:image/")) {
      return src;
    }
    return rasterizeToPngDataUrl(src);
  }

  useEffect(() => {
    fetchCatalog()
      .then((payload) => {
        setCatalog(payload);
        const opencv = payload.libraries.find((library) => library.id === "opencv") ?? payload.libraries[0];
        if (!opencv) return;
        setLibraryId(opencv.id);
        setModuleId(opencv.modules[0]?.id ?? "");
        setAlgorithmId(opencv.modules[0]?.algorithms[0]?.id ?? "");
      })
      .catch(() => setStatusText("状态：Catalog 加载失败"));
  }, []);

  useEffect(() => {
    fetch(SAMPLE_IMAGE)
      .then((res) => res.blob())
      .then(toDataUrl)
      .then((base64) => {
        setSampleDataUrl(base64);
        setSourceImage(base64);
        setResultImage(base64);
        return normalizeImageForApi(base64);
      })
      .then((apiImage) => {
        setSourceImageApi(apiImage);
      })
      .catch(() => setStatusText("状态：样例图加载失败"));
  }, []);

  useEffect(() => {
    if (!activeAlgorithm) return;
    const defaults = Object.fromEntries(activeAlgorithm.params.map((p) => [p.name, p.default]));
    setParamValues(defaults);
    fetchSnippet(activeAlgorithm.id)
      .then((payload) => {
        setSnippet(payload.snippet);
        setHighlightedSnippet(payload.highlighted_html);
        setPygmentsCss(payload.pygments_css);
        setHighlightAvailable(payload.highlight_available);
        setHighlightMessage(payload.message);
      })
      .catch(() => {
        setSnippet("# snippet unavailable");
        setHighlightedSnippet("");
        setPygmentsCss("");
        setHighlightAvailable(false);
        setHighlightMessage("高亮已降级：snippet 请求异常");
      });
  }, [activeAlgorithm?.id]);

  useDebouncedEffect(
    () => {
      if (!activeAlgorithm) return;
      if (!sourceImageApi.startsWith("data:image/")) {
        setStatusText("状态：请先上传或加载样例图");
        return;
      }
      setStatusText("状态：Processing...");
      processImage({
        library_id: libraryId,
        algorithm_id: activeAlgorithm.id,
        params: paramValues,
        image: sourceImageApi
      })
        .then((res) => {
          setResultImage(res.processed_image);
          setElapsedMs(res.meta.elapsed_ms);
          setStatusText("状态：Ready");
        })
        .catch((err: Error) => {
          setStatusText(`状态：处理失败（${err.message.slice(0, 40)}）`);
        });
    },
    [libraryId, activeAlgorithm?.id, JSON.stringify(paramValues), sourceImageApi],
    150
  );

  function onFileUpload(file: File) {
    const reader = new FileReader();
    reader.onload = () => {
      const base64 = String(reader.result);
      setSourceImage(base64);
      setResultImage(base64);
      normalizeImageForApi(base64)
        .then((apiImage) => setSourceImageApi(apiImage))
        .catch(() => setStatusText("状态：上传图像解析失败"));
    };
    reader.readAsDataURL(file);
  }

  return (
    <div className="app-shell">
      <header className="topbar panel">
        <div className="brand">
          <strong>cvAlgoVis</strong>
          <span>Industrial Console</span>
        </div>
        <div className="selectors">
          <LibrarySelector libraries={catalog?.libraries ?? []} value={libraryId} onChange={setLibraryId} />
          <AlgorithmSelector
            modules={activeLibrary?.modules ?? []}
            moduleId={activeModule?.id ?? ""}
            algorithmId={activeAlgorithm?.id ?? ""}
            onModuleChange={setModuleId}
            onAlgorithmChange={setAlgorithmId}
          />
        </div>
        <div className="actions">
          <label className="upload">
            上传图像
            <input
              type="file"
              hidden
              accept="image/*"
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (file) onFileUpload(file);
              }}
            />
          </label>
          <button
            className="ghost"
            onClick={() => {
              if (!sampleDataUrl) return;
              setSourceImage(sampleDataUrl);
              setResultImage(sampleDataUrl);
              normalizeImageForApi(sampleDataUrl)
                .then((apiImage) => setSourceImageApi(apiImage))
                .catch(() => setStatusText("状态：样例图解析失败"));
            }}
          >
            样例图
          </button>
        </div>
      </header>

      <main className="workspace">
        <div className="cell cell-result">
          <ImagePreviewPanel
            title="效果显示区（处理后图像）"
            image={resultImage || sourceImage}
            metaLeft={statusText}
            metaRight={`处理耗时：${elapsedMs} ms`}
          />
        </div>
        <div className="cell cell-params">
          <ParamControlPanel
            params={activeAlgorithm?.params ?? []}
            values={paramValues}
            onChange={(name, value) =>
              setParamValues((old) => ({
                ...old,
                [name]: value
              }))
            }
          />
        </div>
        <div className="cell cell-source">
          <ImagePreviewPanel title="原始图像区" image={sourceImage} metaLeft="输入图像" />
        </div>
        <div className="cell cell-code">
          <CodePanel
            snippet={snippet}
            highlightedHtml={highlightedSnippet}
            pygmentsCss={pygmentsCss}
            highlightAvailable={highlightAvailable}
            highlightMessage={highlightMessage}
            onCopy={() => {
              navigator.clipboard.writeText(snippet).catch(() => null);
            }}
          />
        </div>
      </main>
    </div>
  );
}
