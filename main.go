package main

import (
	"fmt"
	"os"

	"github.com/gofiber/fiber/v2"
	"github.com/gofiber/fiber/v2/middleware/logger"
	"github.com/gofiber/fiber/v2/middleware/recover"
	"htw-berlin.de/meditation/config"
	"htw-berlin.de/meditation/router"
)

func main() {
	fmt.Println("Hello, World!")

	// load env
	err := config.LoadENV()
	if err != nil {
		// return err
		return
	}

	// create app
	app := fiber.New()

	// attach middleware
	app.Use(recover.New())
	app.Use(logger.New())

	// setup routes
	router.SetupRoutes(app)

	// get the port and start
	port := os.Getenv("PORT")
	app.Listen(":" + port)

}
