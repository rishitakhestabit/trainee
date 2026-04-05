// src/middlewares/error.middleware.js

class AppError extends Error {
  constructor(message, code = "APP_ERROR", status = 500, details = undefined) {
    super(message);
    this.name = this.constructor.name;
    this.code = code;
    this.status = status;
    this.details = details;
  }
}

class BadRequestError extends AppError {
  constructor(message = "Bad Request", code = "BAD_REQUEST", details) {
    super(message, code, 400, details);
  }
}

class NotFoundError extends AppError {
  constructor(message = "Not Found", code = "NOT_FOUND", details) {
    super(message, code, 404, details);
  }
}

class ConflictError extends AppError {
  constructor(message = "Conflict", code = "CONFLICT", details) {
    super(message, code, 409, details);
  }
}

// Centralized error handler
function errorMiddleware(err, req, res, next) {
  const status = err.status && Number.isInteger(err.status) ? err.status : 500;
  const code = err.code || (status === 500 ? "INTERNAL_SERVER_ERROR" : "UNKNOWN_ERROR");
  const message = err.message || "Something went wrong";

  // optional: log stack only for 500
  // console.error(err);

  return res.status(status).json({
    success: false,
    message,
    code,
    timestamp: new Date().toISOString(),
    path: req.originalUrl,
    // uncomment if you want: (be careful in production)
    // details: err.details,
  });
}

module.exports = {
  AppError,
  BadRequestError,
  NotFoundError,
  ConflictError,
  errorMiddleware,
};
