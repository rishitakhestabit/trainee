const router = require("express").Router();
const productController = require("../controllers/product.controller");

router.get("/", productController.listProducts);
router.get("/:id", productController.getProductById);
router.post("/", productController.createProduct);
router.put("/:id", productController.updateProduct);
router.delete("/:id", productController.softDeleteProduct);

module.exports = router;
