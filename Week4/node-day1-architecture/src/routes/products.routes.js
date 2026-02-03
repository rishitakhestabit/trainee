// src/routes/products.routes.js
const router = require("express").Router();

const validate = require("../middlewares/validate");
const {
  createProductSchema,
  updateProductSchema,
  productQuerySchema,
} = require("../validators/product.schema");

const productController = require("../controllers/product.controller.js");

/**
 * @openapi
 * tags:
 *   - name: Products
 *     description: Product management APIs
 */

/**
 * @openapi
 * /api/products:
 *   get:
 *     tags: [Products]
 *     summary: Get all products with filters
 *     parameters:
 *       - in: query
 *         name: search
 *         schema:
 *           type: string
 *       - in: query
 *         name: minPrice
 *         schema:
 *           type: number
 *       - in: query
 *         name: maxPrice
 *         schema:
 *           type: number
 *       - in: query
 *         name: sort
 *         schema:
 *           type: string
 *           enum: [price_asc, price_desc, newest]
 *     responses:
 *       200:
 *         description: Products list
 */
router.get(
  "/",
  validate({ query: productQuerySchema }),
  productController.listProducts
);

/**
 * @openapi
 * /api/products/{id}:
 *   get:
 *     tags: [Products]
 *     summary: Get product by id
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: string
 *     responses:
 *       200:
 *         description: Product found
 *       404:
 *         description: Product not found
 */
router.get("/:id", productController.getProductById);

/**
 * @openapi
 * /api/products:
 *   post:
 *     tags: [Products]
 *     summary: Create product
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               title:
 *                 type: string
 *                 example: Galaxy S24
 *               price:
 *                 type: number
 *                 example: 999
 *               description:
 *                 type: string
 *                 example: Samsung flagship phone
 *     responses:
 *       201:
 *         description: Product created
 */
router.post(
  "/",
  validate({ body: createProductSchema }),
  productController.createProduct
);

/**
 * @openapi
 * /api/products/{id}:
 *   patch:
 *     tags: [Products]
 *     summary: Update product
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: string
 *     requestBody:
 *       required: true
 *     responses:
 *       200:
 *         description: Product updated
 */
router.patch(
  "/:id",
  validate({ body: updateProductSchema }),
  productController.updateProduct
);

/**
 * @openapi
 * /api/products/{id}:
 *   delete:
 *     tags: [Products]
 *     summary: Soft delete product
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: string
 *     responses:
 *       200:
 *         description: Product deleted
 */
router.delete("/:id", productController.softDeleteProduct);

module.exports = router;
