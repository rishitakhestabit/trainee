// src/utils/tracing.js
const { AsyncLocalStorage } = require("node:async_hooks");
const { randomUUID } = require("node:crypto");

const als = new AsyncLocalStorage();

function getRequestId() {
  const store = als.getStore();
  return store?.requestId || "no-request-id";
}

/**
 * tracingMiddleware
 * - sets X-Request-ID
 * - stores requestId in AsyncLocalStorage
 * - makes it available in logs via getRequestId()
 */
function tracingMiddleware(req, res, next) {
  const incoming =
    req.headers["x-request-id"] ||
    req.headers["x-request-id".toLowerCase()] ||
    null;

  const requestId = incoming || randomUUID();

  // Set header so client also receives it
  res.setHeader("X-Request-ID", requestId);

  als.run({ requestId }, () => next());
}

module.exports = {
  tracingMiddleware,
  getRequestId,
};
