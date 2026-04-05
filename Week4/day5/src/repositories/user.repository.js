const mongoose = require("mongoose");
const User = require("../models/User");

class UserRepository {
  async create(payload) {
    const user = new User(payload);
    return user.save();
  }

  async findById(id, { includePassword = false } = {}) {
    if (!mongoose.Types.ObjectId.isValid(id)) return null;

    let q = User.findById(id);
    if (includePassword) q = q.select("+password");

    return q.lean({ virtuals: true });
  }

  // Page-based (skip/limit)
  async findPaginated({ page = 1, limit = 10, filter = {}, sort = { createdAt: -1 } } = {}) {
    page = Math.max(1, Number(page));
    limit = Math.min(100, Math.max(1, Number(limit)));
    const skip = (page - 1) * limit;

    const [items, total] = await Promise.all([
      User.find(filter).sort(sort).skip(skip).limit(limit).lean({ virtuals: true }),
      User.countDocuments(filter),
    ]);

    return {
      items,
      meta: { page, limit, total, totalPages: Math.ceil(total / limit), strategy: "skip_limit" },
    };
  }

  // Cursor-based (best for large collections)
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

    const items = await User.find(queryFilter)
      .sort({ createdAt: dir, _id: dir })
      .limit(limit)
      .lean({ virtuals: true });

    const last = items[items.length - 1];
    const nextCursor = last ? `${new Date(last.createdAt).toISOString()}_${last._id}` : null;

    return { items, meta: { limit, nextCursor, strategy: "cursor", sortDirection } };
  }

  async update(id, updates = {}) {
    if (!mongoose.Types.ObjectId.isValid(id)) return null;

    // if password changes → use save() to trigger pre-save hashing
    if (updates.password) {
      const user = await User.findById(id).select("+password");
      if (!user) return null;
      Object.assign(user, updates);
      await user.save();
      return user.toObject({ virtuals: true });
    }

    return User.findByIdAndUpdate(id, { $set: updates }, { new: true, runValidators: true }).lean({
      virtuals: true,
    });
  }

  async delete(id) {
    if (!mongoose.Types.ObjectId.isValid(id)) return null;
    return User.findByIdAndDelete(id).lean({ virtuals: true });
  }
}

module.exports = new UserRepository();
