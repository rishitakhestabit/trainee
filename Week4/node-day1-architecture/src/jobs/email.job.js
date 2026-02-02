// src/jobs/email.job.js
const { Queue, Worker } = require("bullmq");
const IORedis = require("ioredis");
const logger = require("../utils/logger");

const useRedis = (process.env.USE_REDIS_QUEUE || "true") === "true";
const redisUrl = process.env.REDIS_URL || "redis://127.0.0.1:6379";

// In-memory fallback queue (simple)
const inMemory = {
  add: async (name, data) => {
    logger.info({ job: name, data }, "In-memory job queued");
    setTimeout(() => {
      logger.info({ job: name, data }, "In-memory job processed");
    }, 500);
    return { id: `mem-${Date.now()}` };
  },
};

// Real BullMQ queue + worker
let emailQueue = null;

function getQueue() {
  if (!useRedis) return inMemory;
  if (emailQueue) return emailQueue;

  const connection = new IORedis(redisUrl, {
    maxRetriesPerRequest: null,
  });

  emailQueue = new Queue("emailQueue", { connection });
  return emailQueue;
}

/**
 * Enqueue an email job
 */
async function enqueueEmailJob(payload) {
  const q = getQueue();

  // In-memory fallback
  if (q === inMemory) {
    return q.add("sendEmail", payload);
  }

  // BullMQ job with retry + exponential backoff
  return q.add("sendEmail", payload, {
    attempts: 5,
    backoff: {
      type: "exponential",
      delay: 2000, // 2s base delay
    },
    removeOnComplete: 100,
    removeOnFail: 100,
  });
}

/**
 * Start worker (call from server startup)
 * Worker runs in same process for training.
 * In production, run as separate process using PM2 (see prod/ecosystem.config.js)
 */
function startEmailWorker() {
  if (!useRedis) {
    logger.warn("USE_REDIS_QUEUE=false, worker not started (in-memory mode).");
    return null;
  }

  const connection = new IORedis(redisUrl, {
    maxRetriesPerRequest: null,
  });

  const worker = new Worker(
    "emailQueue",
    async (job) => {
      logger.info(
        { jobId: job.id, name: job.name, payload: job.data },
        "Email worker picked job"
      );

      // Simulate sending email / report generation
      // Replace with real provider later
      await new Promise((r) => setTimeout(r, 500));

      logger.info({ jobId: job.id }, "Email job completed");
      return { delivered: true };
    },
    { connection }
  );

  worker.on("failed", (job, err) => {
    logger.error(
      { jobId: job?.id, name: job?.name, err: err?.message },
      "Email job failed"
    );
  });

  worker.on("completed", (job) => {
    logger.info({ jobId: job.id }, "Email job success event");
  });

  logger.info("Email worker started");
  return worker;
}

module.exports = {
  enqueueEmailJob,
  startEmailWorker,
};
