package database

import (
	"database/sql"
	"fmt"
	"log"
	"time"

	_ "github.com/go-sql-driver/mysql"
)

var databaseClient *sql.DB

// var dbName string

func StartDatabase() error {
	// dsn := "username:password@tcp(127.0.0.1:3306)/meditation_db"
	dsn := "middleware:supersafepassword@tcp(127.0.0.1:3306)/meditation_db"

	// Open a connection to the database
	db, err := sql.Open("mysql", dsn)
	if err != nil {
		log.Fatal(err)
	}

	// check if connection is established
	err = db.Ping()
	if err != nil {
		log.Fatal(err)
	}
	fmt.Println("Successfully connected to database!")

	// Assign the opened connection to the global variable
	databaseClient = db

	// create table
	_, err = db.Exec(`
		CREATE TABLE IF NOT EXISTS meditation_sessions (
			id INT AUTO_INCREMENT PRIMARY KEY, 
			title VARCHAR(255) NOT NULL, 
			duration INT NOT NULL, 
			created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
		)
	`)

	if err != nil {
		return err
	}

	return nil
}

func CloseDatabase() {
	// disconnect from database mariadb (mysql)
	err := databaseClient.Close()
	if err != nil {
		panic(err)
	}
}

func GetDatabase(name string) *sql.DB {
	return databaseClient
}

func GetAllEntriesFromTable(tableName string) (*sql.Rows, error) {
	// get all entries from table
	rows, err := databaseClient.Query("SELECT * FROM " + tableName)
	if err != nil {
		return nil, err
	}
	return rows, nil
}

func GetAllMeditationSessions() ([]MeditationSession, error) {
	// get all entries from the table
	rows, err := databaseClient.Query("SELECT * FROM meditation_sessions")
	if err != nil {
		return nil, err
	}
	// defer rows.Close()

	// create an array to store the results
	var meditationSessions []MeditationSession

	// iterate over all rows
	for rows.Next() {
		// create a new MeditationSession instance
		var meditationSession MeditationSession

		// Scan the values from the row into the struct fields
		err := rows.Scan(
			&meditationSession.ID,
			&meditationSession.Title,
			&meditationSession.Duration,
			&meditationSession.CreatedAtString, // Use a string for scanning
		)
		if err != nil {
			return nil, err
		}

		// Parse the string into time.Time
		createdAt, err := time.Parse("yyyy-MM-dd HH:mm:ss", meditationSession.CreatedAtString)
		if err != nil {
			return nil, err
		}
		meditationSession.CreatedAt = createdAt

		// append the struct to the array
		meditationSessions = append(meditationSessions, meditationSession)
	}

	// check for errors from iterating over rows
	if err := rows.Err(); err != nil {
		return nil, err
	}

	return meditationSessions, nil
}

type MeditationSession struct {
	ID              int       `json:"id"`
	Title           string    `json:"title"`
	Duration        int       `json:"duration"`
	CreatedAtString string    `json:"created_at"` // Use a string for scanning
	CreatedAt       time.Time `json:"-"`
}
