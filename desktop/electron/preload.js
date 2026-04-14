const { contextBridge } = require("electron");

contextBridge.exposeInMainWorld("__APP_CONFIG__", {
  apiBase: process.env.CVALGOVIS_API_BASE || "http://127.0.0.1:18000"
});
