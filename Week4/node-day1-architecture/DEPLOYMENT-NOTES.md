# DEPLOYMENT NOTES — Day 5
Capstone Job Queues • Logging • Request Tracing • API Documentation

---

## 1. Overview

Day 5 of this Node.js backend training project focused on transforming an existing REST API into a **production-oriented backend system**. Before Day 5, the application primarily handled synchronous HTTP requests and returned responses directly from controllers. While this worked for basic CRUD operations, it did not reflect real-world backend systems where:

- Heavy or slow tasks should run in the background
- Logs must be structured and persisted
- Requests should be traceable across the system
- APIs must be documented for consumers
- Deployment configuration should be prepared

On this day, I implemented background job queues, structured logging, request tracing using correlation IDs, Swagger-based API documentation, and production-ready configuration files.

---

## 2. High-Level Architecture

The system now follows this flow:

1. Client sends HTTP request
2. Request passes through security middleware
3. Request tracing middleware attaches `X-Request-ID`
4. Request logger records metadata
5. Controller executes business logic
6. Optional background job is enqueued
7. Worker processes job asynchronously
8. Logs are written to disk
9. Response is returned to client

This separation ensures fast API responses, better observability, and scalability.

---

## 3. Background Job Queue Implementation

### Purpose

Some tasks (such as email notifications or report generation) should not block API responses. These tasks are executed asynchronously using a queue.

### Implementation

**File created:** `src/jobs/email.job.js`

**Design:**
- Uses **BullMQ** when Redis is enabled
- Uses **in-memory fallback queue** when Redis is not available
- Supports retries and exponential backoff
- Contains both producer and worker logic

**Main functions:**
- `enqueueEmailJob(payload)` → Adds job to queue
- `startEmailWorker()` → Starts worker that processes jobs

**Architecture decision:**
- In-memory fallback allows development without Redis
- Same interface for both queues keeps code simple

### Verification

Triggered background job using curl:
```bash
curl -i -X POST http://localhost:5000/api/users/notify
```

**Response:**
```
HTTP/1.1 202 Accepted
```

**Screenshot:**

![curlnotify](ss/day5ss/curlnotify.png)

Worker logs visible in terminal showing:
- Job picked
- Job processed
- Job completed

---

## 4. Structured Logging System

### Purpose

Console logs are not sufficient in production. Logs must be:
- Structured (JSON-like)
- Persisted to files
- Separated by severity

### Implementation

**File created:** `src/utils/logger.js`

**Logger interface:**
```js
logger.info(obj, msg)
logger.warn(obj, msg)
logger.error(obj, msg)
```

**Features:**
- Uses **Pino** for performance
- Writes to `logs/app.log`
- Pretty-prints in development
- JSON format in production

### Verification

- Starting server writes startup logs
- Hitting APIs writes request logs
- Worker logs appear when job runs

**Screenshot:**

![202accept](ss/day5ss/202accept.png)

---

## 5. Request Logging Middleware

### Purpose

Every request should record:
- HTTP method
- URL path
- Status code
- Response time

### Implementation

**File created:** `src/middlewares/requestLogger.js`

**Middleware behavior:**
- Records start time
- On response finish, logs metadata
- Mounted inside app loader

### Verification

Requests written into `logs/app.log` file.

**Screenshot:**

![swagger](ss/day5ss/swagger.png)

---

## 6. Request Tracing (Correlation ID)

### Purpose

In real systems, a single request may generate many logs. All logs should share a unique ID.

### Implementation

**File created:** `src/utils/tracing.js`

**Behavior:**
- If client sends `X-Request-ID`, reuse it
- Else generate UUID
- Attach to:
  - `req.requestId`
  - Response header `X-Request-ID`
  - All logs include this ID

### Verification

Swagger / curl responses show:
```
X-Request-ID: <uuid>
```

---

## 7. Swagger API Documentation

### Purpose

Provide interactive, self-hosted API documentation.

### Implementation

**File created:** `src/utils/swagger.js`

**Uses:**
- `swagger-jsdoc`
- Reads OpenAPI JSDoc blocks from route files
- Serves UI at: `http://localhost:5000/docs`

**Routes documented:**
- Products
- Users
- Health

### Verification

Swagger UI loads and displays endpoints:

**Products section expanded:**

![curlnotify](ss/day5ss/curlnotify.png)

**Users section visible:**

![202accept](ss/day5ss/202accept.png)

---

## 8. Route-Level OpenAPI Annotations

Inside route files such as: `src/routes/products.routes.js`

Each endpoint has OpenAPI comment blocks:
- Summary
- Tags
- Parameters
- Request body schema
- Responses

This keeps documentation close to implementation.

---

## 9. Production Folder

**Folder created:** `prod/`
```
└── ecosystem.config.js
```

**Purpose:** PM2 configuration for production process management

**Supports:**
- App name
- Script path
- Instances
- Restart policy
- Environment variables

**This allows:**
```bash
pm2 start prod/ecosystem.config.js
```

---

## 10. Environment Template

**File created:** `.env.example`

**Contains:**
```env
PORT=
MONGO_URI=
REDIS_URL=
USE_REDIS_QUEUE=
NODE_ENV=
```

**Purpose:**
- Documents required environment variables
- Prevents secrets from being committed

---

## 11. Application Loader Integration

**File updated:** `src/loaders/app.js`

**Order of setup:**
1. Security middleware
2. Database connection
3. Routes
4. Request logger
5. Swagger
6. Error middleware
7. Tracing middleware

This ensures tracing and logging occur for all requests.

---

