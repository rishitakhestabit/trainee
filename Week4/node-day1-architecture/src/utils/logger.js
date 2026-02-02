// src/utils/logger.js
const fs = require("node:fs");
const path = require("node:path");
const pino = require("pino");

// create logs folder if not exists
const logsDir = path.join(process.cwd(), "logs");
if (!fs.existsSync(logsDir)) fs.mkdirSync(logsDir, { recursive: true });

// write streams
const appStream = fs.createWriteStream(path.join(logsDir, "app.log"), { flags: "a" });
const errStream = fs.createWriteStream(path.join(logsDir, "error.log"), { flags: "a" });

// two loggers: info -> app.log, error -> error.log
const logger = {
  info: (obj, msg) => {
    if (typeof obj === "string") return pino(appStream).info(obj);
    return pino(appStream).info(obj || {}, msg || "");
  },
  warn: (obj, msg) => {
    if (typeof obj === "string") return pino(appStream).warn(obj);
    return pino(appStream).warn(obj || {}, msg || "");
  },
  error: (obj, msg) => {
    if (typeof obj === "string") return pino(errStream).error(obj);
    return pino(errStream).error(obj || {}, msg || "");
  },
};

module.exports = logger;
