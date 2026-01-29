const express = require("express");
const { healthCheck } = require("../controllers/health.controller.js");

const router = express.Router();

router.get("/health", healthCheck);

module.exports = router;
