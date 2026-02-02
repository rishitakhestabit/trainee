// src/loaders/app.js
const express = require("express");

const loadDB = require("./db.js");
const logger = require("../utils/logger.js");

const securityMiddleware = require("../middlewares/security");
const { errorMiddleware } = require("../middlewares/error.middleware");
const requestLogger = require("../middlewares/requestLogger");
const setupSwagger = require("../utils/swagger");

const usersRoutes = require("../routes/users.routes.js");
const healthRoutes = require("../routes/health.routes.js");
const productsRoutes = require("../routes/products.routes.js");
const { tracingMiddleware } = require("../utils/tracing");
// Ensure models are registered
require("../models/User.js");
require("../models/Product.js");

async function createApp() {
  const app = express();

  //Security + parsing + limits (helmet/cors/rate-limit/sanitize/xss/hpp/json limit)
  securityMiddleware(app);
  logger.info("Security middleware loaded");

  // Database
  await loadDB();
  logger.info("DB connected");

  // Routes
  app.use("/api", healthRoutes);
  app.use("/api/users", usersRoutes);
  app.use("/api/products", productsRoutes);
  logger.info("Routes mounted: /api, /api/users, /api/products");
  app.use(requestLogger);
  setupSwagger(app);

  // Error handler last
  app.use(errorMiddleware);
  

  app.use(tracingMiddleware);
  logger.info("Tracing middleware loaded");


  return app;
}

module.exports = createApp;
