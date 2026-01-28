import { Router } from "express"
import { usersController } from "../controllers/users.controller.js"

const router = Router()

router.get("/", usersController.list)   // endpoint 2
router.post("/", usersController.create) // endpoint 3

export default router
