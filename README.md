# cvAlgoVis

一个可交互的计算机视觉实验应用：前端实时调参，后端基于 OpenCV 处理图像并返回结果。

## 功能概览

- 三栏工作台：代码区 / 图像区 / 参数区
- 图像区双面板：原始图像 + 处理后图像
- 算法切换：边缘、阈值、形态学、滤波、锐化
- 参数交互：滑块 + 数值输入 + 鼠标滚轮微调
- 实时反馈：前端节流调用 `/process`
- 开发辅助：算法 Python 代码片段 + OpenCV 函数说明

## 界面截图

### 真实 UI 工作台

![真实 UI 工作台](frontend/public/screenshots/ui-workbench.png)

### 输入示意（原始图像）

![原始图像示意](frontend/public/screenshots/sample-before.svg)

### 输出示意（处理后图像）

![处理后图像示意](frontend/public/screenshots/sample-after.svg)

## 技术栈

- 前端：React + TypeScript + Vite
- 后端：FastAPI + OpenCV + NumPy
- 测试：Pytest（单元 + 集成）

## 当前目录结构（与项目现状一致）

```text
cvAlgoVis/
  backend/
    app/
      main.py
      catalog.py
      schemas.py
      examples/
        code_snippets.py
      services/
        algorithms.py
        image_io.py
        opencv_reference.py
        pipeline.py
    tests/
      test_algorithms_unit.py
      test_api_process.py
    requirements.txt
  frontend/
    public/
      samples/sample-1.svg
      screenshots/
        ui-workbench.png
        sample-before.svg
        sample-after.svg
    src/
      api/client.ts
      components/
        AlgorithmSelector.tsx
        CodePanel.tsx
        ImagePreviewPanel.tsx
        LibrarySelector.tsx
        ParamControlPanel.tsx
      config/libraryAlgorithmMap.ts
      hooks/
        useDebouncedEffect.ts
        useWheelAdjust.ts
      App.tsx
      main.tsx
      styles.css
      types.ts
    index.html
    package.json
    tsconfig.json
    vite.config.ts
  README.md
  .gitignore
```

## 环境要求

- Node.js 18+
- Python 3.10+
- pip

## 快速启动

### 1) 启动后端

```bash
cd backend
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

安装依赖并运行：

```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

后端地址：`http://localhost:8000`

### 2) 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端地址：`http://localhost:5173`

## 测试

在后端虚拟环境中执行：

```bash
cd backend
pytest -q
```

## OpenCV 函数清单（用途/参数/返回值）

以下函数已在 `backend/app/services/opencv_reference.py` 统一维护，并可通过 API 获取：

```text
GET /opencv-reference
```

| 函数 | 用途 | 核心参数 | 返回值 |
| --- | --- | --- | --- |
| `cv2.imread` | 从磁盘读取图像 | `filename`, `flags` | `ndarray` 或 `None` |
| `cv2.cvtColor` | 色彩空间转换（如 BGR->GRAY） | `src`, `code` | 转换后的 `ndarray` |
| `cv2.GaussianBlur` | 高斯滤波降噪 | `src`, `ksize`, `sigmaX` | 模糊后 `ndarray` |
| `cv2.Canny` | 边缘检测 | `image`, `threshold1`, `threshold2`, `apertureSize` | 单通道边缘图 `ndarray` |
| `cv2.findContours` | 轮廓查找 | `image`, `mode`, `method` | `(contours, hierarchy)` |
| `cv2.warpPerspective` | 透视变换 | `src`, `M`, `dsize` | 变换后 `ndarray` |
| `cv2.matchTemplate` | 模板匹配定位 | `image`, `templ`, `method` | 匹配响应图 `ndarray` |
| `cv2.CascadeClassifier.detectMultiScale` | 级联检测（如人脸） | `image`, `scaleFactor`, `minNeighbors`, `minSize` | 检测框数组 `(x,y,w,h)` |

## 常见问题

### `python -m venv .venv` 失败

- 现象：`python: command not found` 或命令直接退出
- 原因：系统未安装可用 Python 或 PATH 未配置
- 建议：先执行 `python --version`，确认解释器可用后再创建虚拟环境

## 联系方式

![微信公众号](frontend/public/samples/contact.jpg)


