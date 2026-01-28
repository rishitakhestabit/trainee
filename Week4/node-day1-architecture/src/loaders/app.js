import express from "express"
import loadDB from "./db.js"
import logger from "../utils/logger.js"
import usersRoutes from "../routes/users.routes.js"
import healthRoutes from "../routes/health.routes.js"



export default async function createApp() {
  const app = express()

  // Middlewares
  app.use(express.json())
  logger.info("Middlewares loaded")

  // Database
  await loadDB()

  // Routes
  app.use("/api", healthRoutes)
  app.use("/api/users", usersRoutes)
  logger.info("Routes mounted: 3 endpoints")



  return app
}
