// src/routes/users.routes.js
const router = require("express").Router();

const validate = require("../middlewares/validate");
const { createUserSchema } = require("../validators/user.schema");

const { usersController } = require("../controllers/users.controller.js");

router.get("/", usersController.list);
router.post("/", validate({ body: createUserSchema }), usersController.create);

const { enqueueEmailJob } = require("../jobs/email.job");
router.post("/notify", async (req, res, next) => {
  try {
    const job = await enqueueEmailJob({
      to: "demo@example.com",
      subject: "Welcome",
      message: "Background email job test",
    });

    res.status(202).json({
      success: true,
      message: "Email job queued",
      jobId: job.id,
    });
  } catch (e) {
    next(e);
  }
});


module.exports = router;
