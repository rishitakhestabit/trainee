
# SECURITY-REPORT.md  
DAY 4 — Security, Validation, Rate Limiting & Hardening

---

## Introduction

On Day 4 of this project, the objective was to secure and harden the backend API by introducing proper validation, sanitization, and protection against common web vulnerabilities.

The focus areas included:

- Securing HTTP headers  
- Validating incoming requests  
- Preventing malformed and malicious inputs  
- Adding rate limiting  
- Applying payload size limits  
- Testing vulnerabilities manually  

All implementations were verified using terminal commands (curl) and browser testing.

---

## Security Middleware Implemented

The following global security mechanisms were added:

- Helmet for security headers  
- CORS policy  
- Rate limiting using express-rate-limit  
- Payload size limit (10kb)  
- HTTP Parameter Pollution (HPP) protection  
- Zod schema validation for User and Product  

These are configured inside:

src/middlewares/security.js
src/middlewares/validate.js
src/validators/


Security middleware is applied before all routes in:

src/loaders/app.js


---

## New Files Added

src/middlewares/security.js
src/middlewares/validate.js
src/validators/user.schema.js
src/validators/product.schema.js


---

## Baseline Check – Products API Working

Before performing security tests, the Products API was verified.

URL:

http://localhost:5000/api/products


Result:

- Products list returned successfully  
- Confirms server and database are working  

Status: Passed  

![Products](ss/day4ss/products.png)


---

## Helmet Security Headers

Helmet was used to add important HTTP security headers.

Command:

```bash
curl -I http://localhost:5000/api/products

Observed Headers:

    Content-Security-Policy

    X-Frame-Options: SAMEORIGIN

    X-Content-Type-Options: nosniff

    Strict-Transport-Security

    Referrer-Policy

Status: Passed

Screenshot:

![Helmet Headers](ss/day4ss/header1.png)

Product Validation (Zod)

Zod schema validation was applied to product creation.

Test: Invalid Product Types

curl -i -X POST http://localhost:5000/api/products \
-H "Content-Type: application/json" \
-d '{"title":123,"price":"abc"}'


Expected:

400 Bad Request

Validation error messages

Actual Result:

Validation failed

Errors returned for title and price

Status: Passed

Screenshot:

![Product Validation](ss/day4ss/validation.png)

User Validation (Zod)

Zod schema validation was applied to user creation.

Test: Empty Body

curl -i -X POST http://localhost:5000/api/users \
-H "Content-Type: application/json" \
-d '{}'


Expected:

400 Bad Request

Errors for missing name, email, password

Actual Result:

Validation failed

Errors returned for all required fields

Status: Passed

Screenshot:

![User Validation](ss/day4ss/validation.png)

NoSQL Injection Test

Attempted to inject MongoDB operator into email field.

Command:

curl -i -X POST http://localhost:5000/api/users \
-H "Content-Type: application/json" \
-d '{"name":"Test","email":{"$ne":""},"password":"123456"}'


Expected:

Should not allow object in email field

Actual Result:

Validation failed

Email must be string

![No-sql injection](ss/day4ss/nosql.png)

Status: Passed


Multiple requests were sent to exceed the rate limit.

for i in {1..120}; do curl -s -o /dev/null -w "%{http_code}\n" http://localhost:5000/api/products; done


Expected:

429 Too Many Requests

Actual Result:

After threshold, server returned 429

Status: Passed

![Rate-limiting](ss/day4ss/ratelimit.png)

Payload Size Limit

Tested sending request body larger than 10kb.

node -e "console.log(JSON.stringify({name:'A',email:'a@a.com',password:'123456',big:'x'.repeat(12000)}))" | \
curl -i -X POST http://localhost:5000/api/users \
-H "Content-Type: application/json" \
--data-binary @-


Expected:

413 Payload Too Large

Actual Result:

Request rejected

Status: Passed
![payload too large](toolarge.png)