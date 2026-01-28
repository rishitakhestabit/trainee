import mongoose from "mongoose"
import config from "../config/index.js"
import logger from "../utils/logger.js"

export default async function loadDB() {
  try {
    await mongoose.connect(config.dbUrl)
    logger.info("Database connected")
  } catch (err) {
    logger.error("Database connection failed")
    throw err
  }
}
