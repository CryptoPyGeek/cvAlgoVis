import { useEffect, useMemo, useRef, useState } from "react";

import { fetchCatalog, fetchSnippet, processImage, processOpen3D } from "./api/client";
import { AlgorithmSelector } from "./components/AlgorithmSelector";
import { CodePanel } from "./components/CodePanel";
import { ImagePreviewPanel } from "./components/ImagePreviewPanel";
import { LibrarySelector } from "./components/LibrarySelector";
import { Open3DRegistrationSummary } from "./components/Open3DRegistrationSummary";
import { ParamControlPanel } from "./components/ParamControlPanel";
import { PointCloudViewer } from "./components/PointCloudViewer";
import { OPEN3D_SAMPLES } from "./constants/open3dSamples";
import { useDebouncedEffect } from "./hooks/useDebouncedEffect";
import type { CatalogResponse, Open3DProcessResponse } from "./types";

const SAMPLE_IMAGE = `${import.meta.env.BASE_URL}samples/contact.png`;
const OPEN3D_REGISTRATION_ALGORITHMS = new Set([
  "registration_icp_point_to_point",
  "registration_icp_point_to_plane",
  "registration_ransac_based_on_feature_matching",
  "registration_fast_based_on_feature_matching",
  "registration_colored_icp",
  "registration_ransac_then_icp_point_to_plane",
  "registration_fast_then_icp_point_to_plane",
  "evaluate_registration"
]);
const OPEN3D_TARGET_ALGORITHMS = new Set([
  "registration_icp_point_to_point",
  "registration_icp_point_to_plane",
  "registration_ransac_based_on_feature_matching",
  "registration_fast_based_on_feature_matching",
  "registration_colored_icp",
  "registration_ransac_then_icp_point_to_plane",
  "registration_fast_then_icp_point_to_plane",
  "evaluate_registration",
  "compute_point_cloud_distance"
]);

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
  const [open3dTargetFile, setOpen3dTargetFile] = useState<File | null>(null);
  const [sampleOpen3dFile, setSampleOpen3dFile] = useState<File | null>(null);
  const [sampleOpen3dTargetFile, setSampleOpen3dTargetFile] = useState<File | null>(null);
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
  const [isOpen3dProcessing, setIsOpen3dProcessing] = useState(false);
  const [lastAppliedAlgorithmId, setLastAppliedAlgorithmId] = useState<string | null>(null);
  const [lastAppliedParamsSignature, setLastAppliedParamsSignature] = useState<string>("");
  const [lastAppliedParamValues, setLastAppliedParamValues] = useState<Record<string, number>>({});
  const latestOpen3dRequestRef = useRef(0);
  const open3dAbortRef = useRef<AbortController | null>(null);

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
  const isRegistrationAlgorithm = activeAlgorithm
    ? OPEN3D_REGISTRATION_ALGORITHMS.has(activeAlgorithm.id)
    : false;
  const requiresTargetPointCloud = activeAlgorithm
    ? OPEN3D_TARGET_ALGORITHMS.has(activeAlgorithm.id)
    : false;
  const currentOpen3dParamsSignature = useMemo(() => JSON.stringify(paramValues), [paramValues]);
  const isCurrentOpen3dResultFresh =
    !isOpen3dProcessing &&
    Boolean(open3dResult) &&
    lastAppliedAlgorithmId === activeAlgorithm?.id &&
    lastAppliedParamsSignature === currentOpen3dParamsSignature;
  const registrationHintSampleIds = new Set(["registration-pair"]);

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

    if (!selectedOpen3dSample.targetFile) {
      setSampleOpen3dTargetFile(null);
      return;
    }

    fetch(selectedOpen3dSample.targetFile)
      .then((res) => {
        if (!res.ok) throw new Error("sample target point cloud fetch failed");
        return res.blob();
      })
      .then((blob) => {
        const fileName = selectedOpen3dSample.targetFile?.split("/").pop() ?? `${selectedOpen3dSample.id}-target.ply`;
        const sample = new File([blob], fileName, { type: "application/octet-stream" });
        setSampleOpen3dTargetFile(sample);
      })
      .catch(() => setSampleOpen3dTargetFile(null));
  }, [selectedOpen3dSample]);

  useEffect(() => {
    if (!isOpen3D || !recommendedOpen3dSample) return;
    if (selectedOpen3dSampleId === recommendedOpen3dSample.id) return;
    setSelectedOpen3dSampleId(recommendedOpen3dSample.id);
  }, [isOpen3D, recommendedOpen3dSample, selectedOpen3dSampleId]);

  useEffect(() => {
    if (!isOpen3D || !sampleOpen3dFile) return;
    if (requiresTargetPointCloud && selectedOpen3dSample?.targetFile && !sampleOpen3dTargetFile) return;
    onPointCloudUpload(sampleOpen3dFile, `状态：已自动载入样例点云 ${sampleOpen3dFile.name}`);
    if (requiresTargetPointCloud && sampleOpen3dTargetFile) {
      onTargetPointCloudUpload(sampleOpen3dTargetFile, `状态：已自动载入目标点云 ${sampleOpen3dTargetFile.name}`);
    }
  }, [isOpen3D, requiresTargetPointCloud, sampleOpen3dFile, sampleOpen3dTargetFile, selectedOpen3dSample]);

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
          setIsOpen3dProcessing(false);
          setStatusText("状态：请先上传点云文件");
          return;
        }
        if (requiresTargetPointCloud && !open3dTargetFile) {
          setIsOpen3dProcessing(false);
          setStatusText("状态：该算法请同时上传目标点云");
          return;
        }
        latestOpen3dRequestRef.current += 1;
        const requestId = latestOpen3dRequestRef.current;
        open3dAbortRef.current?.abort();
        const controller = new AbortController();
        open3dAbortRef.current = controller;
        setIsOpen3dProcessing(true);
        setStatusText(open3dResult ? "状态：参数已更新，等待最新结果" : "状态：Open3D Processing...");
        processOpen3D({
          algorithm_id: activeAlgorithm.id,
          params: paramValues,
          file: open3dFile,
          target_file: requiresTargetPointCloud ? open3dTargetFile : undefined,
          signal: controller.signal
        })
          .then((res) => {
            if (requestId !== latestOpen3dRequestRef.current) return;
            setOpen3dResult(res);
            setElapsedMs(res.meta.elapsed_ms);
            setLastAppliedAlgorithmId(activeAlgorithm.id);
            setLastAppliedParamsSignature(currentOpen3dParamsSignature);
            setLastAppliedParamValues({ ...paramValues });
            setIsOpen3dProcessing(false);
            setStatusText("状态：Ready");
          })
          .catch((err: Error) => {
            if (requestId !== latestOpen3dRequestRef.current) return;
            if (err.name === "AbortError") return;
            setIsOpen3dProcessing(false);
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
      isRegistrationAlgorithm,
      requiresTargetPointCloud,
      activeAlgorithm?.id,
      currentOpen3dParamsSignature,
      sourceImageApi,
      open3dFile?.name,
      open3dFile?.size,
      open3dFile?.lastModified,
      open3dTargetFile?.name,
      open3dTargetFile?.size,
      open3dTargetFile?.lastModified
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
    open3dAbortRef.current?.abort();
    setIsOpen3dProcessing(false);
    setOpen3dFile(file);
    setOpen3dResult(null);
    setLastAppliedAlgorithmId(null);
    setLastAppliedParamsSignature("");
    setLastAppliedParamValues({});
    setElapsedMs(0);
    setStatusText(message ?? `状态：已载入点云文件 ${file.name}`);
  }

  function onTargetPointCloudUpload(file: File, message?: string) {
    open3dAbortRef.current?.abort();
    setIsOpen3dProcessing(false);
    setOpen3dTargetFile(file);
    setOpen3dResult(null);
    setLastAppliedAlgorithmId(null);
    setLastAppliedParamsSignature("");
    setLastAppliedParamValues({});
    setElapsedMs(0);
    setStatusText(message ?? `状态：已载入目标点云 ${file.name}`);
  }

  function loadSamplePointCloud() {
    if (!sampleOpen3dFile) {
      setStatusText("状态：样例点云加载失败");
      return;
    }
    onPointCloudUpload(sampleOpen3dFile);
    if (requiresTargetPointCloud && sampleOpen3dTargetFile) {
      onTargetPointCloudUpload(sampleOpen3dTargetFile);
    }
  }

  const open3dResultLines = useMemo(() => {
    if (!open3dResult) {
      return [
        "等待 Open3D 处理结果。",
        isOpen3dProcessing ? "参数已更新，正在计算最新结果。" : "处理完成后会展示点数变化与算法统计信息。",
        requiresTargetPointCloud ? "该算法需要同时提供源点云和目标点云。" : "支持在左侧三维视图中直接观察点云结果。"
      ];
    }

    const statsLines = Object.entries(open3dResult.stats).flatMap(([key, value]) => {
      if (Array.isArray(value) && value.length > 0 && Array.isArray(value[0])) {
        const rows = value as number[][];
        return [
          `${key}:`,
          ...rows.map((row, index) => `  row${index}: ${row.map((item) => Number(item).toFixed(4)).join(", ")}`)
        ];
      }
      const rendered = Array.isArray(value) ? value.join(", ") : String(value);
      return `${key}: ${rendered}`;
    });

    return [
      open3dResult.summary,
      isCurrentOpen3dResultFresh ? "结果状态：当前显示为最新参数结果" : "结果状态：当前显示为上一版结果，正在刷新",
      `输入点数：${open3dResult.meta.points_before}`,
      `输出点数：${open3dResult.meta.points_after}`,
      `文件类型：${open3dResult.meta.file_type}`,
      ...statsLines
    ];
  }, [isCurrentOpen3dResultFresh, isOpen3dProcessing, open3dResult, requiresTargetPointCloud]);

  const open3dOverlayLayers = useMemo(() => {
    if (!open3dResult) return [];
    if (requiresTargetPointCloud) {
      return [
        { points: open3dResult.target_points, color: "#47d7ac", size: 0.07 },
        { points: open3dResult.processed_points, color: "#ffd84d", size: 0.095 }
      ];
    }
    return [
      { points: open3dResult.source_points, color: "#4da3ff", size: 0.06 },
      { points: open3dResult.processed_points, color: "#ffd84d", size: 0.095 }
    ];
  }, [open3dResult, requiresTargetPointCloud]);

  const open3dProcessedLayers = useMemo(() => {
    if (!open3dResult) return [];
    return [{ points: open3dResult.processed_points, color: "#ffd84d", size: 0.095 }];
  }, [open3dResult]);

  const open3dReferenceLayers = useMemo(() => {
    if (!open3dResult) return [];
    const layers = [];
    if (open3dResult.source_points.length > 0) {
      layers.push({ points: open3dResult.source_points, color: "#4da3ff", size: 0.06 });
    }
    if (open3dResult.target_points.length > 0) {
      layers.push({ points: open3dResult.target_points, color: "#47d7ac", size: 0.07 });
    }
    if (open3dResult.processed_points.length > 0) {
      layers.push({ points: open3dResult.processed_points, color: "#ffd84d", size: 0.095 });
    }
    return layers;
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
      ? `源文件：${open3dFile.name} · ${formatFileSize(open3dFile.size)}`
      : sampleOpen3dFile
        ? `当前样例：${selectedOpen3dSample?.label ?? "未命名样例"}`
        : "内置样例点云加载中。";
    const targetLine =
      requiresTargetPointCloud && open3dTargetFile
        ? `目标文件：${open3dTargetFile.name} · ${formatFileSize(open3dTargetFile.size)}`
        : requiresTargetPointCloud && sampleOpen3dTargetFile
          ? `目标样例：${sampleOpen3dTargetFile.name}`
          : requiresTargetPointCloud
            ? "目标点云：请上传或使用配准样例。"
            : null;

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
    const freshnessLine = open3dResult
      ? isCurrentOpen3dResultFresh
        ? "结果一致性：已与当前参数同步"
        : "结果一致性：参数已变更，正在等待最新结果"
      : isOpen3dProcessing
        ? "结果一致性：正在生成首个结果"
        : null;

    return [fileLine, targetLine, descriptionLine, recommendedLine, matchedLine, freshnessLine, ...open3dResultLines].filter(Boolean) as string[];
  }, [
    activeAlgorithm,
    isRegistrationAlgorithm,
    isCurrentOpen3dResultFresh,
    isOpen3dProcessing,
    requiresTargetPointCloud,
    open3dFile,
    open3dResult,
    open3dResultLines,
    open3dTargetFile,
    sampleOpen3dFile,
    sampleOpen3dTargetFile,
    selectedOpen3dSample
  ]);

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
          {isOpen3D && requiresTargetPointCloud ? (
            <label className="upload">
              上传目标点云
              <input
                type="file"
                hidden
                accept=".ply,.pcd"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (!file) return;
                  onTargetPointCloudUpload(file);
                }}
              />
            </label>
          ) : null}
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
                referenceLayers={open3dReferenceLayers}
                emptyMessage={
                  requiresTargetPointCloud
                    ? "请先上传源点云和目标点云，或载入配准样例对。"
                    : "请先上传或载入样例点云，随后将在此显示点云效果。"
                }
                pointScale={pointScale}
                resetToken={viewerResetToken}
              />
              <div className="point-cloud-legend">
                {(open3dViewMode === "source" || (open3dViewMode === "overlay" && !requiresTargetPointCloud)) && (
                  <span className="legend-item">
                    <i className="legend-dot legend-source" />
                    原始点云
                  </span>
                )}
                {requiresTargetPointCloud && open3dViewMode === "overlay" && (
                  <span className="legend-item">
                    <i className="legend-dot legend-target" />
                    目标点云
                  </span>
                )}
                {(open3dViewMode === "processed" || open3dViewMode === "overlay") && (
                  <span className="legend-item">
                    <i className="legend-dot legend-processed" />
                    {requiresTargetPointCloud ? (isRegistrationAlgorithm ? "配准后源点云" : "源点云") : "处理后点云"}
                  </span>
                )}
              </div>
              <div className="preview-meta">
                <span>{statusText}</span>
                <span>{open3dFile ? open3dFile.name : `处理耗时：${elapsedMs} ms`}</span>
              </div>
              {isRegistrationAlgorithm && open3dResult ? (
                <Open3DRegistrationSummary
                  algorithmId={open3dResult.meta.algorithm}
                  result={open3dResult}
                  paramsSnapshot={lastAppliedParamValues}
                  isFresh={isCurrentOpen3dResultFresh}
                  sampleDescription={selectedOpen3dSample?.description}
                  showDifferenceHint={Boolean(selectedOpen3dSample && registrationHintSampleIds.has(selectedOpen3dSample.id))}
                />
              ) : null}
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
