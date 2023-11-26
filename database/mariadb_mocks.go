package database

import (
	"database/sql"

	_ "github.com/go-sql-driver/mysql"
)

func SetMockDBConnection(db *MockDB) {
	databaseClient = &sql.DB{}
}

func ResetMockDBConnection() {
	databaseClient = nil
}

type MockDB struct{}

func (db *MockDB) GetAllEntriesFromTable(tableName string) (*MockRows, error) {
	return &MockRows{}, nil
}

type MockRows struct{}

func (rows *MockRows) Next() bool {
	// Implement your mock behavior here
	// ...

	// Return a mock result
	return false
}

func (rows *MockRows) Scan(dest ...interface{}) error {
	// Implement your mock behavior here
	// ...

	// Return a mock result
	return nil
}
