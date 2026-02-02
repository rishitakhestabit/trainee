const mongoose = require("mongoose");
const Product = require("../models/Product");

class ProductRepository {
  async create(payload) {
    const product = new Product({
      ...payload,
      deletedAt: payload?.deletedAt ?? null,
    });
    return product.save();
  }

  async findById(id, { includeDeleted = false } = {}) {
    if (!mongoose.Types.ObjectId.isValid(id)) return null;

    if (!includeDeleted) {
      return Product.findOne({ _id: id, deletedAt: null }).lean({ virtuals: true });
    }

    return Product.findById(id).lean({ virtuals: true });
  }

  async findPaginated({
    page = 1,
    limit = 10,
    filter = {},
    sort = { createdAt: -1 },
    includeDeleted = false,
  } = {}) {
    page = Math.max(1, Number(page));
    limit = Math.min(100, Math.max(1, Number(limit)));
    const skip = (page - 1) * limit;

    const queryFilter = includeDeleted ? { ...filter } : { ...filter, deletedAt: null };

    const [items, total] = await Promise.all([
      Product.find(queryFilter).sort(sort).skip(skip).limit(limit).lean({ virtuals: true }),
      Product.countDocuments(queryFilter),
    ]);

    return {
      items,
      meta: { page, limit, total, totalPages: Math.ceil(total / limit), strategy: "skip_limit" },
    };
  }

  async findPaginatedCursor({
    limit = 10,
    filter = {},
    cursor = null,
    sortDirection = "desc",
    includeDeleted = false,
  } = {}) {
    limit = Math.min(100, Math.max(1, Number(limit)));
    const dir = sortDirection === "asc" ? 1 : -1;

    const queryFilter = includeDeleted ? { ...filter } : { ...filter, deletedAt: null };

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

  async update(id, updates = {}, { includeDeleted = false } = {}) {
    if (!mongoose.Types.ObjectId.isValid(id)) return null;

    const filter = includeDeleted ? { _id: id } : { _id: id, deletedAt: null };

    return Product.findOneAndUpdate(filter, { $set: updates }, { new: true, runValidators: true }).lean({
      virtuals: true,
    });
  }

  // ✅ soft delete
  async delete(id) {
    if (!mongoose.Types.ObjectId.isValid(id)) return null;

    return Product.findOneAndUpdate(
      { _id: id, deletedAt: null },
      { $set: { deletedAt: new Date() } },
      { new: true }
    ).lean({ virtuals: true });
  }

  async restore(id) {
    if (!mongoose.Types.ObjectId.isValid(id)) return null;

    return Product.findOneAndUpdate(
      { _id: id, deletedAt: { $ne: null } },
      { $set: { deletedAt: null } },
      { new: true }
    ).lean({ virtuals: true });
  }

  async hardDelete(id) {
    if (!mongoose.Types.ObjectId.isValid(id)) return null;
    return Product.findByIdAndDelete(id).lean({ virtuals: true });
  }
}

module.exports = new ProductRepository();
