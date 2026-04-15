import { useEffect, useMemo, useState } from "react";

import { fetchCatalog, fetchSnippet, processImage, processOpen3D } from "./api/client";
import { AlgorithmSelector } from "./components/AlgorithmSelector";
import { CodePanel } from "./components/CodePanel";
import { ImagePreviewPanel } from "./components/ImagePreviewPanel";
import { LibrarySelector } from "./components/LibrarySelector";
import { ParamControlPanel } from "./components/ParamControlPanel";
import { PointCloudViewer } from "./components/PointCloudViewer";
import { OPEN3D_SAMPLES } from "./constants/open3dSamples";
import { useDebouncedEffect } from "./hooks/useDebouncedEffect";
import type { CatalogResponse, Open3DProcessResponse } from "./types";

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
  const [open3dFile, setOpen3dFile] = useState<File | null>(null);
  const [sampleOpen3dFile, setSampleOpen3dFile] = useState<File | null>(null);
  const [selectedOpen3dSampleId, setSelectedOpen3dSampleId] = useState(OPEN3D_SAMPLES[0]?.id ?? "");
  const [open3dResult, setOpen3dResult] = useState<Open3DProcessResponse | null>(null);
  const [snippet, setSnippet] = useState<string>("# loading...");
  const [highlightedSnippet, setHighlightedSnippet] = useState<string>("<pre># loading...</pre>");
  const [pygmentsCss, setPygmentsCss] = useState<string>("");
  const [highlightAvailable, setHighlightAvailable] = useState(false);
  const [highlightMessage, setHighlightMessage] = useState("高亮状态初始化中");
  const [statusText, setStatusText] = useState("状态：Ready");
  const [elapsedMs, setElapsedMs] = useState(0);
  const [pointScale, setPointScale] = useState(1);
  const [viewerResetToken, setViewerResetToken] = useState(0);
  const [open3dViewMode, setOpen3dViewMode] = useState<"source" | "processed" | "overlay">("overlay");

  const activeLibrary = useMemo(() => {
    return catalog?.libraries.find((library) => library.id === libraryId);
  }, [catalog, libraryId]);

  const activeModule = useMemo(() => {
    return activeLibrary?.modules.find((module) => module.id === moduleId) ?? activeLibrary?.modules[0];
  }, [activeLibrary, moduleId]);

  const activeAlgorithm = useMemo(() => {
    return activeModule?.algorithms.find((algorithm) => algorithm.id === algorithmId) ?? activeModule?.algorithms[0];
  }, [activeModule, algorithmId]);

  const isOpen3D = activeLibrary?.id === "open3d";
  const selectedOpen3dSample = useMemo(
    () => OPEN3D_SAMPLES.find((sample) => sample.id === selectedOpen3dSampleId) ?? OPEN3D_SAMPLES[0],
    [selectedOpen3dSampleId]
  );
  const recommendedOpen3dSample = useMemo(() => {
    if (!activeAlgorithm) return OPEN3D_SAMPLES[0];
    return OPEN3D_SAMPLES.find((sample) => sample.recommendedAlgorithms.includes(activeAlgorithm.id)) ?? OPEN3D_SAMPLES[0];
  }, [activeAlgorithm]);

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

  function formatFileSize(bytes: number): string {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
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
    if (!selectedOpen3dSample) return;
    fetch(selectedOpen3dSample.file)
      .then((res) => {
        if (!res.ok) throw new Error("sample point cloud fetch failed");
        return res.blob();
      })
      .then((blob) => {
        const fileName = selectedOpen3dSample.file.split("/").pop() ?? `${selectedOpen3dSample.id}.ply`;
        const sample = new File([blob], fileName, { type: "application/octet-stream" });
        setSampleOpen3dFile(sample);
      })
      .catch(() => null);
  }, [selectedOpen3dSample]);

  useEffect(() => {
    if (!isOpen3D || !recommendedOpen3dSample) return;
    if (selectedOpen3dSampleId === recommendedOpen3dSample.id) return;
    setSelectedOpen3dSampleId(recommendedOpen3dSample.id);
  }, [isOpen3D, recommendedOpen3dSample, selectedOpen3dSampleId]);

  useEffect(() => {
    if (!isOpen3D || !sampleOpen3dFile) return;
    onPointCloudUpload(sampleOpen3dFile, `状态：已自动载入样例点云 ${sampleOpen3dFile.name}`);
  }, [isOpen3D, sampleOpen3dFile]);

  useEffect(() => {
    if (!activeLibrary) return;
    const nextModule = activeLibrary.modules.find((module) => module.id === moduleId) ?? activeLibrary.modules[0];
    if (!nextModule) return;
    if (nextModule.id !== moduleId) {
      setModuleId(nextModule.id);
      return;
    }
    const nextAlgorithm =
      nextModule.algorithms.find((algorithm) => algorithm.id === algorithmId) ?? nextModule.algorithms[0];
    if (nextAlgorithm && nextAlgorithm.id !== algorithmId) {
      setAlgorithmId(nextAlgorithm.id);
    }
  }, [activeLibrary, moduleId, algorithmId]);

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
      if (isOpen3D) {
        if (!open3dFile) {
          setStatusText("状态：请先上传点云文件");
          return;
        }
        setStatusText("状态：Open3D Processing...");
        processOpen3D({
          algorithm_id: activeAlgorithm.id,
          params: paramValues,
          file: open3dFile
        })
          .then((res) => {
            setOpen3dResult(res);
            setElapsedMs(res.meta.elapsed_ms);
            setStatusText("状态：Ready");
          })
          .catch((err: Error) => {
            setStatusText(`状态：Open3D 处理失败（${err.message.slice(0, 40)}）`);
          });
        return;
      }

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
    [
      libraryId,
      isOpen3D,
      activeAlgorithm?.id,
      JSON.stringify(paramValues),
      sourceImageApi,
      open3dFile?.name,
      open3dFile?.size,
      open3dFile?.lastModified
    ],
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

  function onPointCloudUpload(file: File, message?: string) {
    setOpen3dFile(file);
    setOpen3dResult(null);
    setElapsedMs(0);
    setStatusText(message ?? `状态：已载入点云文件 ${file.name}`);
  }

  function loadSamplePointCloud() {
    if (!sampleOpen3dFile) {
      setStatusText("状态：样例点云加载失败");
      return;
    }
    onPointCloudUpload(sampleOpen3dFile);
  }

  const open3dResultLines = useMemo(() => {
    if (!open3dResult) {
      return [
        "等待 Open3D 处理结果。",
        "处理完成后会展示点数变化与算法统计信息。",
        "首版不提供点云三维可视化，先返回摘要与元数据。"
      ];
    }

    const statsLines = Object.entries(open3dResult.stats).map(([key, value]) => {
      const rendered = Array.isArray(value) ? value.join(", ") : String(value);
      return `${key}: ${rendered}`;
    });

    return [
      open3dResult.summary,
      `输入点数：${open3dResult.meta.points_before}`,
      `输出点数：${open3dResult.meta.points_after}`,
      `文件类型：${open3dResult.meta.file_type}`,
      ...statsLines
    ];
  }, [open3dResult]);

  const open3dOverlayLayers = useMemo(() => {
    if (!open3dResult) return [];
    return [
      { points: open3dResult.source_points, color: "#4da3ff", size: 0.06 },
      { points: open3dResult.processed_points, color: "#ffd84d", size: 0.095 }
    ];
  }, [open3dResult]);

  const open3dProcessedLayers = useMemo(() => {
    if (!open3dResult) return [];
    return [{ points: open3dResult.processed_points, color: "#ffd84d", size: 0.095 }];
  }, [open3dResult]);

  const open3dMainLayers = useMemo(() => {
    if (open3dViewMode === "source") {
      return open3dResult ? [{ points: open3dResult.source_points, color: "#4da3ff", size: 0.085 }] : [];
    }
    if (open3dViewMode === "processed") {
      return open3dProcessedLayers;
    }
    return open3dOverlayLayers;
  }, [open3dOverlayLayers, open3dProcessedLayers, open3dResult, open3dViewMode]);

  const open3dInfoLines = useMemo(() => {
    const fileLine = open3dFile
      ? `文件：${open3dFile.name} · ${formatFileSize(open3dFile.size)}`
      : sampleOpen3dFile
        ? `当前样例：${selectedOpen3dSample?.label ?? "未命名样例"}`
        : "内置样例点云加载中。";

    const descriptionLine = selectedOpen3dSample
      ? `说明：${selectedOpen3dSample.description}`
      : "说明：请上传或选择样例点云。";
    const recommendedLine = selectedOpen3dSample?.recommendedAlgorithms.length
      ? `推荐算法：${selectedOpen3dSample.recommendedAlgorithms.join(" / ")}`
      : "推荐算法：通用点云基础处理";
    const matchedLine =
      selectedOpen3dSample && activeAlgorithm && selectedOpen3dSample.recommendedAlgorithms.includes(activeAlgorithm.id)
        ? `当前算法已匹配推荐样例：${activeAlgorithm.id}`
        : `当前算法：${activeAlgorithm?.id ?? "未选择"}`;

    return [fileLine, descriptionLine, recommendedLine, matchedLine, ...open3dResultLines];
  }, [activeAlgorithm, open3dFile, open3dResultLines, sampleOpen3dFile, selectedOpen3dSample]);

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
          {isOpen3D ? (
            <label>
              样例选择
              <select value={selectedOpen3dSampleId} onChange={(e) => setSelectedOpen3dSampleId(e.target.value)}>
                {OPEN3D_SAMPLES.map((sample) => (
                  <option key={sample.id} value={sample.id}>
                    {sample.label}
                  </option>
                ))}
              </select>
            </label>
          ) : null}
          <label className="upload">
            {isOpen3D ? "上传点云" : "上传图像"}
            <input
              type="file"
              hidden
              accept={isOpen3D ? ".ply,.pcd" : "image/*"}
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (!file) return;
                if (isOpen3D) {
                  onPointCloudUpload(file);
                } else {
                  onFileUpload(file);
                }
              }}
            />
          </label>
          {!isOpen3D ? (
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
          ) : (
            <button className="ghost" onClick={loadSamplePointCloud} disabled={!sampleOpen3dFile}>
              重新载入样例
            </button>
          )}
        </div>
      </header>

      <main className={`workspace ${isOpen3D ? "workspace-open3d" : ""}`}>
        <div className="cell cell-result">
          {isOpen3D ? (
            <section className="panel preview-panel open3d-preview-panel">
              <div className="panel-title">效果展示区（Open3D 点云视图）</div>
              <div className="point-cloud-toolbar">
                <div className="point-cloud-mode-switch">
                  <button
                    className={`ghost small ${open3dViewMode === "source" ? "mode-active" : ""}`}
                    onClick={() => setOpen3dViewMode("source")}
                  >
                    原始
                  </button>
                  <button
                    className={`ghost small ${open3dViewMode === "processed" ? "mode-active" : ""}`}
                    onClick={() => setOpen3dViewMode("processed")}
                  >
                    处理后
                  </button>
                  <button
                    className={`ghost small ${open3dViewMode === "overlay" ? "mode-active" : ""}`}
                    onClick={() => setOpen3dViewMode("overlay")}
                  >
                    叠加
                  </button>
                </div>
                <div className="point-cloud-toolbar-actions">
                  <button className="ghost small" onClick={() => setViewerResetToken((value) => value + 1)}>
                    重置视角
                  </button>
                </div>
                <label className="point-scale-control">
                  <span>{`点大小 ${pointScale.toFixed(1)}x`}</span>
                  <input
                    type="range"
                    min={0.6}
                    max={2.6}
                    step={0.1}
                    value={pointScale}
                    onChange={(e) => setPointScale(Number(e.target.value))}
                  />
                </label>
              </div>
              <PointCloudViewer
                layers={open3dMainLayers}
                emptyMessage="请先上传或载入样例点云，随后将在此显示点云效果。"
                pointScale={pointScale}
                resetToken={viewerResetToken}
              />
              <div className="point-cloud-legend">
                {(open3dViewMode === "source" || open3dViewMode === "overlay") && (
                  <span className="legend-item">
                    <i className="legend-dot legend-source" />
                    原始点云
                  </span>
                )}
                {(open3dViewMode === "processed" || open3dViewMode === "overlay") && (
                  <span className="legend-item">
                    <i className="legend-dot legend-processed" />
                    处理后点云
                  </span>
                )}
              </div>
              <div className="preview-meta">
                <span>{statusText}</span>
                <span>{open3dFile ? open3dFile.name : `处理耗时：${elapsedMs} ms`}</span>
              </div>
              <div className="point-cloud-details compact">
                {open3dInfoLines.map((line) => (
                  <div className="point-cloud-detail-line" key={line}>
                    {line}
                  </div>
                ))}
              </div>
            </section>
          ) : (
            <ImagePreviewPanel
              title="效果显示区（处理后图像）"
              image={resultImage || sourceImage}
              metaLeft={statusText}
              metaRight={`处理耗时：${elapsedMs} ms`}
            />
          )}
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
        {!isOpen3D ? (
          <div className="cell cell-source">
            <ImagePreviewPanel title="原始图像区" image={sourceImage} metaLeft="输入图像" />
          </div>
        ) : null}
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
