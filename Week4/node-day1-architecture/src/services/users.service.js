export const usersService = {
  list: async () => {
    return [{ id: "u1", name: "Demo User" }]
  },

  create: async (data) => {
    return { id: "u2", ...data }
  }
}
