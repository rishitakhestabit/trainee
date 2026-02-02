// src/services/product.service.js
const productRepository = require("../repositories/product.repository");
const { BadRequestError, NotFoundError } = require("../middlewares/error.middleware");

// helpers
function toNumberOrUndefined(v) {
  if (v === undefined || v === null || v === "") return undefined;
  const n = Number(v);
  return Number.isFinite(n) ? n : undefined;
}

function parseTags(tags) {
  if (!tags) return [];
  if (Array.isArray(tags)) {
    return tags
      .flatMap((t) => String(t).split(","))
      .map((x) => x.trim())
      .filter(Boolean);
  }
  return String(tags)
    .split(",")
    .map((x) => x.trim())
    .filter(Boolean);
}

function parseSort(sortRaw) {
  // supports: sort=price:desc OR sort=price OR sort=price:asc
  if (!sortRaw) return { createdAt: -1 };

  const raw = String(sortRaw).trim();
  const [field, dir] = raw.split(":").map((x) => (x ? x.trim() : ""));
  if (!field) return { createdAt: -1 };

  const direction = (dir || "asc").toLowerCase() === "desc" ? -1 : 1;
  return { [field]: direction };
}

function buildQueryEngineFilters(q = {}) {
  const search = q.search ? String(q.search).trim() : "";
  const minPrice = toNumberOrUndefined(q.minPrice);
  const maxPrice = toNumberOrUndefined(q.maxPrice);
  const includeDeleted = String(q.includeDeleted || "false").toLowerCase() === "true";
  const tags = parseTags(q.tags);

  // pagination (page/limit)
  const page = Math.max(1, toNumberOrUndefined(q.page) || 1);
  const limit = Math.min(100, Math.max(1, toNumberOrUndefined(q.limit) || 10));

  // cursor pagination (optional)
  const cursor = q.cursor ? String(q.cursor).trim() : null;
  const sortDirection = String(q.sortDirection || "desc").toLowerCase() === "asc" ? "asc" : "desc";

  if (minPrice !== undefined && minPrice < 0) throw new BadRequestError("minPrice must be >= 0", "INVALID_QUERY");
  if (maxPrice !== undefined && maxPrice < 0) throw new BadRequestError("maxPrice must be >= 0", "INVALID_QUERY");
  if (minPrice !== undefined && maxPrice !== undefined && minPrice > maxPrice) {
    throw new BadRequestError("minPrice cannot be greater than maxPrice", "INVALID_QUERY");
  }

  const filter = {};

  // Price range
  if (minPrice !== undefined || maxPrice !== undefined) {
    filter.price = {};
    if (minPrice !== undefined) filter.price.$gte = minPrice;
    if (maxPrice !== undefined) filter.price.$lte = maxPrice;
  }

  // Tags
  if (tags.length) {
    // assumes Product schema field: tags: [String]
    filter.tags = { $in: tags };
  }

  // Search (regex + OR)
  if (search) {
    const safe = search.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    const rx = new RegExp(safe, "i");

    // adjust fields according to your Product schema
    filter.$or = [{ title: rx }, { description: rx }, { brand: rx }, { category: rx }];
  }

  const sort = parseSort(q.sort);

  return {
    filter,
    sort,
    page,
    limit,
    includeDeleted,
    search,
    tags,
    minPrice,
    maxPrice,
    cursor,
    sortDirection,
  };
}

async function list(query) {
  const engine = buildQueryEngineFilters(query);

  // If cursor is present, use cursor pagination
  if (engine.cursor) {
    const res = await productRepository.findPaginatedCursor({
      limit: engine.limit,
      filter: engine.filter,
      cursor: engine.cursor,
      sortDirection: engine.sortDirection,
      includeDeleted: engine.includeDeleted,
    });

    return { items: res.items, meta: res.meta };
  }

  // Otherwise normal page/limit pagination
  const res = await productRepository.findPaginated({
    page: engine.page,
    limit: engine.limit,
    filter: engine.filter,
    sort: engine.sort,
    includeDeleted: engine.includeDeleted,
  });

  return { items: res.items, meta: res.meta };
}

async function getById(id, query) {
  const includeDeleted = String(query?.includeDeleted || "false").toLowerCase() === "true";

  const product = await productRepository.findById(id, { includeDeleted });
  if (!product) throw new NotFoundError("Product not found", "PRODUCT_NOT_FOUND");

  return product;
}

async function create(payload) {
  if (!payload || typeof payload !== "object") {
    throw new BadRequestError("Invalid body", "INVALID_BODY");
  }

  if (!payload.title) throw new BadRequestError("title is required", "VALIDATION_ERROR");
  if (payload.price === undefined) throw new BadRequestError("price is required", "VALIDATION_ERROR");

  return productRepository.create(payload);
}

async function update(id, payload) {
  const updated = await productRepository.update(id, payload);
  if (!updated) throw new NotFoundError("Product not found", "PRODUCT_NOT_FOUND");
  return updated;
}

// Soft delete: uses repository.delete() (which you changed to set deletedAt)
async function softDelete(id) {
  const deleted = await productRepository.delete(id);
  if (!deleted) throw new NotFoundError("Product not found", "PRODUCT_NOT_FOUND");
  return deleted;
}

module.exports = {
  list,
  getById,
  create,
  update,
  softDelete,
  buildQueryEngineFilters,
};
