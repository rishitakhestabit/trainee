// import mongoose from "mongoose"
// import config from "../config/index.js"
// import logger from "../utils/logger.js"

// export default async function loadDB() {
//   try {
//     await mongoose.connect(config.dbUrl)
//     logger.info("Database connected")
//   } catch (err) {
//     logger.error("Database connection failed")
//     throw err
//   }
// }

const mongoose = require("mongoose");
const config = require("../config/index.js");

const loadDB = async () => {
  try {
    await mongoose.connect(config.dbUrl);
    console.log("MongoDB connected");
  } catch (err) {
    console.log("MongoDB connection error");
    console.error(err.message);
    process.exit(1);
  }
};

module.exports = loadDB;
