const mongoose = require("mongoose");
const Product = require("../models/Product");

class ProductRepository {
  async create(payload) {
    const product = new Product(payload);
    return product.save();
  }

  async findById(id) {
    if (!mongoose.Types.ObjectId.isValid(id)) return null;
    return Product.findById(id).lean({ virtuals: true });
  }

  async findPaginated({ page = 1, limit = 10, filter = {}, sort = { createdAt: -1 } } = {}) {
    page = Math.max(1, Number(page));
    limit = Math.min(100, Math.max(1, Number(limit)));
    const skip = (page - 1) * limit;

    const [items, total] = await Promise.all([
      Product.find(filter).sort(sort).skip(skip).limit(limit).lean({ virtuals: true }),
      Product.countDocuments(filter),
    ]);

    return {
      items,
      meta: { page, limit, total, totalPages: Math.ceil(total / limit), strategy: "skip_limit" },
    };
  }

  async findPaginatedCursor({ limit = 10, filter = {}, cursor = null, sortDirection = "desc" } = {}) {
    limit = Math.min(100, Math.max(1, Number(limit)));
    const dir = sortDirection === "asc" ? 1 : -1;

    const queryFilter = { ...filter };

    if (cursor) {
      const [createdAtIso, id] = cursor.split("_");
      const createdAt = new Date(createdAtIso);

      queryFilter.$or =
        dir === -1
          ? [{ createdAt: { $lt: createdAt } }, { createdAt, _id: { $lt: id } }]
          : [{ createdAt: { $gt: createdAt } }, { createdAt, _id: { $gt: id } }];
    }

    const items = await Product.find(queryFilter)
      .sort({ createdAt: dir, _id: dir })
      .limit(limit)
      .lean({ virtuals: true });

    const last = items[items.length - 1];
    const nextCursor = last ? `${new Date(last.createdAt).toISOString()}_${last._id}` : null;

    return { items, meta: { limit, nextCursor, strategy: "cursor", sortDirection } };
  }

  async update(id, updates = {}) {
    if (!mongoose.Types.ObjectId.isValid(id)) return null;

    return Product.findByIdAndUpdate(id, { $set: updates }, { new: true, runValidators: true }).lean({
      virtuals: true,
    });
  }

  async delete(id) {
    if (!mongoose.Types.ObjectId.isValid(id)) return null;
    return Product.findByIdAndDelete(id).lean({ virtuals: true });
  }
}

module.exports = new ProductRepository();
