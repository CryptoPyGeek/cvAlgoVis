const { app, BrowserWindow } = require("electron");
const http = require("http");
const path = require("path");
const fs = require("fs");
const { spawn } = require("child_process");

let backendProcess = null;
const runtimeDataDir = path.resolve(__dirname, ".runtime");
const API_BASE = "http://127.0.0.1:18000";

function configureUserDataPath() {
  if (!app.isPackaged) {
    fs.mkdirSync(runtimeDataDir, { recursive: true });
    app.setPath("userData", runtimeDataDir);
    return;
  }

  const portableDir =
    process.env.PORTABLE_EXECUTABLE_DIR || path.dirname(app.getPath("exe"));
  const packagedRuntimeDir = path.join(portableDir, ".runtime");
  fs.mkdirSync(packagedRuntimeDir, { recursive: true });
  app.setPath("userData", packagedRuntimeDir);
}

configureUserDataPath();

function getBackendExecutable() {
  const exeName = process.platform === "win32" ? "cvAlgoVis-backend.exe" : "cvAlgoVis-backend";
  const packaged = path.join(process.resourcesPath, "backend", exeName);
  const dev = path.resolve(__dirname, "..", "..", "backend", "dist", exeName);
  return fs.existsSync(packaged) ? packaged : dev;
}

function startBackend() {
  const backendExecutable = getBackendExecutable();
  const env = {
    ...process.env,
    CVALGOVIS_HOST: "127.0.0.1",
    CVALGOVIS_PORT: "18000",
    CVALGOVIS_API_BASE: API_BASE
  };
  backendProcess = spawn(backendExecutable, [], {
    env,
    stdio: "ignore",
    windowsHide: true
  });
}

function getFrontendEntry() {
  if (process.env.CVALGOVIS_DEV_SERVER_URL) {
    return process.env.CVALGOVIS_DEV_SERVER_URL;
  }
  if (app.isPackaged) {
    return path.join(process.resourcesPath, "frontend", "index.html");
  }
  return path.resolve(__dirname, "..", "..", "frontend", "dist", "index.html");
}

function waitForBackendReady(timeoutMs = 15000) {
  const startedAt = Date.now();

  return new Promise((resolve, reject) => {
    const attempt = () => {
      const req = http.get(`${API_BASE}/health`, (res) => {
        res.resume();
        if (res.statusCode === 200) {
          resolve();
          return;
        }
        retry();
      });

      req.on("error", retry);
      req.setTimeout(1500, () => {
        req.destroy();
        retry();
      });
    };

    const retry = () => {
      if (Date.now() - startedAt > timeoutMs) {
        reject(new Error("Backend startup timed out"));
        return;
      }
      setTimeout(attempt, 300);
    };

    attempt();
  });
}

function createWindow() {
  const win = new BrowserWindow({
    width: 1440,
    height: 960,
    show: false,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false
    }
  });

  win.once("ready-to-show", () => {
    win.show();
  });

  const frontendEntry = getFrontendEntry();
  if (process.env.CVALGOVIS_DEV_SERVER_URL) {
    win.loadURL(frontendEntry);
  } else {
    win.loadFile(frontendEntry);
  }
}

app.whenReady().then(async () => {
  try {
    startBackend();
    await waitForBackendReady();
    createWindow();
  } catch (error) {
    console.error(error);
    app.quit();
  }
});

app.on("window-all-closed", () => {
  if (backendProcess) {
    backendProcess.kill();
    backendProcess = null;
  }
  if (process.platform !== "darwin") {
    app.quit();
  }
});
