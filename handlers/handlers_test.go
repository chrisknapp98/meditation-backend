package handlers

import (
	"os"
	"testing"

	"htw-berlin.de/meditation/database"

	"github.com/gofiber/fiber/v2"
	"github.com/stretchr/testify/assert"
)

var testDB *database.MockDB // Assuming MockDB is your mock database type

func TestMain(m *testing.M) {
	// Setup
	setup()
	defer tearDown()

	// Run tests
	exitCode := m.Run()

	// Exit with the result of the test run
	os.Exit(exitCode)
}

func setup() {
	// Initialize resources, setup the environment, etc.
	testDB = &database.MockDB{}
	database.SetMockDBConnection(testDB)
}

func tearDown() {
	// Cleanup resources, close connections, etc.
	database.ResetMockDBConnection()
}

func TestHandleAllMeditations(t *testing.T) {
	// Mock the Fiber context
	c := new(fiber.Ctx)

	// Mock the database connection
	database.SetMockDBConnection(&database.MockDB{})

	// Call the function being tested
	err := HandleAllMeditations(c)

	// Assert the results
	assert.Nil(t, err)
}
