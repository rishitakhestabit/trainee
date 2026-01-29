const config = require("./config/index.js");
const createApp = require("./loaders/app.js");
const logger = require("./utils/logger.js");


async function startServer() {
  const app = await createApp()

  app.listen(config.port, () => {
    logger.info(`Server started on port ${config.port}`)
  })
}

startServer()
