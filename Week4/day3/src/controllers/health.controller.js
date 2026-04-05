function healthCheck(req, res) {
  res.json({ status: "OK" });
}

module.exports = { healthCheck };
