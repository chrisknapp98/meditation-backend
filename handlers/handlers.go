package handlers

import (
	"github.com/gofiber/fiber/v2"
)

func HandleAllMeditations(c *fiber.Ctx) error {
	return c.Status(200).JSON(fiber.Map{"response": "Hello World!"})
}
