const express = require("express");
const os = require("os");

const app = express();
const PORT = process.env.PORT || 3000;

// health check
app.get("/health", (req, res) => {
  res.json({ ok: true });
});

// main api
app.get("/api", (req, res) => {
  res.json({
    message: "Hello from backend",
    hostname: os.hostname(),
    time: new Date().toISOString()
  });
});

app.listen(PORT, () => {
  console.log(`Backend running on port ${PORT}`);
});
