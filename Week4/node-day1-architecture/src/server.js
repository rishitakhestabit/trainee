import config from "./config/index.js"
import createApp from "./loaders/app.js"
import logger from "./utils/logger.js"

async function startServer() {
  const app = await createApp()

  app.listen(config.port, () => {
    logger.info(`Server started on port ${config.port}`)
  })
}

startServer()
