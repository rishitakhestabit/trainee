// src/utils/logger.js
const fs = require("node:fs");
const path = require("node:path");
const pino = require("pino");

const logsDir = path.join(process.cwd(), "logs");
if (!fs.existsSync(logsDir)) fs.mkdirSync(logsDir, { recursive: true });

const appStream = fs.createWriteStream(path.join(logsDir, "app.log"), { flags: "a" });
const errStream = fs.createWriteStream(path.join(logsDir, "error.log"), { flags: "a" });

const appLogger = pino(appStream);
const errLogger = pino(errStream);

module.exports = {
  info: (obj, msg) => appLogger.info(obj || {}, msg || ""),
  warn: (obj, msg) => appLogger.warn(obj || {}, msg || ""),
  error: (obj, msg) => errLogger.error(obj || {}, msg || ""),
};
