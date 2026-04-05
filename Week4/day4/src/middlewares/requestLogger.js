// src/middlewares/requestLogger.js
const logger = require("../utils/logger");

module.exports = (req, res, next) => {
  const start = Date.now();

  res.on("finish", () => {
    const ms = Date.now() - start;

    logger.info(
      {
        method: req.method,
        path: req.originalUrl,
        status: res.statusCode,
        ms,
      },
      "request"
    );
  });

  next();
};
