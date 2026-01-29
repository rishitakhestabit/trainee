const express = require("express");
const loadDB = require("./db.js");
const logger = require("../utils/logger.js");

const usersRoutes = require("../routes/users.routes.js");
const healthRoutes = require("../routes/health.routes.js");

require("../models/User.js");
require("../models/Product.js");

async function createApp() {
  const app = express();

  // Middlewares
  app.use(express.json());
  logger.info("Middlewares loaded");

  // Database
  await loadDB();

  // Routes
  app.use("/api", healthRoutes);
  app.use("/api/users", usersRoutes);
  logger.info("Routes mounted: 3 endpoints");

  return app;
}

module.exports = createApp;
