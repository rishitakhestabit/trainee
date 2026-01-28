import dotenv from "dotenv"
import path from "path"

const env = process.env.NODE_ENV || "local"

dotenv.config({
  path: path.resolve(process.cwd(), `.env.${env}`)
})

export default {
  env,
  port: process.env.PORT,
  dbUrl: process.env.DB_URL
}
