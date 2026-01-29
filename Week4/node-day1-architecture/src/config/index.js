const dotenv = require("dotenv");
const path = require("path");

const env = process.env.NODE_ENV || "local";

dotenv.config({
  path: path.resolve(process.cwd(), `.env.${env}`),
});

module.exports = {
  env,
  port: Number(process.env.PORT) || 3000,
  dbUrl: process.env.DB_URL,
};
