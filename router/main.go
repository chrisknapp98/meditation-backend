package router

import (
	"github.com/gofiber/fiber/v2"

	"htw-berlin.de/meditation/handlers"
)

func SetupRoutes(app *fiber.App) {
	app.Get("/", func(c *fiber.Ctx) error {
		return c.SendString("Hello World!")
	})
	meditations := app.Group("/meditations")
	meditations.Get("/", handlers.HandleAllMeditations)
}
