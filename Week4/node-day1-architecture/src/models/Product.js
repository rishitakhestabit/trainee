const mongoose = require("mongoose");

const { Schema } = mongoose;

/* Embedded review schema */
const reviewSchema = new Schema(
  {
    userId: { type: Schema.Types.ObjectId, ref: "User", required: true },
    rating: { type: Number, required: true, min: 1, max: 5 },
    comment: { type: String, trim: true },
  },
  { _id: false, timestamps: true }
);

/* Product Schema */
const productSchema = new Schema(
  {
    title: {
      type: String,
      required: true,
      trim: true,
      minlength: 2,
    },

    description: {
      type: String,
      trim: true,
      default: "",
    },

    price: {
      type: Number,
      required: true,
      min: 0,
    },

    status: {
      type: String,
      enum: ["draft", "active", "archived"],
      default: "draft",
      index: true,
    },

    category: {
      type: String,
      default: "general",
      lowercase: true,
    },

    // referenced user
    seller: {
      type: Schema.Types.ObjectId,
      ref: "User",
      required: true,
    },

    // embedded reviews
    reviews: {
      type: [reviewSchema],
      default: [],
    },

    // sparse + unique
    sku: {
      type: String,
      unique: true,
      sparse: true,
    },

    // TTL example
    expiresAt: {
      type: Date,
      default: null,
    },
  },
  {
    timestamps: true,
    toJSON: { virtuals: true },
    toObject: { virtuals: true },
  }
);

/* Virtual: average rating */
productSchema.virtual("averageRating").get(function () {
  if (!this.reviews.length) return 0;
  const sum = this.reviews.reduce((a, r) => a + r.rating, 0);
  return sum / this.reviews.length;
});

/* Compound index */
productSchema.index({ status: 1, createdAt: -1 });

/* TTL index */
productSchema.index({ expiresAt: 1 }, { expireAfterSeconds: 0 });

module.exports =
  mongoose.models.Product || mongoose.model("Product", productSchema);
