// prod/ecosystem.config.js
module.exports = {
  apps: [
    {
      name: "api",
      script: "src/server.js",
      env: {
        NODE_ENV: "production",
        PORT: 5000,
      },
    },
    {
      name: "worker",
      script: "src/server.js",
      env: {
        NODE_ENV: "production",
        PORT: 5000,
        WORKER_ONLY: "true",
      },
    },
  ],
};
