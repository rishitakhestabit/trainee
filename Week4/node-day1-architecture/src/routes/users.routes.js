const express = require("express");
const { usersController } = require("../controllers/users.controller.js");

const router = express.Router();

router.get("/", usersController.list);    // endpoint 2
router.post("/", usersController.create); // endpoint 3

module.exports = router;
