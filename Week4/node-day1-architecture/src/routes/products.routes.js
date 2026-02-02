// src/routes/products.routes.js
const router = require("express").Router();

const validate = require("../middlewares/validate");
const {
  createProductSchema,
  updateProductSchema,
  productQuerySchema,
} = require("../validators/product.schema");

const productController = require("../controllers/product.controller.js");

// List + filters
router.get(
  "/",
  validate({ query: productQuerySchema }),
  productController.listProducts
);

// Get by id
router.get("/:id", productController.getProductById);

// Create
router.post(
  "/",
  validate({ body: createProductSchema }),
  productController.createProduct
);

// Update
router.patch(
  "/:id",
  validate({ body: updateProductSchema }),
  productController.updateProduct
);

// Soft delete
router.delete("/:id", productController.softDeleteProduct);

module.exports = router;
