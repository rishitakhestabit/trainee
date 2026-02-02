// /validators/product.schema.js
const { z } = require("zod");

const createProductSchema = z.object({
  title: z.string().min(2).max(120),
  description: z.string().min(5).max(2000).optional(),
  price: z.number().nonnegative("price must be >= 0"),
  category: z.string().min(2).max(60).optional(),
  tags: z.array(z.string().min(1).max(30)).optional(),
  stock: z.number().int().nonnegative().optional(),
});

const updateProductSchema = createProductSchema
  .partial()
  .refine((data) => Object.keys(data).length > 0, {
    message: "At least one field is required to update",
  });

/**
 * If you have filtering in GET /api/products:
 * /api/products?minPrice=100&maxPrice=500&tags=apple,samsung
 */
const productQuerySchema = z
  .object({
    search: z.string().trim().min(1).optional(),
    minPrice: z.coerce.number().nonnegative().optional(),
    maxPrice: z.coerce.number().nonnegative().optional(),
    tags: z.string().trim().min(1).optional(), // comma-separated
    sort: z.enum(["price_asc", "price_desc", "newest"]).optional(),
    page: z.coerce.number().int().min(1).optional(),
    limit: z.coerce.number().int().min(1).max(100).optional(),
  })
  .refine(
    (q) => !(q.minPrice != null && q.maxPrice != null && q.minPrice > q.maxPrice),
    { message: "minPrice cannot be greater than maxPrice" }
  );

module.exports = { createProductSchema, updateProductSchema, productQuerySchema };
