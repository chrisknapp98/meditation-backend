package handlers

import (
	"github.com/gofiber/fiber/v2"
	"htw-berlin.de/meditation/database"
)

func HandleAllMeditations(c *fiber.Ctx) error {
	// fetch all meditations from database
	meditations, err := database.GetAllMeditationSessions()

	if err != nil {
		return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
			"message": "Error while fetching meditations from database",
			"error":   err.Error(),
		})
	}

	// return meditations
	return c.JSON(fiber.Map{
		"message": "Successfully fetched all meditations",
		"data":    meditations,
	})
}
