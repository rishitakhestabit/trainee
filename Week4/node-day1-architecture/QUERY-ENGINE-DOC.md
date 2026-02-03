# QUERY-ENGINE-DOC.md

## Day 3 – High Performance REST API & Advanced Query Engine

On Day 3, I focused only on building a powerful Product API with an advanced query engine. My main objective was to make the API capable of handling real-world product listing scenarios such as searching, filtering, sorting, pagination, soft delete, and structured error handling.

Everything I implemented on this day is related specifically to the Product API and its query.

---

## What I Implemented on Day 3

- I implemented Controller -> Service -> Repository architecture for Product API.
- I created a dynamic query engine for product listing.
- I added search, filtering, sorting, and pagination.
- I implemented soft delete using a timestamp.
- I added centralized and typed error handling.
- I ensured consistent API response format.

---

## Controller - Service - Repository Flow

I structured my Product API into three layers:

### Controller Layer
- I receive HTTP requests.
- I pass request data to the service layer.
- I return formatted responses.
- I forward errors to error middleware.

### Service Layer
- I build dynamic query logic.
- I validate query parameters.
- I apply search, filters, sorting, and pagination.
- I call repository functions.

### Repository Layer
- I interact directly with MongoDB using Mongoose.
- I execute database queries.
- I return raw data back to service.

This separation makes my code easier to maintain and scale.


GET /api/products


- I return a list of products.
- I return pagination metadata.


## Search Implementation

GET /api/products?search=phone


What I did:

- I created case-insensitive regular expression search.
- I used MongoDB `$or` condition.
- I searched across multiple fields.

Fields I search in title, description, brand, category  

If the keyword matches any field, I return that product.

---

## Price Filtering



GET /api/products?minPrice=100&maxPrice=500


What I did:

- If minPrice exists -> price >= minPrice
- If maxPrice exists -> price <= maxPrice
- If both exist → price must be between them

Validation I added:

- minPrice must be >= 0  
- maxPrice must be >= 0  
- minPrice cannot be greater than maxPrice  

---

## Tags Filtering



GET /api/products?tags=apple,samsung


What I did:

- I split tags using comma.
- I used MongoDB `$in` operator.
- If product contains any of the tags, I return it.

---

## Sorting



GET /api/products?sort=price:asc
GET /api/products?sort=price:desc


What I did:

- I accept format: field:direction
- Direction can be asc or desc
- Default sorting is by createdAt descending

---

## Pagination



GET /api/products?page=1&limit=10


What I did:

- Default page = 1
- Default limit = 10
- Maximum limit = 100
- I calculate skip as (page - 1) * limit

---

## Soft Delete



DELETE /api/products/:id


What I did:

- I do not remove product from database.
- I set deletedAt = current timestamp.
- Product stays in database.

---

## Excluding Deleted Products (Default)



GET /api/products


What I did:

- I return only products where deletedAt is null.

---

## Including Deleted Products



GET /api/products?includeDeleted=true


What I did:

- I return both deleted and active products.

---

## Get Product By ID



GET /api/products/:id


What I did:

- I fetch product by id.
- If product is not found, I throw Product Not Found error.

---

## Centralized Error Handling

What I did:

- I created custom error classes.
- I attach error codes to errors.
- I created a global error middleware.
- All errors are returned in a single format.

---

## Global Error Response Format

```json
{
  "success": false,
  "message": "Error message",
  "code": "ERROR_CODE",
  "timestamp": "ISO_TIMESTAMP",
  "path": "/api/products"
}
