const { app, BrowserWindow } = require("electron");
const path = require("path");
const fs = require("fs");
const { spawn } = require("child_process");

let backendProcess = null;

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
    CVALGOVIS_API_BASE: "http://127.0.0.1:18000"
  };
  backendProcess = spawn(backendExecutable, [], {
    env,
    stdio: "ignore",
    windowsHide: true
  });
}

function createWindow() {
  const win = new BrowserWindow({
    width: 1440,
    height: 960,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false
    }
  });

  if (process.env.CVALGOVIS_DEV_SERVER_URL) {
    win.loadURL(process.env.CVALGOVIS_DEV_SERVER_URL);
  } else {
    const indexPath = path.resolve(__dirname, "..", "..", "frontend", "dist", "index.html");
    win.loadFile(indexPath);
  }
}

app.whenReady().then(() => {
  startBackend();
  createWindow();
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
