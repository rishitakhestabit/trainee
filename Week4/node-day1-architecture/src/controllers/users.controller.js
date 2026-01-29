const { usersService } = require("../services/users.service.js");

const usersController = {
  list: async (req, res) => {
    const users = await usersService.list();
    res.json(users);
  },

  create: async (req, res) => {
    const user = await usersService.create(req.body);
    res.status(201).json(user);
  },
};

module.exports = { usersController };
