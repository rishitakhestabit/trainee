// src/middlewares/security.js
const helmet = require("helmet");
const cors = require("cors");
const rateLimit = require("express-rate-limit");
// const mongoSanitize = require("express-mongo-sanitize");
// const xssClean = require("xss-clean");
const hpp = require("hpp");

const securityMiddleware = (app) => {
  app.use(helmet());

  const allowedOrigin = process.env.CLIENT_ORIGIN || "*";
  app.use(
    cors({
      origin: allowedOrigin === "*" ? "*" : [allowedOrigin],
      credentials: allowedOrigin === "*" ? false : true,
      methods: ["GET", "POST", "PUT", "PATCH", "DELETE"],
      allowedHeaders: ["Content-Type", "Authorization"],
    })
  );

  // payload limits
  app.use(require("express").json({ limit: "10kb" }));
  app.use(require("express").urlencoded({ extended: true, limit: "10kb" }));

  // rate limit
  app.use(
    "/api",
    rateLimit({
      windowMs: 15 * 60 * 1000,
      max: 100,
      standardHeaders: true,
      legacyHeaders: false,
      message: { success: false, message: "Too many requests, please try again later." },
    })
  );
  app.use(hpp({ whitelist: ["tags"] }));

  app.disable("x-powered-by");
};

module.exports = securityMiddleware;
