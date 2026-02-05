const express = require("express");
const mongoose = require("mongoose");
const cors = require("cors");

const app = express();
app.use(cors());
app.use(express.json());

const MONGO_URI = process.env.MONGO_URI;

async function connectDB() {
  if (!MONGO_URI) throw new Error("MONGO_URI is missing");
  await mongoose.connect(MONGO_URI);
  console.log(" MongoDB connected");
}

app.get("/health", async (req, res) => {
  const state = mongoose.connection.readyState; // 0=disconnected,1=connected,2=connecting,3=disconnecting
  res.json({
    ok: true,
    mongoReadyState: state,
  });
});

app.get("/api/hello", (req, res) => {
  res.json({ message: "Hello from Node server!" });
});

const PORT = process.env.PORT || 5000;

connectDB()
  .then(() => {
    app.listen(PORT, () => console.log(` Server running on port ${PORT}`));
  })
  .catch((err) => {
    console.error(" DB connection failed:", err.message);
    process.exit(1);
  });
