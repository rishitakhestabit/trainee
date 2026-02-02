// /validators/user.schema.js
const { z } = require("zod");

const createUserSchema = z.object({
  name: z.string().min(2, "name must be at least 2 chars").max(50),
  email: z.string().email("invalid email"),
  password: z
    .string()
    .min(6, "password must be at least 6 chars")
    .max(100),
  role: z.enum(["user", "admin"]).optional(),
});

const updateUserSchema = createUserSchema
  .partial()
  .refine((data) => Object.keys(data).length > 0, {
    message: "At least one field is required to update",
  });

module.exports = { createUserSchema, updateUserSchema };
