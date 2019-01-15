package models

import (
	"crypto/rand"
	"encoding/binary"
	"errors"
	"fmt"
	"io"
	"os"
	"time"

	"github.com/duo-labs/webauthn.io/config"
	log "github.com/duo-labs/webauthn.io/logger"

	_ "github.com/go-sql-driver/mysql" // Blank import needed to import mysql
	"github.com/jinzhu/gorm"
	_ "github.com/mattn/go-sqlite3" // Blank import needed to import sqlite3
)

var db *gorm.DB
var err error

// ErrUsernameTaken is thrown when a user attempts to register a username that is taken.
var ErrUsernameTaken = errors.New("username already taken")

// Copy of auth.GenerateSecureKey to prevent cyclic import with auth library
func generateSecureKey() string {
	k := make([]byte, 32)
	io.ReadFull(rand.Reader, k)
	return fmt.Sprintf("%x", k)
}

// BytesToID converts a byte slice to a uint. This is needed because the
// WebAuthn specification deals with byte buffers, while the primary keys in
// our database are uints.
func BytesToID(buf []byte) uint {
	// TODO: Probably want to catch the number of bytes converted in production
	id, _ := binary.Uvarint(buf)
	return uint(id)
}

// Setup initializes the Conn object
// It also populates the Config object
func Setup(config *config.Config) error {
	createDb := false
	if _, err = os.Stat(config.DBPath); err != nil || config.DBPath == ":memory:" {
		createDb = true
	}
	// Open our database connection
	db, err = gorm.Open(config.DBName, config.DBPath)
	if err != nil {
		return err
	}
	db.LogMode(false)
	db.SetLogger(log.Logger)
	db.DB().SetMaxOpenConns(1)
	if err != nil {
		return err
	}
	// Migrate up to the latest version
	//If the database didn't exist, we need to create the admin user
	err := db.AutoMigrate(
		&User{},
		&Credential{},
		&Authenticator{},
	).Error

	if err != nil {
		return err
	}

	gorm.NowFunc = func() time.Time {
		return time.Now().UTC()
	}

	if createDb {
		// Create the default user
		initUser := User{
			Username:    "admin",
			DisplayName: "Example Admin",
		}
		err = db.Save(&initUser).Error
		if err != nil {
			log.Infof("error creating initial user: %s", err)
			return err
		}
	}
	return nil
}
