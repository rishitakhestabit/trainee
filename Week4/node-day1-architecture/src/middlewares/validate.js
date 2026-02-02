// src/middlewares/validate.js
const { ZodError } = require("zod");

const validate = (schema = {}) => (req, res, next) => {
  try {
    req.validated = req.validated || {};

    if (schema.body) {
      const parsedBody = schema.body.parse(req.body);
      req.validated.body = parsedBody;
      req.body = parsedBody;
    }

    if (schema.params) {
      const parsedParams = schema.params.parse(req.params);
      req.validated.params = parsedParams;
      req.params = parsedParams;
    }

    if (schema.query) {
      const parsedQuery = schema.query.parse(req.query);
      req.validated.query = parsedQuery;
      // don't assign to req.query
    }

    return next();
  } catch (err) {
    //  Zod v3/v4 compatible formatting
    if (err instanceof ZodError || err?.name === "ZodError") {
      const issues = err.issues || err.errors || [];
      return res.status(400).json({
        success: false,
        message: "Validation failed",
        errors: issues.map((e) => ({
          path: Array.isArray(e.path) ? e.path.join(".") : String(e.path || ""),
          message: e.message,
        })),
      });
    }
    return next(err);
  }
};

module.exports = validate;
