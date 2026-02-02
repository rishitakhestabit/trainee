// src/controllers/product.controller.js
const productService = require("../services/product.service");

// small wrapper to avoid repeating try/catch in every controller
const asyncHandler = (fn) => (req, res, next) =>
  Promise.resolve(fn(req, res, next)).catch(next);

const listProducts = asyncHandler(async (req, res) => {
  const result = await productService.list(req.query);

  return res.status(200).json({
    success: true,
    data: result.items,
    meta: result.meta,
    path: req.originalUrl,
  });
});

const getProductById = asyncHandler(async (req, res) => {
  const product = await productService.getById(req.params.id, req.query);

  return res.status(200).json({
    success: true,
    data: product,
    path: req.originalUrl,
  });
});

const createProduct = asyncHandler(async (req, res) => {
  const created = await productService.create(req.body);

  return res.status(201).json({
    success: true,
    data: created,
    path: req.originalUrl,
  });
});

const updateProduct = asyncHandler(async (req, res) => {
  const updated = await productService.update(req.params.id, req.body);

  return res.status(200).json({
    success: true,
    data: updated,
    path: req.originalUrl,
  });
});

// Soft delete: marks deletedAt
const softDeleteProduct = asyncHandler(async (req, res) => {
  const deleted = await productService.softDelete(req.params.id);

  return res.status(200).json({
    success: true,
    data: deleted,
    path: req.originalUrl,
  });
});

module.exports = {
  listProducts,
  getProductById,
  createProduct,
  updateProduct,
  softDeleteProduct,
};
