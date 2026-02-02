// src/routes/users.routes.js
const router = require("express").Router();

const validate = require("../middlewares/validate");
const { createUserSchema } = require("../validators/user.schema");

const { usersController } = require("../controllers/users.controller.js");

router.get("/", usersController.list);
router.post("/", validate({ body: createUserSchema }), usersController.create);

module.exports = router;
