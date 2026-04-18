# cvAlgoVis

`cvAlgoVis` 是一个面向教学、演示与快速验证的可交互视觉实验平台。项目当前同时支持：

- `OpenCV` 图像处理工作流
- `Open3D` 点云处理与点云配准工作流
- `Web` 开发模式
- `Windows` 桌面 EXE 打包与运行

界面左上角品牌当前显示为：`cvAlgoVis 词元视觉`。

## 项目定位

这个项目不是单纯的算法集合，而是一个“前端可调参 + 后端即时计算 + 结果可视化”的实验工作台：

- 前端负责算法切换、参数调节、样例载入和结果可视化
- 后端负责 OpenCV / Open3D 实际计算
- 图像和点云分别通过独立接口处理
- 代码片段、函数说明、结果摘要会同步显示，便于教学与调试

## 当前能力

### OpenCV 工作流

当前 OpenCV 已按 10 个模块组织：

- 颜色与强度处理
- 几何变换
- 阈值与二值化
- 去噪与平滑
- 形态学处理
- 梯度与边缘检测
- 图像分割
- 特征检测与描述
- 匹配与检索
- 增强处理

界面表现上，OpenCV 模式保持四区工作台：

- 左上：效果显示区
- 右上：参数设置区
- 左下：原始图像区
- 右下：代码区

同时支持：

- 滑块 + 数值输入 + 鼠标滚轮微调
- 代码片段高亮显示（Pygments）
- OpenCV 函数说明接口
- 前端节流调用 `/process` 实时反馈处理结果

### Open3D 工作流

当前 Open3D 已按 5 个模块组织：

- 点云基础处理
- 点云过滤采样
- 点云分割聚类
- 点云几何分析
- 点云配准

当前已支持的代表性能力包括：

- 体素下采样
- 法线估计
- 统计/半径离群点去除
- 平面分割与平面外点提取
- DBSCAN 聚类
- 轴对齐/有向包围盒
- 凸包、最近邻距离、点云间距离、马氏距离
- 刚体变换
- ICP 点到点 / 点到面配准
- FPFH 特征
- RANSAC / 快速全局配准
- 彩色 ICP
- 粗配准 + 精配准一体化流程
- 配准质量评估

当前 Open3D 界面特性包括：

- 支持上传 `ply` / `pcd`
- 支持源点云 / 目标点云双文件配准场景
- 支持样例点云一键载入
- 支持 `原始 / 处理后 / 目标对齐 / 叠加 / 误差视图`
- 支持法线估计结果可视化
- 支持配准结果摘要、质量等级和误差统计显示

### 当前内置点云样例

项目当前内置以下 Open3D 样例文件：

- `配准点云对`
- `旋转错位配准对`
- `平面 + 离群点`
- `立方体格点`
- `分层斜坡`
- `球壳点云`

对应文件位于 `frontend/public/samples/`。

## 界面截图

### 真实 UI 工作台

![真实 UI 工作台](frontend/public/screenshots/ui-workbench.png)

### 输入示意（原始图像）

![原始图像示意](frontend/public/screenshots/sample-before.svg)

### 输出示意（处理后图像）

![处理后图像示意](frontend/public/screenshots/sample-after.svg)

## 技术栈

- 前端：React + TypeScript + Vite
- 后端：FastAPI + OpenCV + Open3D + NumPy
- 桌面端：Electron + Python sidecar（PyInstaller）
- 测试：Pytest

## 当前目录结构

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
        open3d_algorithms.py
        open3d_pipeline.py
        opencv_reference.py
        pipeline.py
    tests/
      test_algorithms_unit.py
      test_api_process.py
      test_open3d_algorithms_unit.py
    entry.py
    pyinstaller.spec
    requirements.txt
  desktop/
    electron/
      main.js
      preload.js
      electron-builder.yml
      package.json
  docs/
    api.md
    desktop-packaging.md
  frontend/
    public/
      samples/
      screenshots/
    src/
      components/
      config/
      constants/
      api/
      App.tsx
      styles.css
      types.ts
    package.json
    vite.config.ts
  scripts/
    build-desktop-win.ps1
    clean-desktop.ps1
    smoke-test-desktop.ps1
  package.json
  README.md
```

## 环境要求

- Node.js 18+
- Python 3.10+
- pip

## 快速启动

### 1. 启动后端

```bash
cd backend
python -m venv .venv
```

Windows：

```bash
.venv\Scripts\activate
```

macOS/Linux：

```bash
source .venv/bin/activate
```

安装依赖并运行：

```bash
pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

后端地址：`http://127.0.0.1:8000`

### 2. 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端地址：`http://127.0.0.1:5173`

## 主要接口

当前后端主要提供以下接口：

- `GET /health`
- `GET /catalog`
- `GET /code-snippet?algorithm_id=...`
- `GET /opencv-reference`
- `POST /process`
- `POST /open3d/process`

说明：

- `/process` 用于 OpenCV 图像处理
- `/open3d/process` 用于 Open3D 点云处理
- `/catalog` 提供库、模块、算法和参数定义
- `/code-snippet` 返回算法 Python 代码片段和高亮 HTML

## 测试

在后端虚拟环境中执行：

```bash
cd backend
pytest -q
```

## 桌面软件打包

项目已提供基于 `Electron + Python sidecar` 的 Windows 一键自动化打包流程，默认输出可双击运行的便携版 EXE。

相关文件：

- `desktop/electron/`
- `backend/entry.py`
- `backend/pyinstaller.spec`
- `scripts/build-desktop-win.ps1`
- `scripts/clean-desktop.ps1`
- `scripts/smoke-test-desktop.ps1`
- `docs/desktop-packaging.md`

推荐命令：

```bash
npm run build:desktop
```

等价命令：

```bash
npm run build:desktop:win
```

该命令会自动执行：

1. 清理旧构建产物
2. 构建前端静态资源
3. 打包后端 sidecar
4. 使用 Electron Builder 输出 Windows portable EXE
5. 执行桌面包自检

默认产物位置：

- `dist-desktop/cvAlgoVis 0.1.0.exe`
- `dist-desktop/build-时间戳/win-unpacked/cvAlgoVis.exe`
- `dist-desktop/LATEST_BUILD.txt`

说明：

- 当前默认自动化目标为 Windows
- 桌面模式后端默认监听 `127.0.0.1:18000`
- 软件启动后会自动拉起静默后端，不弹黑框
- 前端会在桌面模式下读取运行时注入的 API 地址
- 若 `desktop/electron/node_modules/electron/dist` 缺失，脚本会先安装 Electron 依赖
- `dist-desktop/`、`backend/dist/`、`backend/build/`、`.runtime/`、`node_modules/`、`__pycache__/` 都属于构建或运行期产物，不需要手工提交

## OpenCV 函数清单（用途/参数/返回值）

以下函数已在 `backend/app/services/opencv_reference.py` 统一维护，并可通过 API 获取：

```text
GET /opencv-reference
```

| 函数                                        | 用途                  | 核心参数                                                                   | 返回值                     |
| ----------------------------------------- | ------------------- | ---------------------------------------------------------------------- | ----------------------- |
| `cv2.imread`                              | 从磁盘读取图像             | `filename`, `flags`                                                    | `ndarray` 或 `None`      |
| `cv2.cvtColor`                            | 色彩空间转换（如 BGR->GRAY） | `src`, `code`                                                          | 转换后的 `ndarray`          |
| `cv2.GaussianBlur`                        | 高斯滤波降噪              | `src`, `ksize`, `sigmaX`                                               | 模糊后 `ndarray`           |
| `cv2.Canny`                               | 边缘检测                | `image`, `threshold1`, `threshold2`, `apertureSize`                    | 单通道边缘图 `ndarray`        |
| `cv2.findContours`                        | 轮廓查找                | `image`, `mode`, `method`                                              | `(contours, hierarchy)` |
| `cv2.warpPerspective`                     | 透视变换                | `src`, `M`, `dsize`                                                    | 变换后 `ndarray`           |
| `cv2.matchTemplate`                       | 模板匹配定位              | `image`, `templ`, `method`                                             | 匹配响应图 `ndarray`         |
| `cv2.CascadeClassifier.detectMultiScale`  | 级联检测（如人脸）           | `image`, `scaleFactor`, `minNeighbors`, `minSize`                      | 检测框数组 `(x,y,w,h)`       |
| `cv2.adaptiveThreshold`                   | 自适应阈值二值化            | `src`, `maxValue`, `adaptiveMethod`, `thresholdType`, `blockSize`, `C` | 二值图 `ndarray`           |
| `cv2.morphologyEx`                        | 形态学复合操作             | `src`, `op`, `kernel`                                                  | 处理后图像 `ndarray`         |
| `cv2.grabCut`                             | 图割前景分割              | `img`, `mask`, `rect`, `iterCount`, `mode`                             | 更新后的 `mask`             |
| `cv2.goodFeaturesToTrack`                 | Shi-Tomasi 角点检测     | `image`, `maxCorners`, `qualityLevel`, `minDistance`                   | 角点坐标数组                  |
| `cv2.BFMatcher` / `cv2.FlannBasedMatcher` | 特征匹配器               | 匹配器配置参数                                                                | 匹配器对象                   |

## 常见问题

### `python -m venv .venv` 失败

- 现象：`python: command not found` 或命令直接退出
- 原因：系统未安装可用 Python 或 PATH 未配置
- 建议：先执行 `python --version`，确认解释器可用后再创建虚拟环境

### 代码区高亮不是彩色

- 现象：代码区显示纯文本，状态提示为“高亮已降级”
- 原因：`/code-snippet` 接口不可用（常见于后端未启动）
- 建议：先启动后端，再刷新前端页面；后端可用时状态会变为“高亮已启用（Pygments）”

## 联系方式

![微信公众号](frontend/public/samples/contact.png)

如果大家不想自己编译，可以
关注微信公众号后回复：cvAlgoVis，免费获取cvAlgoVis 软件（单一exe软件可直接打开）
