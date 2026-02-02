// src/seed.js
const path = require("path");
const mongoose = require("mongoose");

// Load same env file like your dev server
const envName = process.env.NODE_ENV || "dev";
const envPath = path.join(process.cwd(), `.env.${envName}`);

require("dotenv").config({ path: envPath });

const Product = require("./models/Product");
const User = require("./models/User");

async function seed() {
  console.log("NODE_ENV =", envName);
  console.log("Loading env from:", envPath);

  const uri = process.env.DB_URL;

  if (!uri) {
    console.error("DB_URL not found in", envPath);
    process.exit(1);
  }

  console.log("Connecting to:", uri);
  await mongoose.connect(uri);

  console.log("Mongo connected");
  console.log("DB name:", mongoose.connection.name);

  // Clear old data
  await Product.deleteMany({});
  await User.deleteMany({});
  console.log("Cleared users and products");

  // Create users
  const users = await User.create([
    {
      firstName: "Riya",
      lastName: "Sharma",
      email: "user1@test.com",
      password: "Password@123",
      status: "active",
    },
    {
      firstName: "Aman",
      lastName: "Verma",
      email: "user2@test.com",
      password: "Password@123",
      status: "active",
    },
    {
      firstName: "Neha",
      lastName: "Singh",
      email: "user3@test.com",
      password: "Password@123",
      status: "inactive",
    },
  ]);

  console.log("Inserted users:", users.length);
  users.forEach((u) => console.log(u._id.toString(), u.email));

  // Use first user as seller
  const sellerId = users[0]._id;

  // Create products
  const products = [
    {
      title: "iPhone 15",
      description: "Latest iPhone model",
      price: 1200,
      status: "active",
      category: "phone",
      brand: "Apple",
      tags: ["apple", "ios", "phone"],
      seller: sellerId,
      sku: "IPHONE-15-001",
      deletedAt: null,
    },
    {
      title: "Galaxy S24",
      description: "Samsung flagship phone",
      price: 999,
      status: "active",
      category: "phone",
      brand: "Samsung",
      tags: ["samsung", "android", "phone"],
      seller: sellerId,
      sku: "S24-001",
      deletedAt: null,
    },
  ];

  const insertedProducts = await Product.insertMany(products);
  console.log("Inserted products:", insertedProducts.length);
  insertedProducts.forEach((p) => console.log(p._id.toString(), p.title));

  await mongoose.disconnect();
  console.log("Done");
}

seed().catch((err) => {
  console.error("Seed failed:", err);
  process.exit(1);
});
