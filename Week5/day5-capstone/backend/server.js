const express = require("express");
const mongoose = require("mongoose");
const cors = require("cors");

const app = express();

app.use(cors());
app.use(express.json());

const PORT = process.env.PORT || 3000;
const MONGO_URI = process.env.MONGO_URI;

// Model
const NoteSchema = new mongoose.Schema(
  { text: { type: String, required: true } },
  { timestamps: true }
);
const Note = mongoose.model("Note", NoteSchema);

// Healthcheck (required for compose healthcheck)
app.get("/health", (req, res) => res.status(200).json({ ok: true }));

// Create note
app.post("/api/notes", async (req, res) => {
  try {
    const { text } = req.body;
    if (!text || !text.trim()) {
      return res.status(400).json({ error: "text is required" });
    }
    const note = await Note.create({ text: text.trim() });
    res.status(201).json(note);
  } catch (err) {
    res.status(500).json({ error: "server error" });
  }
});

// Get all notes
app.get("/api/notes", async (req, res) => {
  try {
    const notes = await Note.find().sort({ createdAt: -1 });
    res.json(notes);
  } catch (err) {
    res.status(500).json({ error: "server error" });
  }
});

// Connect DB then start server
mongoose
  .connect(MONGO_URI)
  .then(() => {
    console.log("MongoDB connected");
    app.listen(PORT, () => console.log(`Backend running on ${PORT}`));
  })
  .catch((err) => {
    console.error("Mongo connection error:", err.message);
    process.exit(1);
  });
