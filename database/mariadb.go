package database

import (
	"database/sql"
	"fmt"
	"log"

	_ "github.com/go-sql-driver/mysql"
)

var databaseClient *sql.DB
var dbName string

func StartDatabase() error {
	// dsn := "username:password@tcp(127.0.0.1:3306)/meditation_db"
	dsn := "middleware:supersafepassword@tcp(127.0.0.1:3306)/meditation_db"

	// Open a connection to the database
	db, err := sql.Open("mysql", dsn)
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	// check if connection is established
	err = db.Ping()
	if err != nil {
		log.Fatal(err)
	}
	fmt.Println("Successfully connected to database!")

	// create table
	_, err = db.Exec(`
		CREATE TABLE IF NOT EXISTS meditation_sessions (
			id INT AUTO_INCREMENT PRIMARY KEY, 
			title VARCHAR(255) NOT NULL, 
			duration INT NOT NULL, 
			created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
		)
	`)

	return nil
}

func CloseMongoDB() {
	// disconnect from database mariadb (mysql)
	err := databaseClient.Close()
	if err != nil {
		panic(err)
	}
}
