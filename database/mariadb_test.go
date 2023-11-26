package database

import (
	"log"
	"os"
	"testing"

	_ "github.com/go-sql-driver/mysql"
	"github.com/stretchr/testify/assert"
)

// var testDB *MockDB // Assuming MockDB is your mock database type

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
	// testDB = &MockDB{}
	StartDatabase()
}

func tearDown() {
	// Cleanup resources, close connections, etc.
	CloseDatabase()
}

func TestGetAllEntriesFromTable(t *testing.T) {

	rows, err := GetAllEntriesFromTable("meditation_sessions")
	if err != nil {
		// Handle the error, don't use 'rows' in this case
		log.Fatal(err)
	}

	// Use 'rows' here since the error is nil
	defer rows.Close()
	// Process the result set...

	assert.Nil(t, err)     // Assuming your HandleAllMeditations returns an error
	assert.NotNil(t, rows) // Assuming your HandleAllMeditations returns an error
}

func TestGetAllMeditationSessions(t *testing.T) {
	meditationSessions, err := GetAllMeditationSessions()
	if err != nil {
		// Handle the error, don't use 'rows' in this case
		log.Fatal(err)
	}

	// Use 'rows' here since the error is nil
	// defer meditationSessions.Close()

	assert.Nil(t, err)                   // Assuming your HandleAllMeditations returns an error
	assert.NotNil(t, meditationSessions) // Assuming your HandleAllMeditations returns an error

}
