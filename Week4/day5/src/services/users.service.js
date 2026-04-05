const UserRepository = require("../repositories/user.repository.js");

const usersService = {
  async list() {
    return UserRepository.findPaginated({
      page: 1,
      limit: 20,
    });
  },

  async create(payload) {
    return UserRepository.create(payload);
  },
};

module.exports = { usersService };
